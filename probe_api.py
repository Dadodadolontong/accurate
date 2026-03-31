"""probe_api.py – Make a single Accurate API call and pretty-print the response.

Edit the CONFIG and CALL sections below, then run:
    python probe_api.py
"""

import base64
import hashlib
import hmac
import json
import os
import requests
from datetime import datetime, timezone
from config import ACCURATE_API_TOKEN, ACCURATE_SIGNATURE_SECRET, ACCURATE_HOST

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG  ← put your credentials here
# ─────────────────────────────────────────────────────────────────────────────
API_TOKEN  = ACCURATE_API_TOKEN
SIG_SECRET = ACCURATE_SIGNATURE_SECRET
HOST       = ACCURATE_HOST

# ─────────────────────────────────────────────────────────────────────────────
# CALL  ← change the path and params to probe any endpoint
# ─────────────────────────────────────────────────────────────────────────────
PATH   = "/accurate/api/customer/list.do"

PARAMS = {
    #"number": 'SI.0326.808',
    # Uncomment and edit to request specific fields:
    "fields": "id,customerNo,name,email,mobilePhone,billStreet,billCity,categoryId,category,categoryId,currencyId,currencyId,lastUpdate,createDate",
    #"fields": "id,customerNo,name,email,mobilePhone,billStreet,billCity,categoryId,category,categoryId,currencyId,currencyId,lastUpdate,createDate",
    # Uncomment to filter by last-update date:
    #"filter.customerNo.op" : "EQUAL",
    #"filter.customerNo.val": "CUST.05026",
    #"sp.page"    : 1,
    "sp.pageSize": 6000,
}

# Other endpoints you can try (just change PATH above):
#   /accurate/api/customer-category/list.do
#   /accurate/api/customer/list.do
#   /accurate/api/customer/detail.do          + PARAMS = {"id": 62351}
#   /accurate/api/sales-invoice/list.do
#   /accurate/api/sales-invoice/detail.do     + PARAMS = {"id": 116255}
#   /accurate/api/sales-return/list.do
#   /accurate/api/sales-return/detail.do      + PARAMS = {"id": 23701}

# ─────────────────────────────────────────────────────────────────────────────
# DUMP OPTIONS
# Set DUMP_PAGES = True to paginate through all pages and write each raw
# page response to a separate JSON file under DUMP_DIR.
# ─────────────────────────────────────────────────────────────────────────────
DUMP_PAGES = True
DUMP_DIR   = "debug_responses"

# ─────────────────────────────────────────────────────────────────────────────
# Engine – nothing to edit below this line
# ─────────────────────────────────────────────────────────────────────────────

def _build_headers() -> dict:
    ts  = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sig = base64.b64encode(
        hmac.new(SIG_SECRET.encode(), ts.encode(), hashlib.sha256).digest()
    ).decode()
    return {
        "Authorization":   f"Bearer {API_TOKEN}",
        "X-Api-Timestamp": ts,
        "X-Api-Signature": sig,
    }


def _type_summary(value) -> str:
    """Return a compact type label for any JSON value."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return f"bool  = {value}"
    if isinstance(value, int):
        return f"int   = {value}"
    if isinstance(value, float):
        return f"float = {value}"
    if isinstance(value, str):
        preview = repr(value[:60])
        return f"str   = {preview}" + (" …" if len(value) > 60 else "")
    if isinstance(value, list):
        return f"list[{len(value)}]"
    if isinstance(value, dict):
        return f"dict  keys={list(value.keys())}"
    return type(value).__name__


def _print_structure(obj, indent: int = 0, max_depth: int = 4):
    """Recursively print the structure of a JSON object."""
    pad = "  " * indent
    if isinstance(obj, dict):
        for key, val in obj.items():
            if isinstance(val, dict) and indent < max_depth:
                print(f"{pad}{key}:")
                _print_structure(val, indent + 1, max_depth)
            elif isinstance(val, list) and val and isinstance(val[0], dict) and indent < max_depth:
                print(f"{pad}{key}: list[{len(val)}]")
                print(f"{pad}  [0]:")
                _print_structure(val[0], indent + 2, max_depth)
            else:
                print(f"{pad}{key}: {_type_summary(val)}")
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            print(f"{pad}[{i}]:")
            _print_structure(item, indent + 1, max_depth)
    else:
        print(f"{pad}{_type_summary(obj)}")


def _dump_page(body: dict, page: int, run_ts: str, endpoint_slug: str):
    """Write a single page response to DUMP_DIR/<slug>_<ts>_page<N>.json."""
    os.makedirs(DUMP_DIR, exist_ok=True)
    filename = f"{endpoint_slug}_{run_ts}_page{page:04d}.json"
    path = os.path.join(DUMP_DIR, filename)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(body, fh, ensure_ascii=False, indent=2)
    print(f"  → dumped to {path}")


def _endpoint_slug() -> str:
    """Turn /accurate/api/customer/list.do → customer_list"""
    parts = [p for p in PATH.strip("/").split("/") if p not in ("accurate", "api")]
    return "_".join(parts).replace(".do", "")


def fetch_all_pages(run_ts: str) -> list[dict]:
    """Paginate through all pages, optionally dumping each one to disk.

    Returns the combined list of records from all pages.
    """
    page_size = PARAMS.get("sp.pageSize", 100)
    slug = _endpoint_slug()
    all_records: list[dict] = []
    page = 1

    while True:
        params = dict(PARAMS)
        params["sp.page"] = page

        url = HOST + PATH
        resp = requests.get(url, headers=_build_headers(), params=params, timeout=30)
        resp.raise_for_status()
        body = resp.json()

        sp         = body.get("sp") or {}
        page_count = sp.get("pageCount", 0)
        row_count  = sp.get("rowCount", "?")
        records    = body.get("d") or []

        print(
            f"  page {page:>4} → {len(records):>5} record(s)"
            f"  (running total: {len(all_records) + len(records)} / {row_count},"
            f"  pageCount: {page_count or 'unknown'})"
        )

        if DUMP_PAGES:
            _dump_page(body, page, run_ts, slug)

        if not body.get("s"):
            print(f"  API error: {body.get('d')}")
            break

        all_records.extend(records)

        if page_count > 0:
            if page >= page_count:
                break
        else:
            if len(records) < page_size:
                break

        page += 1

    return all_records


def main():
    run_ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    url = HOST + PATH
    print(f"GET {url}")
    print(f"Params: {json.dumps(PARAMS, indent=2)}")
    if DUMP_PAGES:
        print(f"Page dumps enabled → {DUMP_DIR}/")
    print("-" * 60)

    if DUMP_PAGES or PARAMS.get("sp.pageSize"):
        # Paginated mode: walk all pages
        all_records = fetch_all_pages(run_ts)
        print("-" * 60)
        print(f"Total records across all pages: {len(all_records)}")
        if all_records:
            print("\n" + "=" * 60)
            print("STRUCTURE TREE (first record)")
            print("=" * 60)
            _print_structure(all_records[0])
        return

    # Single-request mode (no pagination)
    resp = requests.get(url, headers=_build_headers(), params=PARAMS, timeout=30)
    print(f"HTTP {resp.status_code}")
    print("-" * 60)

    body = resp.json()

    # ── Top-level summary ────────────────────────────────────────────────────
    print("Top-level keys:", list(body.keys()))
    print(f"  s (success) : {body.get('s')}")
    print(f"  sp          : {body.get('sp')}")

    data = body.get("d")
    if isinstance(data, list):
        print(f"  d           : list[{len(data)}]")
    elif isinstance(data, dict):
        print(f"  d           : dict  keys={list(data.keys())}")
    else:
        print(f"  d           : {_type_summary(data)}")

    # ── Full raw JSON ────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("FULL RAW JSON")
    print("=" * 60)
    print(json.dumps(body, indent=2, ensure_ascii=False))

    # ── Structure tree (types only, no values for nested objects) ───────────
    print("\n" + "=" * 60)
    print("STRUCTURE TREE")
    print("=" * 60)
    _print_structure(body)


if __name__ == "__main__":
    main()
