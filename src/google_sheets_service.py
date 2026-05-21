import logging
from typing import List

import gspread
from gspread.exceptions import WorksheetNotFound
from gspread.utils import rowcol_to_a1
from google.oauth2.service_account import Credentials

from src.models import ContactRow

logger = logging.getLogger(__name__)


def _norm_header(key: str) -> str:
    return key.strip().lower().replace(" ", "_").replace("-", "_")


def _record_by_normalized_keys(record: dict) -> dict:
    return {_norm_header(k): v for k, v in record.items()}


def _pick_name(flat: dict) -> str:
    for k in ("name", "full_name", "caller_name", "customer_name"):
        v = flat.get(k)
        if v is not None and str(v).strip():
            return str(v).strip()
    return ""


def _pick_phone(flat: dict) -> str:
    for k in ("phone_number", "phone", "mobile", "number", "ph"):
        v = flat.get(k)
        if v is not None and str(v).strip():
            return str(v).strip()
    return ""


def _pick_notes(flat: dict) -> str:
    for k in ("additional_notes", "notes", "note", "comments"):
        v = flat.get(k)
        if v is not None and str(v).strip():
            return str(v).strip()
    return ""


class GoogleSheetsService:
    def __init__(self, sheet_id: str, service_account_file: str, worksheet_name: str):
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.readonly",
        ]
        credentials = Credentials.from_service_account_file(
            service_account_file, scopes=scopes
        )
        client = gspread.authorize(credentials)
        spreadsheet = client.open_by_key(sheet_id)
        try:
            self.worksheet = spreadsheet.worksheet(worksheet_name)
        except WorksheetNotFound:
            logger.warning("Worksheet '%s' not found. Falling back to first sheet.", worksheet_name)
            self.worksheet = spreadsheet.sheet1

    def get_contact_rows(self) -> List[ContactRow]:
        records = self.worksheet.get_all_records(default_blank="")
        contacts: List[ContactRow] = []

        for idx, record in enumerate(records, start=2):
            flat = _record_by_normalized_keys(record)
            name = _pick_name(flat)
            phone_number = _pick_phone(flat)
            notes = _pick_notes(flat)
            status_val = flat.get("status")
            status = str(status_val).strip() if status_val is not None else ""
            status = status or None

            if not name or not phone_number:
                logger.warning("Skipping invalid row %s: missing name or phone_number", idx)
                continue

            contacts.append(
                ContactRow(
                    row_number=idx,
                    name=name,
                    phone_number=phone_number,
                    notes=notes,
                    status=status,
                )
            )
        return contacts

    def ensure_status_column(self) -> int:
        headers = self.worksheet.row_values(1)
        normalized = [h.strip().lower() for h in headers]

        if "status" in normalized:
            return normalized.index("status") + 1

        status_col = len(headers) + 1 if headers else 1
        cell_ref = rowcol_to_a1(1, status_col)
        self.worksheet.update(cell_ref, [["status"]])
        return status_col

    def update_status(self, row_number: int, status_col: int, status: str) -> None:
        cell_ref = rowcol_to_a1(row_number, status_col)
        self.worksheet.update(cell_ref, [[status]])
