"""reconcile.py – Periodic full-ID reconciliation to detect deleted records.

Accurate does not surface deletions through the incremental sync API (lastUpdate
filter).  This module fetches the complete set of IDs from Accurate for each
entity, compares them against ClickHouse, and soft-deletes any IDs that no
longer exist in Accurate.

Soft-delete mechanics
---------------------
A "soft-delete" is a tombstone INSERT: a minimal row with is_deleted=1 and a
fresh updated_at.  Because tables use ReplacingMergeTree(updated_at), the
tombstone wins over the original row on the next FINAL query or background merge.
Downstream queries must filter ``WHERE is_deleted = 0`` (or join parent tables
with that condition for child-table queries).

Usage
-----
    python reconcile.py              # run once immediately
    python reconcile.py --dry-run    # print orphans without writing
"""

import argparse
import logging
import logging.handlers

from accurate_client import AccurateClient
from config import LOGGER_FILE
from db_manager import get_live_ids, initialize_tables, soft_delete_records

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    handlers=[
        logging.handlers.RotatingFileHandler(
            filename=LOGGER_FILE,
            maxBytes=10 * 1024 * 1024,
            backupCount=7,
            encoding="utf-8",
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Per-entity reconciliation config
# ---------------------------------------------------------------------------
# api_path    : list endpoint that returns all IDs (no lastUpdate filter)
# ch_table    : ClickHouse parent table to reconcile
# extra_params: any extra API filters needed to match the sync scope exactly
#               (e.g. invoiceDp=False keeps reconcile consistent with sync)
# ---------------------------------------------------------------------------
RECONCILE_ENTITIES: list[dict] = [
    {
        "name":     "customer_categories",
        "api_path": "/api/customer-category/list.do",
        "ch_table": "customer_categories",
    },
    {
        "name":     "customers",
        "api_path": "/api/customer/list.do",
        "ch_table": "customers",
    },
    {
        "name":     "sales_orders",
        "api_path": "/api/sales-order/list.do",
        "ch_table": "sales_orders",
    },
    {
        "name":        "sales_invoices",
        "api_path":    "/api/sales-invoice/list.do",
        "ch_table":    "sales_invoices",
        "extra_params": {"filter.invoiceDp": "False"},
    },
    {
        "name":     "sales_returns",
        "api_path": "/api/sales-return/list.do",
        "ch_table": "sales_returns",
    },
]


def _reconcile_entity(
    client: AccurateClient,
    name: str,
    api_path: str,
    ch_table: str,
    extra_params: dict | None,
    dry_run: bool,
) -> int:
    """Reconcile one entity.  Returns the number of orphaned IDs found."""
    logger.info("[%s] Fetching all IDs from Accurate …", name)
    accurate_ids = client.get_all_ids(api_path, extra_params)
    logger.info("[%s] %d IDs in Accurate", name, len(accurate_ids))

    logger.info("[%s] Fetching live IDs from ClickHouse …", name)
    ch_ids = get_live_ids(ch_table)
    logger.info("[%s] %d live IDs in ClickHouse", name, len(ch_ids))

    orphans = sorted(ch_ids - accurate_ids)
    logger.info("[%s] %d orphan(s) to soft-delete", name, len(orphans))

    if orphans:
        if dry_run:
            logger.info("[%s] DRY RUN – would soft-delete IDs: %s", name, orphans)
        else:
            soft_delete_records(ch_table, orphans)

    return len(orphans)


def run_reconcile(dry_run: bool = False):
    """Run a full reconciliation cycle for every entity."""
    logger.info("=" * 60)
    logger.info("Reconciliation started  (dry_run=%s)", dry_run)

    initialize_tables()
    client = AccurateClient()

    total_orphans = 0
    errors: list[str] = []

    for entity in RECONCILE_ENTITIES:
        try:
            count = _reconcile_entity(
                client,
                entity["name"],
                entity["api_path"],
                entity["ch_table"],
                entity.get("extra_params"),
                dry_run,
            )
            total_orphans += count
        except Exception as exc:
            logger.error("[%s] Reconciliation failed: %s", entity["name"], exc, exc_info=True)
            errors.append(entity["name"])

    logger.info("-" * 60)
    logger.info("Reconciliation summary: %d total orphan(s) soft-deleted", total_orphans)
    if errors:
        logger.warning("  Failed entities: %s", ", ".join(errors))
    logger.info("Reconciliation finished")
    logger.info("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reconcile deleted Accurate records in ClickHouse")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print orphaned IDs without writing soft-deletes",
    )
    args = parser.parse_args()
    run_reconcile(dry_run=args.dry_run)
