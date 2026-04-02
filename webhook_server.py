"""webhook_server.py – HTTP endpoint to receive Accurate webhooks.

Accurate fires a webhook for events (including deletions) that are not surfaced
through the incremental sync API.  This server:

  1. Accepts POST requests and saves the raw payload to a timestamped JSON file.
  2. Processes DELETE actions by inserting soft-delete tombstones into ClickHouse
     (is_deleted=1) for the affected records.

Usage:
    python webhook_server.py

The server listens on HOST:PORT (default 0.0.0.0:5055).
Configure the same URL in Accurate's webhook settings.

Payload structure (Accurate sends a JSON array):
    [
      {
        "databaseId": 123,
        "type": "CUSTOMER",          ← entity type
        "timestamp": "02/04/2026 ...",
        "uuid": "...",
        "data": [
          {"customerId": 456, "action": "DELETE"},
          ...
        ]
      },
      ...
    ]

Payload files:
    webhook_payloads/<type>_<timestamp>_<seq>.json
"""

import json
import logging
import os
from datetime import datetime, timezone
from threading import Lock

from flask import Flask, jsonify, request

from db_manager import soft_delete_records

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────
HOST        = "0.0.0.0"
PORT        = 5055
PAYLOAD_DIR = "webhook_payloads"

# Mapping of Accurate webhook type → (ClickHouse table, ID field name in data[])
# Types not listed here are logged as unhandled but still saved to disk.
TYPE_MAP: dict[str, tuple[str, str]] = {
    "CUSTOMER_CATEGORY": ("customer_categories", "customerCategoryId"),
    "CUSTOMER":          ("customers",           "customerId"),
    "SALES_ORDER":       ("sales_orders",        "salesOrderId"),
    "SALES_INVOICE":     ("sales_invoices",      "salesInvoiceId"),
    "SALES_RETURN":      ("sales_returns",        "salesReturnId"),
}

# ─────────────────────────────────────────────────────────────────────────────
# Setup
# ─────────────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
)
logger = logging.getLogger(__name__)

os.makedirs(PAYLOAD_DIR, exist_ok=True)

app = Flask(__name__)

_counter = 0
_counter_lock = Lock()


def _next_seq() -> int:
    global _counter
    with _counter_lock:
        _counter += 1
        return _counter


def _save_payload(event_type: str, payload: dict) -> str:
    """Write payload to disk. Returns the file path."""
    ts   = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    seq  = _next_seq()
    slug = event_type.replace("/", "_").replace(" ", "_") or "unknown"
    filename = f"{slug}_{ts}_{seq:04d}.json"
    path = os.path.join(PAYLOAD_DIR, filename)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    return path


def _process_event(event: dict):
    """Handle a single event object from the Accurate webhook payload."""
    event_type = (event.get("type") or "").upper()
    data_items = event.get("data") or []

    mapping = TYPE_MAP.get(event_type)
    if not mapping:
        logger.warning("Unhandled webhook type '%s' – saved to disk only", event_type)
        return

    table, id_field = mapping

    delete_ids = [
        int(item[id_field])
        for item in data_items
        if (item.get("action") or "").upper() == "DELETE" and item.get(id_field)
    ]

    if delete_ids:
        logger.info(
            "DELETE event: type=%s  table=%s  ids=%s",
            event_type, table, delete_ids,
        )
        soft_delete_records(table, delete_ids)
    else:
        non_delete = {(item.get("action") or "").upper() for item in data_items}
        logger.info(
            "Non-delete event: type=%s  actions=%s – no ClickHouse write",
            event_type, non_delete,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Endpoint
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/webhook", methods=["POST"])
def receive_webhook():
    received_at = datetime.now(timezone.utc).isoformat()

    # Accept JSON or fall back to raw text so nothing is silently dropped
    if request.is_json:
        payload = request.get_json(force=True, silent=True) or {}
    else:
        raw = request.get_data(as_text=True)
        payload = {"_raw": raw}

    # Accurate sends a JSON array at the top level – wrap for uniform storage
    if isinstance(payload, list):
        events = payload
        payload = {"_data": payload}
    else:
        events = payload.get("_data") or []

    payload["_received_at"] = received_at
    payload["_remote_addr"] = request.remote_addr

    # Use the type of the first event as the filename prefix (best effort)
    first_type = events[0].get("type") if events else None
    slug = first_type or payload.get("eventType") or payload.get("type") or "webhook"
    path = _save_payload(slug, payload)
    logger.info("Webhook received  type=%-25s  saved=%s", slug, path)

    # Process each event
    for event in events:
        try:
            _process_event(event)
        except Exception as exc:
            logger.error("Error processing event %s: %s", event, exc, exc_info=True)

    return jsonify({"status": "ok", "saved": path}), 200


@app.route("/webhook/list", methods=["GET"])
def list_payloads():
    """Return a summary list of stored payload files, newest first."""
    files = sorted(
        (f for f in os.listdir(PAYLOAD_DIR) if f.endswith(".json")),
        reverse=True,
    )
    return jsonify({"count": len(files), "files": files}), 200


@app.route("/webhook/latest", methods=["GET"])
def latest_payload():
    """Return the most recently stored payload."""
    files = sorted(
        (f for f in os.listdir(PAYLOAD_DIR) if f.endswith(".json")),
        reverse=True,
    )
    if not files:
        return jsonify({"error": "no payloads stored yet"}), 404
    path = os.path.join(PAYLOAD_DIR, files[0])
    with open(path, encoding="utf-8") as fh:
        return jsonify(json.load(fh)), 200


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logger.info("Webhook server starting on %s:%s  →  POST /webhook", HOST, PORT)
    logger.info("Payloads stored in: %s/", PAYLOAD_DIR)
    app.run(host=HOST, port=PORT)
