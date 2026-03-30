"""schema_defs.py – Single source of truth for entity → ClickHouse column mappings.

To add, remove, or rename a field, edit the relevant *_COLUMNS list here only.
Both the ``fields`` query parameter sent to the Accurate API and the ClickHouse
CREATE TABLE statement are derived automatically from these definitions.

Column fields
-------------
api_path : dot-path into the API response record, e.g. ``"category.name"``.
           The top-level name (the part before the first dot) is used as the
           ``fields`` API query param.  Use a plain name for scalar fields.
col      : ClickHouse column name.
ch_type  : ClickHouse column type.  Use ``""`` for child-table markers (below).

Child-table markers
-------------------
Set ``ch_type=""`` to mark a field whose value is a list that populates a
separate child table (e.g. ``detailItem`` → ``sales_invoice_items``).
These entries are included in the API ``fields`` request so the server returns
the list, but they are skipped when generating the parent-table DDL.
The ``col`` value documents which child table stores the data.
"""

from typing import NamedTuple


class Column(NamedTuple):
    api_path: str  # dot-path into API response, e.g. "category.name" or "id"
    col:      str  # ClickHouse column name (or child table name when ch_type="")
    ch_type:  str  # ClickHouse column type, or "" for child-table markers


# ── customer_categories ────────────────────────────────────────────────────
# Uses detail.do per record (list.do always ignores the 'fields' param).
# No _FIELDS_ string is derived from this – it is listed here for DDL only.

CUSTOMER_CATEGORY_COLUMNS: list[Column] = [
    Column("id",                  "id",               "Int64"),
    Column("name",                "name",             "String"),
    Column("nameWithIndentStrip", "name_strip",       "String"),
    Column("lvl",                 "lvl",              "Int32"),
    Column("defaultCategory",     "default_category", "Bool"),
    Column("sub",                 "sub",              "Bool"),
    Column("parent.id",           "parent_id",        "Nullable(Int64)"),
    Column("parent.name",         "parent_name",      "String"),
]

# ── customers ──────────────────────────────────────────────────────────────

CUSTOMER_COLUMNS: list[Column] = [
    Column("id",              "id",                "Int64"),
    Column("customerNo",      "customer_no",       "String"),
    Column("name",            "name",              "String"),
    Column("email",           "email",             "String"),
    Column("mobilePhone",     "mobile_phone",      "String"),
    Column("workPhone",       "work_phone",        "String"),
    Column("fax",             "fax",               "String"),
    Column("billStreet",      "bill_street",       "String"),
    Column("billCity",        "bill_city",         "String"),
    Column("billProvince",    "bill_province",     "String"),
    Column("billZipCode",     "bill_zip_code",     "String"),
    Column("billCountry",     "bill_country",      "String"),
    Column("categoryId",      "category_id",       "Nullable(Int64)"),
    Column("category.name",   "category_name",     "String"),
    Column("currency.code",    "currency_code",     "String"),
    Column("defaultTermId",   "default_term_id",   "Nullable(Int64)"),
    Column("term.name",       "term_name",         "String"),
    Column("notes",           "notes",             "String"),    
    Column("npwpNo",          "npwp_no",           "String"),
    Column("suspended",       "suspended",         "Bool"),
    Column("customerTaxType", "customer_tax_type", "String"),
    Column("documentCode",    "document_code",     "String"),
    Column("lastUpdate",      "last_update",       "Nullable(DateTime)"),
    Column("createDate",      "create_date",       "Nullable(DateTime)"),
]

# ── sales_orders ───────────────────────────────────────────────────────────

SALES_ORDER_COLUMNS: list[Column] = [
    Column("id",                 "id",              "Int64"),
    Column("number",             "number",          "String"),
    Column("transDate",          "trans_date",      "Nullable(Date)"),
    Column("shipDate",           "ship_date",       "Nullable(Date)"),
    Column("customerId",         "customer_id",     "Nullable(Int64)"),
    Column("customer.name",      "customer_name",   "String"),
    Column("totalAmount",        "total_amount",    "Nullable(Float64)"),
    Column("subTotal",           "sub_total",       "Nullable(Float64)"),
    Column("salesAmount",        "sales_amount",    "Nullable(Float64)"),
    Column("tax1Amount",         "tax1_amount",     "Nullable(Float64)"),
    Column("tax1Rate",           "tax1_rate",       "Nullable(Float64)"),
    Column("status",             "status",          "String"),
    Column("approvalStatus",     "approval_status", "String"),
    Column("description",        "description",     "String"),
    Column("poNumber",           "po_number",       "String"),
    Column("masterSalesmanId",   "salesman_id",     "Nullable(Int64)"),
    Column("masterSalesmanName", "salesman_name",   "String"),
    Column("branchId",           "branch_id",       "Nullable(Int64)"),
    Column("branchName",         "branch_name",     "String"),
    Column("currencyId",         "currency_id",     "Nullable(Int64)"),
    Column("rate",               "rate",              "Nullable(Float64)"),
    Column("lastUpdate",         "last_update",       "Nullable(DateTime)"),
    # Derived from processHistory: first entry where historyType == "SI"
    Column("processHistory",     "sales_invoice_id",  "Nullable(Int64)"),
    Column("processHistory",     "sales_invoice_name","String"),
    Column("detailItem",         "sales_order_items",    ""),  # child table
    Column("detailExpense",      "sales_order_expenses", ""),  # child table
]

# ── sales_invoices ─────────────────────────────────────────────────────────

SALES_INVOICE_COLUMNS: list[Column] = [
    Column("id",                 "id",              "Int64"),
    Column("number",             "number",          "String"),
    Column("transDate",          "trans_date",      "Nullable(Date)"),
    Column("dueDate",            "due_date",        "Nullable(Date)"),
    Column("taxDate",            "tax_date",        "Nullable(Date)"),
    Column("shipDate",           "ship_date",       "Nullable(Date)"),
    Column("customerId",         "customer_id",     "Nullable(Int64)"),
    Column("customer.name",      "customer_name",   "String"),
    Column("totalAmount",        "total_amount",    "Nullable(Float64)"),
    Column("subTotal",           "sub_total",       "Nullable(Float64)"),
    Column("salesAmount",        "sales_amount",    "Nullable(Float64)"),
    Column("tax1Amount",         "tax1_amount",     "Nullable(Float64)"),
    Column("tax1Rate",           "tax1_rate",       "Nullable(Float64)"),
    Column("outstanding",        "outstanding",     "Bool"),
    Column("status",             "status",          "String"),
    Column("approvalStatus",     "approval_status", "String"),
    Column("description",        "description",     "String"),
    Column("masterSalesmanId",   "salesman_id",     "Nullable(Int64)"),
    Column("masterSalesmanName", "salesman_name",   "String"),
    Column("branchId",           "branch_id",       "Nullable(Int64)"),
    Column("branchName",         "branch_name",     "String"),
    Column("currencyId",         "currency_id",     "Nullable(Int64)"),
    Column("rate",               "rate",            "Nullable(Float64)"),
    Column("detailItem",         "sales_invoice_items", ""),  # child table
]

# ── sales_returns ──────────────────────────────────────────────────────────

SALES_RETURN_COLUMNS: list[Column] = [
    Column("id",               "id",                 "Int64"),
    Column("number",           "number",             "String"),
    Column("transDate",        "trans_date",         "Nullable(Date)"),
    Column("taxDate",          "tax_date",           "Nullable(Date)"),
    Column("customerId",       "customer_id",        "Nullable(Int64)"),
    Column("customer.name",    "customer_name",      "String"),
    Column("invoiceId",        "invoice_id",         "Nullable(Int64)"),
    Column("totalAmount",      "total_amount",       "Nullable(Float64)"),
    Column("subTotal",         "sub_total",          "Nullable(Float64)"),
    Column("returnAmount",     "return_amount",      "Nullable(Float64)"),
    Column("tax1Amount",       "tax1_amount",        "Nullable(Float64)"),
    Column("tax1Rate",         "tax1_rate",          "Nullable(Float64)"),
    Column("returnType",       "return_type",        "String"),
    Column("returnStatusType", "return_status_type", "String"),
    Column("approvalStatus",   "approval_status",    "String"),
    Column("description",      "description",        "String"),
    Column("branchId",         "branch_id",          "Nullable(Int64)"),
    Column("currencyId",       "currency_id",        "Nullable(Int64)"),
    Column("rate",             "rate",               "Nullable(Float64)"),
    Column("detailItem",       "sales_return_items",    ""),  # child table
    Column("detailExpense",    "sales_return_expenses", ""),  # child table
]


# ---------------------------------------------------------------------------
# Helpers used by accurate_client.py and db_manager.py
# ---------------------------------------------------------------------------

def col_names(columns: list[Column]) -> list[str]:
    """Return the ordered list of ClickHouse column names for an entity's upsert call.

    Skips child-table markers (ch_type="") and appends "updated_at" at the end,
    matching the column order produced by make_ddl().

    Use this in upsert ``column_names=`` arguments so they stay in sync with
    schema_defs automatically::

        client.insert("customers", rows, column_names=col_names(CUSTOMER_COLUMNS))
    """
    return [c.col for c in columns if c.ch_type] + ["updated_at"]


def make_fields_param(columns: list[Column]) -> str:
    """Derive the comma-separated ``fields`` API query parameter from column definitions.

    Extracts the unique top-level field names (the part before the first dot),
    preserving declaration order.  Child-table markers (ch_type="") are excluded
    because list endpoints do not return nested arrays; those are fetched via
    detail.do separately.
    """
    seen: dict[str, None] = {}
    for col in columns:
        if not col.ch_type:  # skip child-table markers
            continue
        top = col.api_path.split(".")[0]
        seen[top] = None
    return ",".join(seen)


def make_ddl(table: str, columns: list[Column], order_by: str = "id") -> str:
    """Generate a ``CREATE TABLE IF NOT EXISTS`` statement from column definitions.

    Columns with ``ch_type=""`` (child-table markers) are skipped.
    An ``updated_at DateTime DEFAULT now()`` column is always appended last.
    """
    ddl_cols = [c for c in columns if c.ch_type]
    width = max(len(c.col) for c in ddl_cols)
    col_lines = "\n".join(
        f"        {c.col:<{width}}  {c.ch_type},"
        for c in ddl_cols
    )
    return f"""
    CREATE TABLE IF NOT EXISTS {table} (
{col_lines}
        {'updated_at':<{width}}  DateTime DEFAULT now()
    ) ENGINE = ReplacingMergeTree(updated_at)
    ORDER BY {order_by}
    """
