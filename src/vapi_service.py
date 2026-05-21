import logging
import time
from typing import Dict, Any, Optional

import requests

from src.phone_utils import normalize_to_e164

logger = logging.getLogger(__name__)


class VapiService:
    def __init__(
        self,
        api_key: str,
        assistant_id: str,
        phone_number_id: str,
        base_url: str = "https://api.vapi.ai",
    ):
        self.assistant_id = assistant_id
        self.phone_number_id = phone_number_id.strip()
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def start_call(self, phone_number: str, name: str, notes: str) -> requests.Response:
        e164 = normalize_to_e164(phone_number)
        if e164 != phone_number.strip():
            logger.info("Normalized phone %r -> %s", phone_number, e164)
        payload: Dict[str, Any] = {
            "assistantId": self.assistant_id,
            "customer": {"number": e164},
            "assistantOverrides": {
                "variableValues": {
                    "name": name,
                    "notes": notes or "",
                }
            },
        }
        if self.phone_number_id:
            payload["phoneNumberId"] = self.phone_number_id
        return requests.post(
            f"{self.base_url}/call",
            json=payload,
            headers=self.headers,
            timeout=30,
        )

    def get_call_status(self, call_id: str) -> Optional[Dict[str, Any]]:
        """Fetch call details from VAPI by call ID"""
        try:
            response = requests.get(
                f"{self.base_url}/call/{call_id}",
                headers=self.headers,
                timeout=30,
            )
            if response.status_code == 200:
                return response.json()
            logger.error("Failed to get call status for %s: %s", call_id, response.text)
            return None
        except Exception as exc:  # noqa: BLE001
            logger.exception("Exception getting call status for %s: %s", call_id, exc)
            return None

    def wait_for_call_completion(
        self, call_id: str, poll_interval: int = 10, max_wait: int = 300
    ) -> Optional[Dict[str, Any]]:
        """
        Poll VAPI until call is ended or max_wait seconds reached.
        Returns final call data or None.
        """
        elapsed = 0
        while elapsed < max_wait:
            call_data = self.get_call_status(call_id)
            if not call_data:
                return None

            status = call_data.get("status", "")
            logger.info("Call %s status: %s (elapsed: %ds)", call_id, status, elapsed)

            if status == "ended":
                return call_data

            time.sleep(poll_interval)
            elapsed += poll_interval

        logger.warning("Call %s did not complete within %ds", call_id, max_wait)
        return None
