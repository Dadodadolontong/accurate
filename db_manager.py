"""db_manager.py – ClickHouse persistence layer.

All tables use ReplacingMergeTree(updated_at) so that repeated INSERTs are
idempotent.  Deduplication happens on background merge; use
``SELECT … FINAL`` when you need immediate consistency (e.g. sync_log reads).

Table schemas are kept in sync with the actual Accurate API response fields
discovered by probing the live endpoints.
"""

import logging
from datetime import date, datetime

import clickhouse_connect
from clickhouse_connect.driver.client import Client

from config import CH_DATABASE, CH_HOST, CH_PASSWORD, CH_PORT, CH_SECURE, CH_USER

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

    # ------------------------------------------------------------------
    # customer_categories
    # API fields: id, name, nameWithIndentStrip, lvl, defaultCategory,
    #             sub, parent{id,name}
    # ------------------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS customer_categories (
        id               Int64,
        name             String,
        name_strip       String,
        lvl              Int32,
        default_category Bool,
        sub              Bool,
        parent_id        Nullable(Int64),
        parent_name      String,
        updated_at       DateTime DEFAULT now()
    ) ENGINE = ReplacingMergeTree(updated_at)
    ORDER BY id
    """,

    # ------------------------------------------------------------------
    # customers
    # API fields: id, customerNo, name, email, mobilePhone, workPhone,
    #   fax, billStreet, billCity, billProvince, billZipCode, billCountry,
    #   categoryId, category{name}, currencyId, term{name},
    #   notes, website, npwpNo, suspended, customerTaxType, documentCode,
    #   lastUpdate, createDate
    # ------------------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS customers (
        id                Int64,
        customer_no       String,
        name              String,
        email             String,
        mobile_phone      String,
        work_phone        String,
        fax               String,
        bill_street       String,
        bill_city         String,
        bill_province     String,
        bill_zip_code     String,
        bill_country      String,
        category_id       Nullable(Int64),
        category_name     String,
        currency_id       Nullable(Int64),
        term_name         String,
        notes             String,
        website           String,
        npwp_no           String,
        suspended         Bool,
        customer_tax_type String,
        document_code     String,
        last_update       Nullable(DateTime),
        create_date       Nullable(DateTime),
        updated_at        DateTime DEFAULT now()
    ) ENGINE = ReplacingMergeTree(updated_at)
    ORDER BY id
    """,

    # ------------------------------------------------------------------
    # sales_invoices  (header only – line items in sales_invoice_items)
    # API fields: id, number, transDate, dueDate, taxDate, shipDate,
    #   customerId, customer{name}, totalAmount, subTotal, salesAmount,
    #   tax1Amount, tax1Rate, outstanding, status, approvalStatus,
    #   description, masterSalesmanId, masterSalesmanName,
    #   branchId, branchName, currencyId, rate
    # ------------------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS sales_invoices (
        id               Int64,
        number           String,
        trans_date       Nullable(Date),
        due_date         Nullable(Date),
        tax_date         Nullable(Date),
        ship_date        Nullable(Date),
        customer_id      Nullable(Int64),
        customer_name    String,
        total_amount     Nullable(Float64),
        sub_total        Nullable(Float64),
        sales_amount     Nullable(Float64),
        tax1_amount      Nullable(Float64),
        tax1_rate        Nullable(Float64),
        outstanding      Bool,
        status           String,
        approval_status  String,
        description      String,
        salesman_id      Nullable(Int64),
        salesman_name    String,
        branch_id        Nullable(Int64),
        branch_name      String,
        currency_id      Nullable(Int64),
        rate             Nullable(Float64),
        updated_at       DateTime DEFAULT now()
    ) ENGINE = ReplacingMergeTree(updated_at)
    ORDER BY id
    """,

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

    # ------------------------------------------------------------------
    # sales_returns  (header only – line items in sales_return_items)
    # API fields: id, number, transDate, taxDate,
    #   customerId, customer{name}, invoiceId,
    #   totalAmount, subTotal, returnAmount, tax1Amount, tax1Rate,
    #   returnType, returnStatusType, approvalStatus,
    #   description, branchId, currencyId, rate
    # ------------------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS sales_returns (
        id                  Int64,
        number              String,
        trans_date          Nullable(Date),
        tax_date            Nullable(Date),
        customer_id         Nullable(Int64),
        customer_name       String,
        invoice_id          Nullable(Int64),
        total_amount        Nullable(Float64),
        sub_total           Nullable(Float64),
        return_amount       Nullable(Float64),
        tax1_amount         Nullable(Float64),
        tax1_rate           Nullable(Float64),
        return_type         String,
        return_status_type  String,
        approval_status     String,
        description         String,
        branch_id           Nullable(Int64),
        currency_id         Nullable(Int64),
        rate                Nullable(Float64),
        updated_at          DateTime DEFAULT now()
    ) ENGINE = ReplacingMergeTree(updated_at)
    ORDER BY id
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
    "sales_invoices",
    "sales_invoice_items",
    "sales_returns",
    "sales_return_items",
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
        column_names=[
            "id", "name", "name_strip", "lvl", "default_category", "sub",
            "parent_id", "parent_name", "updated_at",
        ],
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
                r.get("categoryId") or _nested(r, "category", "id"),
                _s(_nested(r, "category", "name") or _nested(r, "category", "nameWithIndentStrip")),
                r.get("currencyId") or _nested(r, "currency", "id"),
                _s(_nested(r, "term", "name")),
                _s(r.get("notes")),
                _s(r.get("website")),
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
        column_names=[
            "id", "customer_no", "name", "email",
            "mobile_phone", "work_phone", "fax",
            "bill_street", "bill_city", "bill_province", "bill_zip_code", "bill_country",
            "category_id", "category_name", "currency_id", "term_name",
            "notes", "website", "npwp_no", "suspended",
            "customer_tax_type", "document_code",
            "last_update", "create_date", "updated_at",
        ],
    )
    logger.info("Upserted %d customers", len(records))


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
                r.get("customerId") or _nested(r, "customer", "id"),
                _s(_nested(r, "customer", "name") or _nested(r, "customer", "wpName")),
                r.get("totalAmount"),
                r.get("subTotal"),
                r.get("salesAmount"),
                r.get("tax1Amount"),
                r.get("tax1Rate"),
                bool(r.get("outstanding")),
                _s(r.get("status")),
                _s(r.get("approvalStatus")),
                _s(r.get("description")),
                r.get("masterSalesmanId"),
                _s(r.get("masterSalesmanName")),
                r.get("branchId"),
                _s(r.get("branchName")),
                r.get("currencyId"),
                r.get("rate"),
                now,
            ]
            for r in records
        ],
        column_names=[
            "id", "number", "trans_date", "due_date", "tax_date", "ship_date",
            "customer_id", "customer_name",
            "total_amount", "sub_total", "sales_amount", "tax1_amount", "tax1_rate",
            "outstanding", "status", "approval_status", "description",
            "salesman_id", "salesman_name", "branch_id", "branch_name",
            "currency_id", "rate", "updated_at",
        ],
    )
    logger.info("Upserted %d sales_invoices", len(records))

    # Line items
    all_items = [(r["id"], item) for r in records for item in (r.get("detailItem") or [])]
    if all_items:
        _insert_sales_invoice_items(client, now, all_items)


def _insert_sales_invoice_items(client: Client, now: datetime, pairs: list[tuple]):
    client.insert(
        "sales_invoice_items",
        [
            [
                item.get("id"),
                invoice_id,
                int(item.get("seq") or 0),
                item.get("itemId"),
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
                r.get("customerId") or _nested(r, "customer", "id"),
                _s(_nested(r, "customer", "name") or _nested(r, "customer", "wpName")),
                r.get("invoiceId"),
                r.get("totalAmount"),
                r.get("subTotal"),
                r.get("returnAmount"),
                r.get("tax1Amount"),
                r.get("tax1Rate"),
                _s(r.get("returnType")),
                _s(r.get("returnStatusType")),
                _s(r.get("approvalStatus")),
                _s(r.get("description")),
                r.get("branchId"),
                r.get("currencyId"),
                r.get("rate"),
                now,
            ]
            for r in records
        ],
        column_names=[
            "id", "number", "trans_date", "tax_date",
            "customer_id", "customer_name", "invoice_id",
            "total_amount", "sub_total", "return_amount", "tax1_amount", "tax1_rate",
            "return_type", "return_status_type", "approval_status", "description",
            "branch_id", "currency_id", "rate", "updated_at",
        ],
    )
    logger.info("Upserted %d sales_returns", len(records))

    # Line items
    all_items = [(r["id"], item) for r in records for item in (r.get("detailItem") or [])]
    if all_items:
        _insert_sales_return_items(client, now, all_items)


def _insert_sales_return_items(client: Client, now: datetime, pairs: list[tuple]):
    client.insert(
        "sales_return_items",
        [
            [
                item.get("id"),
                return_id,
                int(item.get("seq") or 0),
                item.get("itemId"),
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


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _s(value) -> str:
    """Convert None to empty string for non-Nullable String columns."""
    return value if value is not None else ""


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
