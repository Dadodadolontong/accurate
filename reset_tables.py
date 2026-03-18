"""reset_tables.py – Drop entity tables and reset sync time to 2026-01-01.

Run this after editing a _FIELDS_* constant in accurate_client.py so that
the tables are recreated with the current schema and data is re-fetched from
the beginning of the year.

Usage
-----
# Reset all entities:
    python reset_tables.py --all

# Reset specific entities:
    python reset_tables.py --entity customers
    python reset_tables.py --entity sales_invoices --entity sales_returns

# List available entity names:
    python reset_tables.py --list
"""

import argparse
import logging
import sys

from db_manager import initialize_tables, reset_sync_time, reset_table

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Maps each logical entity name to:
#   "tables"  – the ClickHouse table(s) to drop and recreate (order matters)
#   "sync_key" – the key used in sync_log
ENTITIES: dict[str, dict] = {
    "customer_categories": {
        "tables": ["customer_categories"],
        "sync_key": "customer_categories",
    },
    "customers": {
        "tables": ["customers"],
        "sync_key": "customers",
    },
    "sales_invoices": {
        "tables": ["sales_invoice_items", "sales_invoices"],
        "sync_key": "sales_invoices",
    },
    "sales_returns": {
        "tables": ["sales_return_expenses", "sales_return_items", "sales_returns"],
        "sync_key": "sales_returns",
    },
}


def reset_entity(name: str):
    cfg = ENTITIES[name]
    logger.info("=== Resetting entity: %s ===", name)

    for table in cfg["tables"]:
        reset_table(table)

    reset_sync_time(cfg["sync_key"])
    logger.info("Done. Next sync will re-fetch '%s' from 2026-01-01.", name)


def main():
    parser = argparse.ArgumentParser(
        description="Drop entity tables and reset sync time to 2026-01-01."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--all",
        action="store_true",
        help="Reset all entities.",
    )
    group.add_argument(
        "--entity",
        metavar="NAME",
        action="append",
        dest="entities",
        choices=list(ENTITIES),
        help="Entity to reset (repeatable). Choices: " + ", ".join(ENTITIES),
    )
    group.add_argument(
        "--list",
        action="store_true",
        help="List available entity names and exit.",
    )
    args = parser.parse_args()

    if args.list:
        print("Available entities:")
        for name, cfg in ENTITIES.items():
            tables = ", ".join(cfg["tables"])
            print(f"  {name:25s}  tables: {tables}")
        sys.exit(0)

    targets = list(ENTITIES) if args.all else args.entities

    # Recreate the database/schema after drops
    initialize_tables()

    for name in targets:
        reset_entity(name)

    logger.info("All done. Run sync.py to repopulate.")


if __name__ == "__main__":
    main()
