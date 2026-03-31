"""db_manager.py – ClickHouse persistence layer.

All tables use ReplacingMergeTree(updated_at) so that repeated INSERTs are
idempotent.  Deduplication happens on background merge; use
``SELECT … FINAL`` when you need immediate consistency (e.g. sync_log reads).

Entity table schemas are auto-generated from schema_defs.*_COLUMNS definitions.
To add, remove, or rename a field, edit schema_defs.py only.
"""

import logging
from datetime import date, datetime, timedelta

import clickhouse_connect
from clickhouse_connect.driver.client import Client

from config import CH_DATABASE, CH_HOST, CH_PASSWORD, CH_PORT, CH_SECURE, CH_USER
from schema_defs import (
    CUSTOMER_CATEGORY_COLUMNS,
    CUSTOMER_COLUMNS,
    SALES_INVOICE_COLUMNS,
    SALES_ORDER_COLUMNS,
    SALES_RETURN_COLUMNS,
    col_names,
    make_ddl,
)

logger = logging.getLogger(__name__)


def _get_client() -> Client:
    return clickhouse_connect.get_client(
        host=CH_HOST,
        port=CH_PORT,
        username=CH_USER,
        password=CH_PASSWORD,
        database=CH_DATABASE,
        secure=CH_SECURE,
    )


# ---------------------------------------------------------------------------
# Schema  (CREATE TABLE IF NOT EXISTS – safe to run on every startup)
# ---------------------------------------------------------------------------

_DDL = [
    f"CREATE DATABASE IF NOT EXISTS {CH_DATABASE}",

    # ------------------------------------------------------------------
    # sync_log – tracks the last successful sync time per entity
    # ------------------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS sync_log (
        entity          String,
        last_sync_time  DateTime,
        records_synced  Int32    DEFAULT 0,
        updated_at      DateTime DEFAULT now()
    ) ENGINE = ReplacingMergeTree(updated_at)
    ORDER BY entity
    """,

    # Entity tables – DDL auto-generated from schema_defs.*_COLUMNS.
    # To add/remove/rename a column, edit schema_defs.py only.
    make_ddl("customer_categories", CUSTOMER_CATEGORY_COLUMNS),
    make_ddl("customers",           CUSTOMER_COLUMNS),
    make_ddl("sales_orders",        SALES_ORDER_COLUMNS),

    # ------------------------------------------------------------------
    # sales_order_items
    # API detailItem fields: id, seq, itemId, item{no,name}, itemUnit{name},
    #   quantity, unitPrice, totalPrice, tax1Rate, tax1Amount
    # ------------------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS sales_order_items (
        id               Int64,
        sales_order_id   Int64,
        seq              Int32,
        item_id          Nullable(Int64),
        item_no          String,
        item_name        String,
        item_unit        String,
        quantity         Nullable(Float64),
        unit_price       Nullable(Float64),
        total_price      Nullable(Float64),
        tax1_rate        Nullable(Float64),
        tax1_amount      Nullable(Float64),
        updated_at       DateTime DEFAULT now()
    ) ENGINE = ReplacingMergeTree(updated_at)
    ORDER BY (sales_order_id, id)
    """,

    # ------------------------------------------------------------------
    # sales_order_expenses  (expense line items from detailExpense)
    # API detailExpense fields: id, seq, accountId, account{name},
    #   description, amount, tax1Rate, tax1Amount
    # ------------------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS sales_order_expenses (
        id               Int64,
        sales_order_id   Int64,
        seq              Int32,
        account_id       Nullable(Int64),
        account_name     String,
        description      String,
        amount           Nullable(Float64),
        tax1_rate        Nullable(Float64),
        tax1_amount      Nullable(Float64),
        updated_at       DateTime DEFAULT now()
    ) ENGINE = ReplacingMergeTree(updated_at)
    ORDER BY (sales_order_id, id)
    """,

    make_ddl("sales_invoices",      SALES_INVOICE_COLUMNS),

    # ------------------------------------------------------------------
    # sales_invoice_items
    # API detailItem fields: id, seq, itemId, item{no,name}, itemUnit{name},
    #   quantity, unitPrice, totalPrice, tax1Rate, tax1Amount
    # ------------------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS sales_invoice_items (
        id               Int64,
        sales_invoice_id Int64,
        seq              Int32,
        item_id          Nullable(Int64),
        item_no          String,
        item_name        String,
        item_unit        String,
        quantity         Nullable(Float64),
        unit_price       Nullable(Float64),
        total_price      Nullable(Float64),
        tax1_rate        Nullable(Float64),
        tax1_amount      Nullable(Float64),
        updated_at       DateTime DEFAULT now()
    ) ENGINE = ReplacingMergeTree(updated_at)
    ORDER BY (sales_invoice_id, id)
    """,

    make_ddl("sales_returns", SALES_RETURN_COLUMNS),

    # ------------------------------------------------------------------
    # period – date dimension table with Indonesian holiday data
    # ------------------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS period (
        full_date             Date,
        year                  Int16,
        semester              Int8,
        quarter               Int8,
        month                 Int8,
        day                   Int8,
        day_of_week           Int8,
        is_weekend            UInt8,
        is_holiday            UInt8,
        holiday_name          String,
        working_day_of_month  Int16,
        updated_at            DateTime DEFAULT now()
    ) ENGINE = ReplacingMergeTree(updated_at)
    ORDER BY full_date
    """,

    # ------------------------------------------------------------------
    # sales_return_items  (same shape as sales_invoice_items)
    # ------------------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS sales_return_items (
        id               Int64,
        sales_return_id  Int64,
        seq              Int32,
        item_id          Nullable(Int64),
        item_no          String,
        item_name        String,
        item_unit        String,
        quantity         Nullable(Float64),
        unit_price       Nullable(Float64),
        total_price      Nullable(Float64),
        tax1_rate        Nullable(Float64),
        tax1_amount      Nullable(Float64),
        updated_at       DateTime DEFAULT now()
    ) ENGINE = ReplacingMergeTree(updated_at)
    ORDER BY (sales_return_id, id)
    """,

    # ------------------------------------------------------------------
    # sales_return_expenses  (expense line items from detailExpense)
    # API detailExpense fields: id, seq, accountId, account{name},
    #   description, amount, tax1Rate, tax1Amount
    # ------------------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS sales_return_expenses (
        id               Int64,
        sales_return_id  Int64,
        seq              Int32,
        account_id       Nullable(Int64),
        account_name     String,
        description      String,
        amount           Nullable(Float64),
        tax1_rate        Nullable(Float64),
        tax1_amount      Nullable(Float64),
        updated_at       DateTime DEFAULT now()
    ) ENGINE = ReplacingMergeTree(updated_at)
    ORDER BY (sales_return_id, id)
    """,
]


def initialize_tables():
    """Create the database and all tables if they do not already exist."""
    client = _get_client()
    try:
        for stmt in _DDL:
            client.command(stmt.strip())
        logger.info("ClickHouse tables initialised successfully")
    except Exception as exc:
        logger.error("Error initialising ClickHouse tables: %s", exc)
        raise


def reset_table(table_name: str):
    """Drop and recreate a single table using the current schema.

    Call this ONCE after a schema change (e.g. columns added/removed).
    All data in the table will be lost and re-synced on the next run.

    Usage:
        from db_manager import reset_table
        reset_table("customer_categories")
    """
    client = _get_client()
    client.command(f"DROP TABLE IF EXISTS {table_name}")
    logger.info("Dropped table %s", table_name)
    # Re-run only the DDL statement that matches this table
    for stmt in _DDL:
        if f"CREATE TABLE IF NOT EXISTS {table_name}" in stmt:
            client.command(stmt.strip())
            logger.info("Recreated table %s with current schema", table_name)
            return
    logger.warning("No DDL found for table %s", table_name)


# Data tables (excludes sync_log so previous sync timestamps are preserved)
_DATA_TABLES = [
    "customer_categories",
    "customers",
    "sales_orders",
    "sales_order_items",
    "sales_order_expenses",
    "sales_invoices",
    "sales_invoice_items",
    "sales_returns",
    "sales_return_items",
    "sales_return_expenses",
    "period",
]


def reset_all_tables():
    """Drop and recreate ALL data tables with the current schema.

    Use this once after a schema change.  sync_log is left untouched so
    the next run performs an incremental sync from the last recorded time.
    Call initialize_tables() afterward if you also want sync_log recreated.

    Usage:
        python -c "from db_manager import reset_all_tables; reset_all_tables()"
    """
    for table in _DATA_TABLES:
        reset_table(table)
    logger.info("All data tables reset.  Run the sync to repopulate.")


# ---------------------------------------------------------------------------
# Period table
# ---------------------------------------------------------------------------

def populate_period_table(start_year: int = 2024, end_year: int | None = None):
    """Populate the period table with one row per calendar day.

    Covers *start_year* through *end_year* (inclusive).  Defaults to the
    current year + 2 so the table always has a useful planning horizon.

    Indonesian public holidays are fetched via the ``holidays`` library.
    ``working_day_of_month`` is a 1-based counter that increments only on
    weekdays (Mon–Fri) that are not public holidays; it is 0 for weekends
    and public holidays.

    The table is truncated before re-insertion so this function is safe to
    call repeatedly.
    """
    try:
        import holidays as holidays_lib  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "The 'holidays' package is required.  Run: pip install holidays>=0.46"
        ) from exc

    if end_year is None:
        end_year = datetime.now().year + 2

    # Build a combined holiday dict for all target years
    id_holidays: dict[date, str] = {}
    for yr in range(start_year, end_year + 1):
        id_holidays.update(holidays_lib.Indonesia(years=yr))

    rows: list[list] = []
    now = datetime.now()

    current = date(start_year, 1, 1)
    last = date(end_year, 12, 31)

    # Track working-day counter per (year, month)
    working_day_counters: dict[tuple[int, int], int] = {}

    while current <= last:
        yr = current.year
        mo = current.month
        dy = current.day
        semester = 1 if mo <= 6 else 2
        quarter = (mo - 1) // 3 + 1
        dow = current.isoweekday()  # 1=Mon … 7=Sun
        is_weekend = 1 if dow >= 6 else 0
        is_holiday = 1 if current in id_holidays else 0
        holiday_name = id_holidays.get(current, "")

        is_working = 1 if (is_weekend == 0 and is_holiday == 0) else 0
        key = (yr, mo)
        if is_working:
            working_day_counters[key] = working_day_counters.get(key, 0) + 1
            wdm = working_day_counters[key]
        else:
            wdm = 0

        rows.append([
            current,
            yr,
            semester,
            quarter,
            mo,
            dy,
            dow,
            is_weekend,
            is_holiday,
            holiday_name,
            wdm,
            now,
        ])
        current += timedelta(days=1)

    client = _get_client()
    client.command("TRUNCATE TABLE IF EXISTS period")
    client.insert(
        "period",
        rows,
        column_names=[
            "full_date", "year", "semester", "quarter", "month", "day",
            "day_of_week", "is_weekend", "is_holiday", "holiday_name",
            "working_day_of_month", "updated_at",
        ],
    )
    logger.info(
        "Period table populated: %d rows (%d–%d)", len(rows), start_year, end_year
    )


# ---------------------------------------------------------------------------
# Sync-log helpers
# ---------------------------------------------------------------------------

def get_last_sync_time(entity: str) -> datetime | None:
    """Return the last successful sync time for *entity*, or a safe default."""
    client = _get_client()
    result = client.query(
        "SELECT last_sync_time FROM sync_log FINAL "
        "WHERE entity = {entity:String} LIMIT 1",
        parameters={"entity": entity},
    )
    if result.result_rows:
        return result.result_rows[0][0]
    return datetime(2026, 1, 1, 0, 0, 0)


def update_sync_log(entity: str, sync_time: datetime, records_synced: int):
    now = datetime.now()
    client = _get_client()
    client.insert(
        "sync_log",
        [[entity, sync_time, records_synced, now]],
        column_names=["entity", "last_sync_time", "records_synced", "updated_at"],
    )


def reset_sync_time(entity: str):
    """Reset the sync time for *entity* to 2026-01-01 so the next run re-syncs from that date.

    Call this after changing a _FIELDS_* constant so all records are re-fetched
    with the new field set.
    """
    update_sync_log(entity, datetime(2026, 1, 1, 0, 0, 0), 0)
    logger.info("Reset sync time for '%s' to 2026-01-01", entity)


# ---------------------------------------------------------------------------
# Upsert helpers
# ---------------------------------------------------------------------------

def upsert_customer_categories(records: list[dict]):
    if not records:
        return
    now = datetime.now()
    client = _get_client()
    client.insert(
        "customer_categories",
        [
            [
                r["id"],
                _s(r.get("name")),
                _s(r.get("nameWithIndentStrip")),
                int(r.get("lvl") or 0),
                bool(r.get("defaultCategory")),
                bool(r.get("sub")),
                _nested(r, "parent", "id"),
                _s(_nested(r, "parent", "name") or _nested(r, "parent", "nameWithIndentStrip")),
                now,
            ]
            for r in records
        ],
        column_names=col_names(CUSTOMER_CATEGORY_COLUMNS),
    )
    logger.info("Upserted %d customer_categories", len(records))


def upsert_customers(records: list[dict]):
    if not records:
        return
    now = datetime.now()
    client = _get_client()
    client.insert(
        "customers",
        [
            [
                r["id"],
                _s(r.get("customerNo")),
                _s(r.get("name")),
                _s(r.get("email")),
                _s(r.get("mobilePhone")),
                _s(r.get("workPhone")),
                _s(r.get("fax")),
                _s(r.get("billStreet")),
                _s(r.get("billCity")),
                _s(r.get("billProvince")),
                _s(r.get("billZipCode")),
                _s(r.get("billCountry")),
                _id(r.get("categoryId")) or _id(_nested(r, "category", "id")),
                _s(_nested(r, "category", "name") or _nested(r, "category", "nameWithIndentStrip")),
                _s(_nested(r, "currency", "code")),
                _id(r.get("defaultTermId")),
                _s(_nested(r, "term", "name")),
                _s(r.get("notes")),
                _s(r.get("npwpNo")),
                bool(r.get("suspended")),
                _s(r.get("customerTaxType")),
                _s(r.get("documentCode")),
                _parse_timestamp(r.get("lastUpdate")),
                _parse_timestamp(r.get("createDate")),
                now,
            ]
            for r in records
        ],
        column_names=col_names(CUSTOMER_COLUMNS),
    )
    logger.info("Upserted %d customers", len(records))


def _extract_si_from_history(record: dict) -> tuple:
    """Scan processHistory for the first entry with historyType == 'SI'.

    Returns (id, historyNumber) or (None, "") when no SI entry is found.
    Field names are checked in both camelCase and PascalCase to be resilient
    to API casing variations.
    """
    for h in (record.get("processHistory") or []):
        htype = h.get("historyType") or h.get("HistoryType") or ""
        if htype.upper() == "SI":
            inv_id   = _id(h.get("id") or h.get("ID"))
            inv_name = _s(h.get("historyNumber") or h.get("HistoryNumber"))
            return inv_id, inv_name
    return None, ""


def upsert_sales_orders(records: list[dict]):
    if not records:
        return
    now = datetime.now()
    client = _get_client()
    client.insert(
        "sales_orders",
        [
            [
                r["id"],
                _s(r.get("number")),
                _parse_date(r.get("transDate")),
                _parse_date(r.get("shipDate")),
                _id(r.get("customerId")) or _id(_nested(r, "customer", "id")),
                _s(_nested(r, "customer", "name") or _nested(r, "customer", "wpName")),
                _s(_nested(r, "customer", "customerNo")),
                r.get("totalAmount"),
                r.get("subTotal"),
                r.get("salesAmount"),
                r.get("tax1Amount"),
                r.get("tax1Rate"),
                _s(r.get("status")),
                _s(r.get("approvalStatus")),
                _s(r.get("description")),
                _s(r.get("poNumber")),
                _id(r.get("masterSalesmanId")),
                _s(r.get("masterSalesmanName")),
                _id(r.get("branchId")),
                _s(r.get("branchName")),
                _id(r.get("currencyId")),
                r.get("rate"),
                _parse_timestamp(r.get("lastUpdate")),
                *_extract_si_from_history(r),   # sales_invoice_id, sales_invoice_name
                now,
            ]
            for r in records
        ],
        column_names=col_names(SALES_ORDER_COLUMNS),
    )
    logger.info("Upserted %d sales_orders", len(records))

    # Line items
    all_items = [(r["id"], item) for r in records for item in (r.get("detailItem") or [])]
    if all_items:
        _insert_sales_order_items(client, now, all_items)

    # Expense line items
    all_expenses = [(r["id"], exp) for r in records for exp in (r.get("detailExpense") or [])]
    if all_expenses:
        _insert_sales_order_expenses(client, now, all_expenses)


def _insert_sales_order_items(client: Client, now: datetime, pairs: list[tuple]):
    client.insert(
        "sales_order_items",
        [
            [
                _id(item.get("id")),
                order_id,
                int(item.get("seq") or 0),
                _id(item.get("itemId")),
                _s(_nested(item, "item", "no")),
                _s(item.get("detailName") or _nested(item, "item", "name")),
                _s(_nested(item, "itemUnit", "name")),
                item.get("quantity"),
                item.get("unitPrice"),
                item.get("totalPrice"),
                item.get("tax1Rate"),
                item.get("tax1Amount"),
                now,
            ]
            for order_id, item in pairs
        ],
        column_names=[
            "id", "sales_order_id", "seq",
            "item_id", "item_no", "item_name", "item_unit",
            "quantity", "unit_price", "total_price",
            "tax1_rate", "tax1_amount", "updated_at",
        ],
    )
    logger.info("Upserted %d sales_order_items", len(pairs))


def _insert_sales_order_expenses(client: Client, now: datetime, pairs: list[tuple]):
    client.insert(
        "sales_order_expenses",
        [
            [
                _id(exp.get("id")),
                order_id,
                int(exp.get("seq") or 0),
                _id(exp.get("accountId")) or _id(_nested(exp, "account", "id")),
                _s(_nested(exp, "account", "name")),
                _s(exp.get("description")),
                exp.get("amount"),
                exp.get("tax1Rate"),
                exp.get("tax1Amount"),
                now,
            ]
            for order_id, exp in pairs
        ],
        column_names=[
            "id", "sales_order_id", "seq",
            "account_id", "account_name", "description",
            "amount", "tax1_rate", "tax1_amount", "updated_at",
        ],
    )
    logger.info("Upserted %d sales_order_expenses", len(pairs))


def upsert_sales_invoices(records: list[dict]):
    if not records:
        return
    now = datetime.now()
    client = _get_client()
    client.insert(
        "sales_invoices",
        [
            [
                r["id"],
                _s(r.get("number")),
                _parse_date(r.get("transDate")),
                _parse_date(r.get("dueDate")),
                _parse_date(r.get("taxDate")),
                _parse_date(r.get("shipDate")),
                _id(r.get("customerId"), "customerId", _s(r.get("number")))
                or _id(_nested(r, "customer", "id")),
                _s(_nested(r, "customer", "name") or _nested(r, "customer", "wpName")),
                _s(_nested(r, "customer", "customerNo")),
                r.get("totalAmount"),
                r.get("subTotal"),
                r.get("salesAmount"),
                r.get("tax1Amount"),
                r.get("tax1Rate"),
                bool(r.get("outstanding")),
                _s(r.get("status")),
                _s(r.get("approvalStatus")),
                _s(r.get("description")),
                _id(r.get("masterSalesmanId")),
                _s(r.get("masterSalesmanName")),
                _id(r.get("branchId")),
                _s(r.get("branchName")),
                _id(r.get("currencyId")),
                r.get("rate"),
                now,
            ]
            for r in records
        ],
        column_names=col_names(SALES_INVOICE_COLUMNS),
    )
    logger.info("Upserted %d sales_invoices", len(records))

    # Line items
    all_items = [(r["id"], item) for r in records for item in (r.get("detailItem") or [])]
    if all_items:
        logger.info("Upserting %d sales_invoice_items", len(all_items)) 
        _insert_sales_invoice_items(client, now, all_items)


def _insert_sales_invoice_items(client: Client, now: datetime, pairs: list[tuple]):
    client.insert(
        "sales_invoice_items",
        [
            [
                _id(item.get("id")),
                invoice_id,
                int(item.get("seq") or 0),
                _id(item.get("itemId")),
                _s(_nested(item, "item", "no")),
                _s(item.get("detailName") or _nested(item, "item", "name")),
                _s(_nested(item, "itemUnit", "name")),
                item.get("quantity"),
                item.get("unitPrice"),
                item.get("totalPrice"),
                item.get("tax1Rate"),
                item.get("tax1Amount"),
                now,
            ]
            for invoice_id, item in pairs
        ],
        column_names=[
            "id", "sales_invoice_id", "seq",
            "item_id", "item_no", "item_name", "item_unit",
            "quantity", "unit_price", "total_price",
            "tax1_rate", "tax1_amount", "updated_at",
        ],
    )
    logger.info("Upserted %d sales_invoice_items", len(pairs))


def upsert_sales_returns(records: list[dict]):
    if not records:
        return
    now = datetime.now()
    client = _get_client()
    client.insert(
        "sales_returns",
        [
            [
                r["id"],
                _s(r.get("number")),
                _parse_date(r.get("transDate")),
                _parse_date(r.get("taxDate")),
                _id(r.get("customerId")) or _id(_nested(r, "customer", "id")),
                _s(_nested(r, "customer", "name") or _nested(r, "customer", "wpName")),
                _s(_nested(r, "customer", "customerNo")),
                _id(r.get("invoiceId")),
                r.get("totalAmount"),
                r.get("subTotal"),
                r.get("returnAmount"),
                r.get("tax1Amount"),
                r.get("tax1Rate"),
                _s(r.get("returnType")),
                _s(r.get("returnStatusType")),
                _s(r.get("approvalStatus")),
                _s(r.get("description")),
                _id(r.get("branchId")),
                _id(r.get("currencyId")),
                r.get("rate"),
                now,
            ]
            for r in records
        ],
        column_names=col_names(SALES_RETURN_COLUMNS),
    )
    logger.info("Upserted %d sales_returns", len(records))

    # Line items
    all_items = [(r["id"], item) for r in records for item in (r.get("detailItem") or [])]
    if all_items:
        _insert_sales_return_items(client, now, all_items)

    # Expense line items
    all_expenses = [(r["id"], exp) for r in records for exp in (r.get("detailExpense") or [])]
    if all_expenses:
        _insert_sales_return_expenses(client, now, all_expenses)


def _insert_sales_return_items(client: Client, now: datetime, pairs: list[tuple]):
    client.insert(
        "sales_return_items",
        [
            [
                _id(item.get("id")),
                return_id,
                int(item.get("seq") or 0),
                _id(item.get("itemId")),
                _s(_nested(item, "item", "no")),
                _s(item.get("detailName") or _nested(item, "item", "name")),
                _s(_nested(item, "itemUnit", "name")),
                item.get("quantity"),
                item.get("unitPrice"),
                item.get("totalPrice"),
                item.get("tax1Rate"),
                item.get("tax1Amount"),
                now,
            ]
            for return_id, item in pairs
        ],
        column_names=[
            "id", "sales_return_id", "seq",
            "item_id", "item_no", "item_name", "item_unit",
            "quantity", "unit_price", "total_price",
            "tax1_rate", "tax1_amount", "updated_at",
        ],
    )
    logger.info("Upserted %d sales_return_items", len(pairs))


def _insert_sales_return_expenses(client: Client, now: datetime, pairs: list[tuple]):
    client.insert(
        "sales_return_expenses",
        [
            [
                _id(exp.get("id")),
                return_id,
                int(exp.get("seq") or 0),
                _id(exp.get("accountId")) or _id(_nested(exp, "account", "id")),
                _s(_nested(exp, "account", "name")),
                _s(exp.get("description")),
                exp.get("amount"),
                exp.get("tax1Rate"),
                exp.get("tax1Amount"),
                now,
            ]
            for return_id, exp in pairs
        ],
        column_names=[
            "id", "sales_return_id", "seq",
            "account_id", "account_name", "description",
            "amount", "tax1_rate", "tax1_amount", "updated_at",
        ],
    )
    logger.info("Upserted %d sales_return_expenses", len(pairs))


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _s(value) -> str:
    """Convert None to empty string for non-Nullable String columns."""
    return value if value is not None else ""


def _id(value, field: str = "", ref: str = "") -> int | None:
    """Return None for absent or zero ID values, optionally warning when missing.

    The Accurate API sometimes returns 0 instead of null for missing foreign
    keys.  This helper normalises 0 and None to None.  Pass ``field`` and
    ``ref`` to emit a warning when the resolved value is still falsy.
    """
    result = int(value) if value else None
    if field and not result:
        logger.warning("Missing %s on record %s", field, ref)
    return result


def _nested(obj: dict, *keys):
    """Safely navigate nested dicts: _nested(r, 'customer', 'id')."""
    for key in keys:
        if not isinstance(obj, dict):
            return None
        obj = obj.get(key)
    return obj


def _parse_timestamp(value: str | None) -> datetime | None:
    """Parse Accurate timestamp format: dd/MM/yyyy HH:mm:ss"""
    if not value:
        return None
    try:
        return datetime.strptime(value, "%d/%m/%Y %H:%M:%S")
    except (ValueError, TypeError):
        return None


def _parse_date(value: str | None) -> date | None:
    """Parse Accurate date format: dd/MM/yyyy"""
    if not value:
        return None
    try:
        return datetime.strptime(value, "%d/%m/%Y").date()
    except (ValueError, TypeError):
        return None
