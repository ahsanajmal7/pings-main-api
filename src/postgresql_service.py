import logging
import psycopg2
import psycopg2.extras
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ContactRow:
    row_number: int          # Id in DB
    name: str                # FullName
    phone_number: str        # CustomerPhone
    status: Optional[bool]   # IsCalled
    notes: Optional[str]     # EventName
    event_slug: Optional[str]
    customer_email: Optional[str]
    customer_timezone: Optional[str]
    first_name: Optional[str]
    is_qualified: Optional[bool]
    vertical: Optional[str]
    language: Optional[str]
    zip: Optional[str]
    state: Optional[str]


class PostgreSQLService:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    def _get_conn(self):
        return psycopg2.connect(self.connection_string)

    def get_contact_rows(self) -> List[ContactRow]:
        """Fetch all contacts where IsCalled = false"""
        with self._get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT *
                    FROM "RejectedPings"
                    WHERE "IsCalled" = false
                    AND "EventName" = 'Ping Rejected'
                    ORDER BY "CreatedAt" ASC
                """)
                rows = cur.fetchall()
                logger.info("Fetched %d contacts from RejectedPings", len(rows))
                return [
                    ContactRow(
                        row_number=row["Id"],
                        name=row.get("FullName") or row.get("CustomerName") or "",
                        phone_number=row["CustomerPhone"],
                        status=row.get("IsCalled"),
                        notes=row.get("EventName"),
                        event_slug=row.get("EventSlug"),
                        customer_email=row.get("CustomerEmail"),
                        customer_timezone=row.get("CustomerTimezone"),
                        first_name=row.get("FirstName"),
                        is_qualified=row.get("IsQualified"),
                        vertical=row.get("Vertical"),
                        language=row.get("Language"),
                        zip=row.get("Zip"),
                        state=row.get("State"),
                    )
                    for row in rows
                ]

    def update_status(self, contact_id: int, is_called: bool = True):
        """Update IsCalled status after call attempt"""
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE "RejectedPings"
                    SET "IsCalled" = %s
                    WHERE "Id" = %s
                    """,
                    (is_called, contact_id),
                )
            conn.commit()
            logger.info("Updated IsCalled=%s for Id=%d", is_called, contact_id)

    def mark_qualified(self, contact_id: int):
        """Mark contact as qualified after successful call"""
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE "RejectedPings"
                    SET "IsQualified" = true, "IsCalled" = true
                    WHERE "Id" = %s
                    """,
                    (contact_id,),
                )
            conn.commit()
            logger.info("Marked Id=%d as Qualified", contact_id)

    def mark_qualified_by_phone(self, phone_number: str):
        """Mark contact as qualified by phone number — called from VAPI webhook"""
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE "RejectedPings"
                    SET "IsQualified" = true
                    WHERE "CustomerPhone" = %s
                    """,
                    (phone_number,),
                )
            conn.commit()
            logger.info("Marked IsQualified=true for phone=%s", phone_number)
