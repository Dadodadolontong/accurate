"""db_manager.py – ClickHouse persistence layer.

All tables use ReplacingMergeTree(updated_at) so that repeated INSERTs are
idempotent.  Deduplication happens on background merge; use
``SELECT … FINAL`` when you need immediate consistency (e.g. sync_log reads).

Entity table schemas are auto-generated from schema_defs.*_COLUMNS definitions.
To add, remove, or rename a field, edit schema_defs.py only.
"""

import logging
from collections.abc import Callable
from datetime import date, datetime, timedelta

import clickhouse_connect
from clickhouse_connect.driver.client import Client

from accurate_client import DETAIL_FAILED
from config import CH_DATABASE, CH_HOST, CH_PASSWORD, CH_PORT, CH_SECURE, CH_USER
from schema_defs import (
    CUSTOMER_CATEGORY_COLUMNS,
    CUSTOMER_COLUMNS,
    ITEM_BRAND_COLUMNS,
    PRODUCT_COLUMNS,
    SALES_INVOICE_COLUMNS,
    SALES_ORDER_COLUMNS,
    SALES_RETURN_COLUMNS,
    col_names,
    make_ddl,
)

logger = logging.getLogger(__name__)

# Max ids per ``IN {ids:Array(Int64)}`` lookup.  clickhouse-connect sends query
# parameters as HTTP form fields, and ClickHouse caps a single field at
# http_max_field_value_size (131072 bytes by default).  A full-sync id list
# (~30k invoice ids ≈ 290 KB serialised) blows straight past that and the
# server rejects it with "HTML Form Exception: Field value too long", so every
# lookup that takes an id list has to go out in chunks.
ID_QUERY_CHUNK = 5000


def _id_chunks(ids: list[int]) -> list[list[int]]:
    """Split *ids* into ID_QUERY_CHUNK-sized slices for parameterised lookups."""
    return [ids[i:i + ID_QUERY_CHUNK] for i in range(0, len(ids), ID_QUERY_CHUNK)]


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
    make_ddl("item_brands",         ITEM_BRAND_COLUMNS),
    make_ddl("products",            PRODUCT_COLUMNS),
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
        is_deleted       UInt8 DEFAULT 0,
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
        sales_order_id        Nullable(Int64),
        sales_order_detail_id Nullable(Int64),
        is_deleted       UInt8 DEFAULT 0,
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
        is_deleted       UInt8 DEFAULT 0,
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


# ---------------------------------------------------------------------------
# "_current" views – FINAL + is_deleted=0, pre-baked for external readers
# (Metabase and friends) that would otherwise query the raw ReplacingMergeTree
# tables directly and silently double-count unmerged duplicate parts.
# ---------------------------------------------------------------------------
_CURRENT_VIEW_TABLES = [
    "customer_categories",
    "customers",
    "item_brands",
    "products",
    "sales_orders",
    "sales_order_items",
    "sales_invoices",
    "sales_invoice_items",
    "sales_returns",
    "sales_return_items",
]


def _create_current_views(client: Client):
    for table in _CURRENT_VIEW_TABLES:
        client.command(
            f"CREATE OR REPLACE VIEW {table}_current AS "
            f"SELECT * FROM {table} FINAL WHERE is_deleted = 0"
        )
    logger.info("Ensured %d '_current' view(s) exist", len(_CURRENT_VIEW_TABLES))


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
    add_is_deleted_columns()
    add_invoice_item_so_link_columns(client)
    add_invoice_cash_discount_column(client)
    _create_current_views(client)
    _create_sales_order_backlog_view(client)


def add_invoice_item_so_link_columns(client: Client):
    """Add the sales-order link columns to sales_invoice_items on old deployments.

    Rows written before this migration have NULL links until their invoice is
    re-synced (run ``python reset_tables.py --entity sales_invoices`` or
    ``reset_sync_time("sales_invoices")`` to backfill).
    """
    for col in ("sales_order_id", "sales_order_detail_id"):
        client.command(
            f"ALTER TABLE sales_invoice_items ADD COLUMN IF NOT EXISTS {col} Nullable(Int64)"
        )


def add_invoice_cash_discount_column(client: Client):
    """Add cash_discount to sales_invoices on old deployments.

    Rows written before this migration have NULL until their invoice is
    re-synced; Laba/Rugi books this discount against revenue.
    """
    client.command(
        "ALTER TABLE sales_invoices ADD COLUMN IF NOT EXISTS "
        "cash_discount Nullable(Float64) AFTER tax1_rate"
    )


def _create_sales_order_backlog_view(client: Client):
    """One row per live sales-order line with what has been invoiced against it.

    backlog_quantity = ordered - invoiced (never negative); backlog_amount
    values it at the order's unit price. Computed at read time from the
    current order/invoice lines, so it needs no update step and cannot drift
    when an invoice is edited or deleted.
    """
    client.command("""
        CREATE OR REPLACE VIEW sales_order_backlog AS
        SELECT
            so.id                                        AS sales_order_id,
            so.number                                    AS sales_order_number,
            so.trans_date                                AS trans_date,
            so.ship_date                                 AS ship_date,
            so.customer_id                               AS customer_id,
            so.customer_name                             AS customer_name,
            so.status                                    AS status,
            soi.id                                       AS sales_order_item_id,
            soi.seq                                      AS seq,
            soi.item_id                                  AS item_id,
            soi.item_no                                  AS item_no,
            soi.item_name                                AS item_name,
            soi.item_unit                                AS item_unit,
            soi.unit_price                               AS unit_price,
            ifNull(soi.quantity, 0)                      AS ordered_quantity,
            ifNull(inv.invoiced_quantity, 0)             AS invoiced_quantity,
            greatest(ordered_quantity - invoiced_quantity, 0) AS backlog_quantity,
            backlog_quantity * ifNull(soi.unit_price, 0) AS backlog_amount
        FROM sales_order_items_current AS soi
        INNER JOIN sales_orders_current AS so ON so.id = soi.sales_order_id
        LEFT JOIN (
            SELECT
                sii.sales_order_detail_id AS sales_order_detail_id,
                sum(ifNull(sii.quantity, 0)) AS invoiced_quantity
            FROM sales_invoice_items_current AS sii
            INNER JOIN sales_invoices_current AS si ON si.id = sii.sales_invoice_id
            WHERE sii.sales_order_detail_id IS NOT NULL
            GROUP BY sii.sales_order_detail_id
        ) AS inv ON inv.sales_order_detail_id = soi.id
    """)
    logger.info("Ensured 'sales_order_backlog' view exists")

    # Order-level rollup. Billing state is derived from the invoice-line links
    # rather than the sales_orders row, because an invoice does not bump the
    # order's lastUpdate in Accurate, so the order row (status, sales_invoice_id)
    # is not re-synced when it gets billed and goes stale.
    client.command("""
        CREATE OR REPLACE VIEW sales_order_billing_status AS
        SELECT
            *,
            multiIf(
                backlog_quantity = 0,  'Fully billed',
                invoiced_quantity = 0, 'Unbilled',
                'Partially billed'
            ) AS billing_status
        FROM (
            SELECT
                sales_order_id,
                any(sales_order_number) AS sales_order_number,
                any(trans_date)         AS trans_date,
                any(ship_date)          AS ship_date,
                any(customer_id)        AS customer_id,
                any(customer_name)      AS customer_name,
                sum(ordered_quantity)   AS ordered_quantity,
                sum(invoiced_quantity)  AS invoiced_quantity,
                sum(backlog_quantity)   AS backlog_quantity,
                sum(backlog_amount)     AS backlog_amount
            FROM sales_order_backlog
            GROUP BY sales_order_id
        )
        """)
    logger.info("Ensured 'sales_order_billing_status' view exists")


# Parent tables that track soft-deletes (child tables are excluded – filter via parent join)
_PARENT_TABLES = [
    "customer_categories",
    "customers",
    "item_brands",
    "products",
    "sales_orders",
    "sales_invoices",
    "sales_returns",
]

# Child line-item tables also carry is_deleted so individual lines that
# disappear from a transaction on edit (not just whole-record deletes) can be
# soft-deleted instead of lingering forever – see _sync_child_items().
_CHILD_ITEM_TABLES = [
    "sales_order_items",
    "sales_invoice_items",
    "sales_return_items",
]


def add_is_deleted_columns():
    """Add is_deleted column to parent tables that don't have it yet.

    Safe to call multiple times – uses IF NOT EXISTS.  Called automatically
    by initialize_tables() so existing deployments are migrated on next startup.
    """
    client = _get_client()
    for table in _PARENT_TABLES + _CHILD_ITEM_TABLES:
        try:
            client.command(
                f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS is_deleted UInt8 DEFAULT 0"
            )
            logger.debug("Ensured is_deleted column exists on %s", table)
        except Exception as exc:
            logger.warning("Could not add is_deleted to %s: %s", table, exc)


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
    "item_brands",
    "products",
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
    return None  # no prior sync → fetch all records (no lastUpdate filter)


def update_sync_log(entity: str, sync_time: datetime, records_synced: int):
    now = datetime.now()
    client = _get_client()
    client.insert(
        "sync_log",
        [[entity, sync_time, records_synced, now]],
        column_names=["entity", "last_sync_time", "records_synced", "updated_at"],
    )


def reset_sync_time(entity: str):
    """Delete the sync_log entry for *entity* so the next run does a full fetch.

    Call this after changing a _FIELDS_* constant so all records are re-fetched
    with the new field set.
    """
    client = _get_client()
    client.command(
        "ALTER TABLE sync_log DELETE WHERE entity = {entity:String}",
        parameters={"entity": entity},
    )
    logger.info("Reset sync time for '%s' – next run will do a full fetch", entity)


# ---------------------------------------------------------------------------
# Reconciliation helpers
# ---------------------------------------------------------------------------

def get_live_ids(table: str) -> set[int]:
    """Return the set of non-deleted IDs currently in *table*.

    Uses FINAL to collapse duplicates from ReplacingMergeTree before comparing.
    """
    client = _get_client()
    result = client.query(
        f"SELECT DISTINCT id FROM {table} FINAL WHERE is_deleted = 0"
    )
    return {row[0] for row in result.result_rows}


def soft_delete_child_records(table: str, parent_col: str, ids_by_parent: dict[int, list[int]]):
    """Insert soft-delete tombstones for child rows keyed by (parent_col, id).

    Child item tables (sales_invoice_items etc.) use
    ``ORDER BY (parent_col, id)`` rather than plain ``id``, so a tombstone MUST
    carry the correct parent id too -- ``soft_delete_records()`` alone leaves
    it at the column default (0), which puts the tombstone on a different sort
    key than the row it's meant to replace and it never collapses on merge/FINAL.
    """
    now = datetime.now()
    rows = [
        [child_id, parent_id, 1, now]
        for parent_id, child_ids in ids_by_parent.items()
        for child_id in child_ids
    ]
    if not rows:
        return
    client = _get_client()
    client.insert(
        table,
        rows,
        column_names=["id", parent_col, "is_deleted", "updated_at"],
    )
    logger.info("Soft-deleted %d child row(s) from %s", len(rows), table)


def soft_delete_records(table: str, ids: list[int]):
    """Insert soft-delete tombstones for *ids* in *table*.

    Each tombstone is a minimal row (id + is_deleted=1 + fresh updated_at).
    All other columns take their DEFAULT values.  Because
    ReplacingMergeTree(updated_at) keeps the row with the latest updated_at,
    these tombstones will win over the original rows on the next merge/FINAL
    query.

    Only safe for tables whose ORDER BY key is plain ``id`` (the parent
    entity tables). For child item tables use soft_delete_child_records().
    """
    if not ids:
        return
    now = datetime.now()
    client = _get_client()
    client.insert(
        table,
        [[id_, 1, now] for id_ in ids],
        column_names=["id", "is_deleted", "updated_at"],
    )
    logger.info("Soft-deleted %d record(s) from %s", len(ids), table)


# ---------------------------------------------------------------------------
# Duplicate-avoidance helpers
#
# Every sync writes a brand new ReplacingMergeTree version for each record it
# touches, even when the record's synced fields are byte-identical to what's
# already stored (e.g. an invoice's lastUpdate bumps for a reason unrelated to
# any synced column, or an unchanged record falls inside an overlapping
# incremental-sync window). Left unchecked this multiplies parts and forces
# every reader to use FINAL just to get a correct count. These helpers compare
# against the current live version and skip the insert when nothing changed.
# ---------------------------------------------------------------------------

def _dedup_rows(client: Client, table: str, columns: list, rows: list[list]) -> list[list]:
    """Drop rows from *rows* that are identical to the currently live row in *table*.

    ``rows`` must be ``[id, val1, val2, ..., valN, updated_at]`` in the exact
    order produced by ``col_names(columns)`` (id first, updated_at last).
    Returns only the rows that are new or whose values actually changed.
    """
    if not rows:
        return rows
    compare_cols = col_names(columns)[1:-1]  # drop leading id, trailing updated_at
    if not compare_cols:
        return rows
    ids = [row[0] for row in rows]
    cols_sql = ", ".join(compare_cols)
    chunks = _id_chunks(ids)
    current: dict = {}
    for n, chunk in enumerate(chunks, 1):
        result = client.query(
            f"SELECT id, {cols_sql} FROM {table} FINAL "
            f"WHERE id IN {{ids:Array(Int64)}} AND is_deleted = 0",
            parameters={"ids": chunk},
        )
        current.update({r[0]: tuple(r[1:]) for r in result.result_rows})
        if len(chunks) > 1:
            logger.info(
                "  %s dedup lookup: chunk %d/%d (%d/%d id(s), %d live row(s) so far)",
                table, n, len(chunks), min(n * ID_QUERY_CHUNK, len(ids)),
                len(ids), len(current),
            )
    changed = [row for row in rows if current.get(row[0]) != tuple(row[1:-1])]
    skipped = len(rows) - len(changed)
    if skipped:
        logger.info("Skipped %d unchanged %s row(s)", skipped, table)
    return changed


_CHILD_ITEM_COLUMNS = [
    "seq", "item_id", "item_no", "item_name", "item_unit",
    "quantity", "unit_price", "total_price", "tax1_rate", "tax1_amount",
]


def _sync_child_items(
    client: Client,
    now: datetime,
    table: str,
    parent_col: str,
    pairs: list[tuple],
    extra_cols: dict[str, Callable[[dict], object]] | None = None,
):
    """Upsert detailItem child rows for a parent transaction (sales invoice/order/return).

    Unlike a plain insert, this reconciles the child table against the parent's
    *current* detailItem list instead of only ever adding rows:

    - Line items no longer present on the parent (e.g. removed/replaced when
      the transaction was edited in Accurate, which assigns the replacement a
      new detail-item id) are soft-deleted instead of lingering forever as
      orphans that inflate SUM()s.
    - Line items whose values are unchanged from the current live row are
      skipped instead of writing a redundant duplicate version.

    ``extra_cols`` maps additional table-specific column names (after the
    common ``_CHILD_ITEM_COLUMNS``) to a function extracting the value from
    the API item, e.g. the sales-order link on invoice lines.
    """
    if not pairs:
        return
    extra_cols = extra_cols or {}
    value_cols = _CHILD_ITEM_COLUMNS + list(extra_cols)

    rows: list[list] = []
    new_ids_by_parent: dict[int, set[int]] = {}
    for parent_id, item in pairs:
        item_id = _id(item.get("id"))
        if item_id is None:
            continue
        new_ids_by_parent.setdefault(parent_id, set()).add(item_id)
        rows.append([
            item_id,
            parent_id,
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
            *(fn(item) for fn in extra_cols.values()),
        ])

    parent_ids = list(new_ids_by_parent.keys())
    live_ids_by_parent: dict[int, set[int]] = {}
    current_values: dict[int, tuple] = {}
    chunks = _id_chunks(parent_ids)
    for n, chunk in enumerate(chunks, 1):
        live = client.query(
            f"SELECT {parent_col}, id, {', '.join(value_cols)} FROM {table} FINAL "
            f"WHERE {parent_col} IN {{ids:Array(Int64)}} AND is_deleted = 0",
            parameters={"ids": chunk},
        )
        for row in live.result_rows:
            pid, iid = row[0], row[1]
            live_ids_by_parent.setdefault(pid, set()).add(iid)
            current_values[iid] = tuple(row[2:])
        if len(chunks) > 1:
            logger.info(
                "  %s live lookup: chunk %d/%d (%d/%d parent(s), %d live row(s) so far)",
                table, n, len(chunks), min(n * ID_QUERY_CHUNK, len(parent_ids)),
                len(parent_ids), len(current_values),
            )

    stale_by_parent = {
        pid: list(live_ids - new_ids_by_parent.get(pid, set()))
        for pid, live_ids in live_ids_by_parent.items()
        if live_ids - new_ids_by_parent.get(pid, set())
    }
    stale_ids = [iid for ids in stale_by_parent.values() for iid in ids]
    if stale_by_parent:
        soft_delete_child_records(table, parent_col, stale_by_parent)
        logger.info(
            "Soft-deleted %d orphaned %s row(s) no longer on their parent",
            len(stale_ids), table,
        )

    changed_rows = [row for row in rows if current_values.get(row[0]) != tuple(row[2:])]
    skipped = len(rows) - len(changed_rows)

    if changed_rows:
        client.insert(
            table,
            [row + [now] for row in changed_rows],
            column_names=["id", parent_col, *value_cols, "updated_at"],
        )
    logger.info(
        "Upserted %d %s row(s) (%d unchanged skipped, %d orphan(s) removed)",
        len(changed_rows), table, skipped, len(stale_ids),
    )


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


def upsert_item_brands(records: list[dict]):
    if not records:
        return
    now = datetime.now()
    client = _get_client()
    client.insert(
        "item_brands",
        [
            [
                r["id"],
                _s(r.get("name")),
                now,
            ]
            for r in records
        ],
        column_names=col_names(ITEM_BRAND_COLUMNS),
    )
    logger.info("Upserted %d item_brands", len(records))


def get_item_brand_map() -> dict[int, str]:
    """Return {item_brand_id: name} for every non-deleted brand.

    Fallback for products.item_brand_name when a record's nested itemBrand
    object is absent (e.g. detail.do responses, which return a flat
    itemBrandId with no nested relation, unlike list.do).
    """
    client = _get_client()
    result = client.query(
        "SELECT id, name FROM item_brands FINAL WHERE is_deleted = 0"
    )
    return {row[0]: row[1] for row in result.result_rows}


def _product_row(r: dict, brand_map: dict[int, str], now: datetime) -> list:
    brand_id = _id(_nested(r, "itemBrand", "id"))
    return [
        r["id"],
        _s(r.get("no")),
        _s(r.get("name")),
        _s(r.get("itemType")),
        _id(_nested(r, "itemCategory", "id")),
        _s(_nested(r, "itemCategory", "name")),
        brand_id,
        _s(_nested(r, "itemBrand", "name")) or brand_map.get(brand_id, ""),
        _s(_nested(r, "unit1", "name")),
        _s(r.get("upcNo")),
        bool(r.get("suspended")),
        _parse_timestamp(r.get("lastUpdate")),
        now,
    ]


def upsert_products(records: list[dict]):
    if not records:
        return
    now = datetime.now()
    client = _get_client()
    brand_map = get_item_brand_map()
    client.insert(
        "products",
        [_product_row(r, brand_map, now) for r in records],
        column_names=col_names(PRODUCT_COLUMNS),
    )
    logger.info("Upserted %d products", len(records))


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

    # An order whose detail.do fetch failed has no processHistory/detailItem;
    # writing it would blank the stored sales_invoice link. Keep the stored
    # version when there is one; a new order is still inserted header-only.
    failed_ids = [r["id"] for r in records if r.get(DETAIL_FAILED)]
    if failed_ids:
        stored = {
            row[0] for row in client.query(
                "SELECT id FROM sales_orders FINAL "
                "WHERE id IN {ids:Array(Int64)} AND is_deleted = 0",
                parameters={"ids": failed_ids},
            ).result_rows
        }
        if stored:
            logger.warning(
                "Skipping %d stored sales_order(s) whose detail fetch failed: %s",
                len(stored), sorted(stored),
            )
            records = [r for r in records if r["id"] not in stored]

    rows = [
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
    ]
    rows = _dedup_rows(client, "sales_orders", SALES_ORDER_COLUMNS, rows)
    if rows:
        client.insert("sales_orders", rows, column_names=col_names(SALES_ORDER_COLUMNS))
    logger.info("Upserted %d sales_orders (%d unchanged skipped)", len(rows), len(records) - len(rows))

    # Line items
    all_items = [(r["id"], item) for r in records for item in (r.get("detailItem") or [])]
    if all_items:
        _sync_child_items(client, now, "sales_order_items", "sales_order_id", all_items)

    # Expense line items
    all_expenses = [(r["id"], exp) for r in records for exp in (r.get("detailExpense") or [])]
    if all_expenses:
        _insert_sales_order_expenses(client, now, all_expenses)


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


def _item_sales_order_id(item: dict) -> int | None:
    return _id(item.get("salesOrderId")) or _id(_nested(item, "salesOrder", "id"))


def _item_sales_order_detail_id(item: dict) -> int | None:
    return _id(item.get("salesOrderDetailId")) or _id(_nested(item, "salesOrderDetail", "id"))


def upsert_sales_invoices(records: list[dict]):
    if not records:
        return
    now = datetime.now()
    client = _get_client()
    rows = [
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
            r.get("cashDiscount"),
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
    ]
    rows = _dedup_rows(client, "sales_invoices", SALES_INVOICE_COLUMNS, rows)
    if rows:
        client.insert("sales_invoices", rows, column_names=col_names(SALES_INVOICE_COLUMNS))
    logger.info("Upserted %d sales_invoices (%d unchanged skipped)", len(rows), len(records) - len(rows))

    # Line items
    all_items = [(r["id"], item) for r in records for item in (r.get("detailItem") or [])]
    if all_items:
        _sync_child_items(
            client, now, "sales_invoice_items", "sales_invoice_id", all_items,
            extra_cols={
                "sales_order_id": _item_sales_order_id,
                "sales_order_detail_id": _item_sales_order_detail_id,
            },
        )


def upsert_sales_returns(records: list[dict]):
    if not records:
        return
    now = datetime.now()
    client = _get_client()
    rows = [
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
    ]
    rows = _dedup_rows(client, "sales_returns", SALES_RETURN_COLUMNS, rows)
    if rows:
        client.insert("sales_returns", rows, column_names=col_names(SALES_RETURN_COLUMNS))
    logger.info("Upserted %d sales_returns (%d unchanged skipped)", len(rows), len(records) - len(rows))

    # Line items
    all_items = [(r["id"], item) for r in records for item in (r.get("detailItem") or [])]
    if all_items:
        _sync_child_items(client, now, "sales_return_items", "sales_return_id", all_items)

    # Expense line items
    all_expenses = [(r["id"], exp) for r in records for exp in (r.get("detailExpense") or [])]
    if all_expenses:
        _insert_sales_return_expenses(client, now, all_expenses)


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


# ClickHouse Date/DateTime are fixed-width (days/seconds since epoch) and
# silently corrupt the whole insert batch if a value falls outside their
# range - e.g. a fat-fingered year like "5959" overflows the UInt16 day
# count and clickhouse-connect raises a misleading "not Nullable" DataError
# that aborts every record in the batch, not just the bad one (seen in
# production: one sales order with shipDate "10/03/5959" blocked all
# sales_orders syncing for a month). Clamp to the valid range instead.
_MIN_DATETIME = datetime(1970, 1, 1)
_MAX_DATETIME = datetime(2106, 2, 7)
_MIN_DATE = date(1970, 1, 1)
_MAX_DATE = date(2149, 6, 6)


def _parse_timestamp(value: str | None) -> datetime | None:
    """Parse Accurate timestamp format: dd/MM/yyyy HH:mm:ss"""
    if not value:
        return None
    try:
        parsed = datetime.strptime(value, "%d/%m/%Y %H:%M:%S")
    except (ValueError, TypeError):
        return None
    if not (_MIN_DATETIME <= parsed <= _MAX_DATETIME):
        logger.warning("Discarding out-of-range timestamp %r", value)
        return None
    return parsed


def _parse_date(value: str | None) -> date | None:
    """Parse Accurate date format: dd/MM/yyyy"""
    if not value:
        return None
    try:
        parsed = datetime.strptime(value, "%d/%m/%Y").date()
    except (ValueError, TypeError):
        return None
    if not (_MIN_DATE <= parsed <= _MAX_DATE):
        logger.warning("Discarding out-of-range date %r", value)
        return None
    return parsed
