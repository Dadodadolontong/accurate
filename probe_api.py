"""probe_api.py – Make a single Accurate API call and pretty-print the response.

Edit the CONFIG and CALL sections below, then run:
    python probe_api.py
"""

import base64
import hashlib
import hmac
import json
import requests
from datetime import datetime, timezone

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG  ← put your credentials here
# ─────────────────────────────────────────────────────────────────────────────
API_TOKEN  = "aat.NTA.eyJ2IjoxLCJ1IjoyODE4NDEsImQiOjQ2ODYzNSwiYWkiOjY0NjUwLCJhayI6ImQ5MzkzNWI1LTZlZTItNDIyNi05NjhlLWZiNTUxNmFlNGQ5MCIsImFuIjoiQkFOIiwiYXAiOiIyNzZmMDBhMy02MzE3LTRmZjMtYjA0Ny04ZjdhMGE4MTY3ZjEiLCJ0IjoxNzcxMjEwNTMwNTQ2fQ.wzLfi9Fjk6sT8y/ux1FUQ++VV7IPxWT/6kJddQgCsCxfT0LxrBg0zKiFrqtFDWQp0JIkJB/sXCmZMiVM1HtZ/P5eJ0c1LcBHdec7qdzdvfkrM7PtrKftKXhuS0Saw5orxUTH31EuyKOa86v6Th/A7/W4v6PfnJ+GYVcykZT6FSD4VuJZ5o2gs3uouL9P+dJGe4K5koCq87Q=.Is58bWtFYS4vGazsBXBvnnmQI7LiDU2f8hwGZmqyFcs"
SIG_SECRET = "hENDHfaS3TtuCQ0fZrX1R2irpp02XhBkD6zMl8B60YrXDnCCEdpBgfoHqMIqXA1J"
HOST       = "https://zeus.accurate.id"

# ─────────────────────────────────────────────────────────────────────────────
# CALL  ← change the path and params to probe any endpoint
# ─────────────────────────────────────────────────────────────────────────────
PATH   = "/accurate/api/sales-order/detail.do"

PARAMS = {
    "number": "SO.0325-001"
    # Uncomment and edit to request specific fields:
    # "fields": "id,customerNo,name,email,mobilePhone,billStreet,billCity,categoryId,category,categoryId,currencyId,currencyId,lastUpdate,createDate",
    #
    # Uncomment to filter by last-update date:
    # "filter.lastUpdate.op" : "GREATER_EQUAL_THAN",
    # "filter.lastUpdate.val": "01/01/2026 00:00:00",
    #"sp.page"    : 1,
    #"sp.pageSize": 5,
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


def main():
    url = HOST + PATH
    print(f"GET {url}")
    print(f"Params: {json.dumps(PARAMS, indent=2)}")
    print("-" * 60)

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
