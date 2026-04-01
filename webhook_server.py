"""webhook_server.py – Dummy HTTP endpoint to receive Accurate webhooks.

Accurate does not push deletion events through the sync API; it fires a
webhook instead.  This server accepts POST requests, dumps the raw payload
to a timestamped JSON file under PAYLOAD_DIR, and returns 200 OK.

Usage:
    python webhook_server.py

The server listens on HOST:PORT (default 0.0.0.0:5055).
Configure the same URL in Accurate's webhook settings.

Payload files:
    webhook_payloads/<event_type>_<timestamp>_<seq>.json

Each file contains the full request body as received plus two metadata
fields injected at the top level:
    _received_at  : ISO-8601 UTC timestamp
    _remote_addr  : caller IP address
"""

import json
import logging
import os
from datetime import datetime, timezone
from threading import Lock

from flask import Flask, request, jsonify

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────
HOST        = "0.0.0.0"
PORT        = 5055
PAYLOAD_DIR = "webhook_payloads"

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

# Counter keeps filenames unique when multiple webhooks arrive in the same second
_counter = 0
_counter_lock = Lock()


def _next_seq() -> int:
    global _counter
    with _counter_lock:
        _counter += 1
        return _counter


def _save_payload(event_type: str, payload: dict) -> str:
    """Write payload to disk. Returns the file path."""
    ts  = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    seq = _next_seq()
    slug = event_type.replace("/", "_").replace(" ", "_") or "unknown"
    filename = f"{slug}_{ts}_{seq:04d}.json"
    path = os.path.join(PAYLOAD_DIR, filename)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    return path


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

    # Inject metadata without mutating caller's keys
    payload["_received_at"] = received_at
    payload["_remote_addr"] = request.remote_addr

    # Use eventType field (Accurate convention) as filename prefix if present
    event_type = (
        payload.get("eventType")
        or payload.get("event_type")
        or payload.get("type")
        or "webhook"
    )

    path = _save_payload(event_type, payload)
    logger.info("Webhook received  event=%-30s  saved=%s", event_type, path)

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
