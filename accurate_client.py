"""accurate_client.py – Accurate Online API client using API Token auth.

Authentication (per request)
-----------------------------
Every request must include three HTTP headers:

  Authorization   : Bearer {ACCURATE_API_TOKEN}
  X-Api-Timestamp : current date/time in ISO 8601 UTC, e.g. "2023-11-02T09:32:43Z"
  X-Api-Signature : Base64( HMAC-SHA256(timestamp_string, SIGNATURE_SECRET) )

No OAuth2 flow, no session opening, no token refresh – the API Token never
expires as long as the user keeps it active in their Accurate Store settings.

Pagination
----------
The API returns pagination info in the ``sp`` key of every list response
(NOT in a ``paging`` key – that field is always null):

    sp.page       – current page (1-based)
    sp.pageCount  – total number of pages
    sp.rowCount   – total number of records across all pages

Fields
------
List endpoints return only the ``id`` field by default.  Pass a
comma-separated ``fields`` query parameter to request additional columns.
"""

import base64
import hashlib
import hmac
import logging
from datetime import datetime, timezone

import requests

from config import (
    ACCURATE_API_TOKEN,
    ACCURATE_HOST,
    ACCURATE_SIGNATURE_SECRET,
    PAGE_SIZE,
)

logger = logging.getLogger(__name__)


class AccurateClient:
    """Stateless API client – no persistent auth state needed."""

    # ------------------------------------------------------------------
    # Header construction
    # ------------------------------------------------------------------

    def _build_headers(self) -> dict:
        """Return the three required authentication headers for one request."""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        signature = base64.b64encode(
            hmac.new(
                ACCURATE_SIGNATURE_SECRET.encode("utf-8"),
                timestamp.encode("utf-8"),
                hashlib.sha256,
            ).digest()
        ).decode("utf-8")

        return {
            "Authorization":   f"Bearer {ACCURATE_API_TOKEN}",
            "X-Api-Timestamp": timestamp,
            "X-Api-Signature": signature,
        }

    # ------------------------------------------------------------------
    # Low-level HTTP
    # ------------------------------------------------------------------

    def _get(self, path: str, params: dict) -> dict:
        """Execute an authenticated GET request against the Accurate API."""
        url = f"{ACCURATE_HOST}/accurate{path}"
        response = requests.get(url, params=params, headers=self._build_headers())
        response.raise_for_status()
        return response.json()

    # ------------------------------------------------------------------
    # Paginated list helper
    # ------------------------------------------------------------------

    def get_list(
        self,
        path: str,
        last_update: datetime | None = None,
        fields: str | None = None,
    ) -> list[dict]:
        """Fetch every page from a list endpoint, optionally filtered by lastUpdate.

        Parameters
        ----------
        path:        e.g. ``/api/customer/list.do``
        last_update: when set, only records updated at or after this time are
                     fetched (incremental sync).
        fields:      comma-separated list of fields to return.
                     The API returns only ``id`` when this is omitted.
        """
        params: dict = {"sp.pageSize": PAGE_SIZE}
        if last_update:
            params["filter.lastUpdate.op"]  = "GREATER_EQUAL_THAN"
            params["filter.lastUpdate.val"] = last_update.strftime("%d/%m/%Y %H:%M:%S")
        if fields:
            params["fields"] = fields

        all_records: list[dict] = []
        page = 1

        while True:
            params["sp.page"] = page
            body = self._get(path, params)

            if not body.get("s"):
                logger.warning("API error on %s page %d: %s", path, page, body.get("d"))
                break

            records = body.get("d") or []
            if not records:
                break

            all_records.extend(records)

            # Pagination info lives in the 'sp' key (body['paging'] is always null).
            sp         = body.get("sp") or {}
            page_count = sp.get("pageCount", 0)
            row_count  = sp.get("rowCount", "?")
            logger.info(
                "  %s page %d → %d record(s)  (running total: %d / %s, pageCount: %s)",
                path, page, len(records), len(all_records), row_count,
                page_count if page_count else "unknown",
            )

            # Primary guard  – stop when we've consumed every page the API reports.
            # Fallback guard – stop when fewer records than PAGE_SIZE were returned,
            #                  which reliably signals the last partial page even if
            #                  sp is absent or pageCount is 0.
            if page_count > 0:
                if page >= page_count:
                    break
            else:
                if len(records) < PAGE_SIZE:
                    break
            page += 1

        logger.info("Fetched %d records from %s", len(all_records), path)
        return all_records

    # ------------------------------------------------------------------
    # Entity-specific helpers  (field lists match the ClickHouse schemas)
    # ------------------------------------------------------------------

    # customer-category/list.do does NOT honour the 'fields' parameter –
    # it always returns only {"id": N}.  We therefore fetch IDs from the
    # list endpoint, then call detail.do for each record individually.
    # This is acceptable because there are typically very few categories (<50).

    _FIELDS_CUSTOMER = (
        "id,customerNo,name,email,mobilePhone,workPhone,fax,"
        "billStreet,billCity,billProvince,billZipCode,billCountry,"
        "categoryId,category,currencyId,defaultTermId,term,"
        "notes,website,npwpNo,suspended,customerTaxType,documentCode,"
        "lastUpdate,createDate"
    )

    _FIELDS_SALES_INVOICE = (
        "id,number,transDate,dueDate,taxDate,shipDate,"
        "customerId,customer,totalAmount,subTotal,salesAmount,"
        "tax1Amount,tax1Rate,outstanding,status,approvalStatus,"
        "description,masterSalesmanId,masterSalesmanName,"
        "branchId,branchName,currencyId,rate,detailItem"
    )

    _FIELDS_SALES_RETURN = (
        "id,number,transDate,taxDate,"
        "customerId,customer,invoiceId,totalAmount,subTotal,"
        "returnAmount,tax1Amount,tax1Rate,"
        "returnType,returnStatusType,approvalStatus,"
        "description,branchId,currencyId,rate,detailItem,detailExpense"
    )

    def get_customer_categories(self, last_update: datetime | None = None) -> list[dict]:
        """Fetch all customer categories.

        The list endpoint ignores the ``fields`` parameter and always returns
        only the id.  We therefore collect all IDs first, then fetch the full
        detail for each record individually.
        """
        id_records = self.get_list(
            "/api/customer-category/list.do",
            last_update,
            fields=None,          # only id is ever returned
        )
        results: list[dict] = []
        for rec in id_records:
            cat_id = rec.get("id")
            if not cat_id:
                continue
            body = self._get("/api/customer-category/detail.do", {"id": cat_id})
            if body.get("s") and body.get("d"):
                results.append(body["d"])
            else:
                logger.warning("Could not fetch customer-category detail for id=%s", cat_id)
        logger.info("Fetched %d customer categories (via detail endpoint)", len(results))
        return results

    def get_customers(self, last_update: datetime | None = None) -> list[dict]:
        return self.get_list(
            "/api/customer/list.do",
            last_update,
            fields=self._FIELDS_CUSTOMER,
        )

    def get_sales_invoices(self, last_update: datetime | None = None) -> list[dict]:
        return self.get_list(
            "/api/sales-invoice/list.do",
            last_update,
            fields=self._FIELDS_SALES_INVOICE,
        )

    def get_sales_returns(self, last_update: datetime | None = None) -> list[dict]:
        return self.get_list(
            "/api/sales-return/list.do",
            last_update,
            fields=self._FIELDS_SALES_RETURN,
        )
