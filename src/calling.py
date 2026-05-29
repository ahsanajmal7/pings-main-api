import logging
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, List

from src.config import Settings, get_settings
from src.postgresql_service import ContactRow, PostgreSQLService
from src.logger import configure_logging
from src.vapi_service import VapiService

logger = logging.getLogger(__name__)


def _call_contact(
    contact: ContactRow,
    settings: Settings,
    db: PostgreSQLService,
    vapi: VapiService,
) -> Dict[str, int]:
    """Start one call, wait for completion, and return partial counts."""
    result = {"called": 0, "failed": 0, "qualified": 0}

    logger.info("Calling %s (%s)", contact.phone_number, contact.name)

    success = False
    call_id = None

    for attempt in range(1, settings.max_retries + 2):
        try:
            response = vapi.start_call(
                phone_number=contact.phone_number,
                name=contact.name,
                notes=contact.notes,
            )
            if 200 <= response.status_code < 300:
                call_id = response.json().get("id")
                logger.info(
                    "Call started for %s — call_id: %s",
                    contact.phone_number,
                    call_id,
                )
                db.update_status(contact.row_number, is_called=True)
                result["called"] = 1
                success = True
                break

            logger.error(
                "Call failed for %s (attempt %s): HTTP %s: %s",
                contact.phone_number,
                attempt,
                response.status_code,
                response.text,
            )
        except Exception:  # noqa: BLE001
            logger.exception(
                "Call exception for %s (attempt %s)",
                contact.phone_number,
                attempt,
            )

        if attempt <= settings.max_retries:
            time.sleep(settings.retry_delay_seconds)

    if not success:
        result["failed"] = 1
        db.update_status(contact.row_number, is_called=False)
        return result

    if call_id:
        logger.info("Waiting for call %s to complete...", call_id)
        call_data = vapi.wait_for_call_completion(call_id)

        if call_data:
            ended_reason = call_data.get("endedReason", "")
            logger.info("Call %s ended — reason: %s", call_id, ended_reason)
            if ended_reason in ("transfer", "assistant-forwarded-call"):
                db.mark_qualified_by_phone(contact.phone_number)
                result["qualified"] = 1
                logger.info("Marked qualified for %s", contact.phone_number)
        else:
            logger.warning("Could not get final status for call %s", call_id)

    delay = random.uniform(settings.min_delay_seconds, settings.max_delay_seconds)
    time.sleep(delay)

    return result


def start_calling_workflow(dry_run: bool = False) -> Dict[str, Any]:
    configure_logging()
    settings = get_settings()

    missing_env = [
        key
        for key, value in {
            "VAPI_API_KEY": settings.vapi_api_key,
            "VAPI_ASSISTANT_ID": settings.vapi_assistant_id,
            "VAPI_PHONE_NUMBER_ID": settings.vapi_phone_number_id,
            "DB_CONNECTION_STRING": settings.db_connection_string,
        }.items()
        if not value
    ]
    if missing_env:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_env)}")

    db = PostgreSQLService(connection_string=settings.db_connection_string)
    vapi = VapiService(
        api_key=settings.vapi_api_key,
        assistant_id=settings.vapi_assistant_id,
        phone_number_id=settings.vapi_phone_number_id,
        base_url=settings.vapi_base_url,
    )

    contacts = db.get_contact_rows()

    called = 0
    failed = 0
    skipped = 0
    would_call = 0
    qualified = 0
    contacts_to_call: List[ContactRow] = []

    for contact in contacts:
        if settings.skip_called_numbers and contact.status is True:
            logger.info("Skipping already-called number: %s", contact.phone_number)
            skipped += 1
            continue

        if dry_run:
            logger.info("[DRY RUN] Would call %s (%s)", contact.phone_number, contact.name)
            would_call += 1
            continue

        contacts_to_call.append(contact)

    if contacts_to_call:
        workers = min(settings.max_concurrent_calls, len(contacts_to_call))
        logger.info(
            "Starting %d calls with %d parallel workers",
            len(contacts_to_call),
            workers,
        )

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [
                executor.submit(_call_contact, contact, settings, db, vapi)
                for contact in contacts_to_call
            ]
            for future in as_completed(futures):
                try:
                    partial = future.result()
                except Exception:  # noqa: BLE001
                    logger.exception("Unexpected error processing contact")
                    failed += 1
                    continue

                called += partial["called"]
                failed += partial["failed"]
                qualified += partial["qualified"]

    return {
        "total_rows": len(contacts),
        "dry_run": dry_run,
        "max_concurrent_calls": settings.max_concurrent_calls,
        "would_call": would_call,
        "called": called,
        "failed": failed,
        "skipped": skipped,
        "qualified": qualified,
    }
