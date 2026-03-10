"""sync.py – Core sync logic.

Run directly for a one-off sync:
    python sync.py
"""

import logging
from datetime import datetime
from typing import Callable

from accurate_client import AccurateClient
from db_manager import (
    get_last_sync_time,
    initialize_tables,
    update_sync_log,
    upsert_customer_categories,
    upsert_customers,
    upsert_sales_invoices,
    upsert_sales_returns,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    handlers=[
        logging.FileHandler("accurate_sync.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------
# Per-entity sync descriptor
# -----------------------------------------------------------------
ENTITIES: list[dict] = [
    {
        "name": "customer_categories",
        "fetch": lambda client, since: client.get_customer_categories(since),
        "upsert": upsert_customer_categories,
    },
    {
        "name": "customers",
        "fetch": lambda client, since: client.get_customers(since),
        "upsert": upsert_customers,
    },
    {
        "name": "sales_invoices",
        "fetch": lambda client, since: client.get_sales_invoices(since),
        "upsert": upsert_sales_invoices,
    },
    {
        "name": "sales_returns",
        "fetch": lambda client, since: client.get_sales_returns(since),
        "upsert": upsert_sales_returns,
    },
]


def _sync_entity(
    client: AccurateClient,
    name: str,
    fetch_fn: Callable,
    upsert_fn: Callable,
) -> int:
    """Fetch and upsert one entity.  Returns the number of records synced."""
    last_sync = get_last_sync_time(name)
    sync_started_at = datetime.now()

    if last_sync:
        logger.info("[%s] Incremental sync – records updated since %s", name, last_sync)
    else:
        logger.info("[%s] Full sync (no previous sync found)", name)

    records = fetch_fn(client, last_sync)
    logger.info("[%s] %d record(s) retrieved", name, len(records))

    if records:
        upsert_fn(records)
        update_sync_log(name, sync_started_at, len(records))

    return len(records)


def run_sync():
    """Run a full sync cycle for every entity."""
    logger.info("=" * 60)
    logger.info("Accurate sync started at %s", datetime.now().isoformat())

    initialize_tables()
    client = AccurateClient()

    results: dict[str, int] = {}
    errors: list[str] = []

    for entity in ENTITIES:
        try:
            count = _sync_entity(
                client,
                entity["name"],
                entity["fetch"],
                entity["upsert"],
            )
            results[entity["name"]] = count
        except Exception as exc:
            logger.error("[%s] Sync failed: %s", entity["name"], exc, exc_info=True)
            errors.append(entity["name"])

    logger.info("-" * 60)
    logger.info("Sync summary:")
    for name, count in results.items():
        logger.info("  %-30s %d record(s)", name, count)
    if errors:
        logger.warning("  Failed entities: %s", ", ".join(errors))
    logger.info("Accurate sync finished at %s", datetime.now().isoformat())
    logger.info("=" * 60)


if __name__ == "__main__":
    run_sync()
