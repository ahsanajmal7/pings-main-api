import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    vapi_api_key: str
    vapi_assistant_id: str

    # Existing verticals
    vapi_assistant_medicare_live: str
    vapi_assistant_final_expense_live: str
    vapi_phone_number_id: str
    vapi_phone_number_medicare_live: str
    vapi_phone_number_final_expense_live: str

    # New verticals
    vapi_assistant_bathroom_remodel: str
    vapi_assistant_debt_settlement: str
    vapi_assistant_private_health: str
    vapi_assistant_windows_live: str
    vapi_assistant_hvac: str
    vapi_assistant_pest_control: str
    vapi_assistant_aca_health_insurance: str
    vapi_assistant_plumbing: str
    vapi_phone_number_bathroom_remodel: str
    vapi_phone_number_debt_settlement: str
    vapi_phone_number_private_health: str
    vapi_phone_number_windows_live: str
    vapi_phone_number_hvac: str
    vapi_phone_number_pest_control: str
    vapi_phone_number_aca_health_insurance: str
    vapi_phone_number_plumbing: str

    min_delay_seconds: float
    max_delay_seconds: float
    max_retries: int
    retry_delay_seconds: float
    skip_called_numbers: bool
    max_concurrent_calls: int
    vapi_base_url: str
    db_connection_string: str

    def assistant_id_for_vertical(self, vertical: Optional[str]) -> str:
        """Map DB Vertical column to the matching VAPI assistant ID."""
        key = (vertical or "").strip().lower()
        if "final expense" in key:
            return self.vapi_assistant_final_expense_live or self.vapi_assistant_id
        if "medicare" in key:
            return self.vapi_assistant_medicare_live or self.vapi_assistant_id
        if "bathroom remodel" in key:
            return self.vapi_assistant_bathroom_remodel or self.vapi_assistant_id
        if "debt settlement" in key:
            return self.vapi_assistant_debt_settlement or self.vapi_assistant_id
        if "private health" in key:
            return self.vapi_assistant_private_health or self.vapi_assistant_id
        if "windows" in key:
            return self.vapi_assistant_windows_live or self.vapi_assistant_id
        if "hvac" in key:
            return self.vapi_assistant_hvac or self.vapi_assistant_id
        if "pest control" in key:
            return self.vapi_assistant_pest_control or self.vapi_assistant_id
        if "aca" in key or "aca health" in key:
            return self.vapi_assistant_aca_health_insurance or self.vapi_assistant_id
        if "plumbing" in key:
            return self.vapi_assistant_plumbing or self.vapi_assistant_id
        return self.vapi_assistant_id

    def phone_number_id_for_vertical(self, vertical: Optional[str]) -> str:
        """Map DB Vertical column to the matching VAPI outbound phone number ID."""
        key = (vertical or "").strip().lower()
        if "final expense" in key:
            return self.vapi_phone_number_final_expense_live or self.vapi_phone_number_id
        if "medicare" in key:
            return self.vapi_phone_number_medicare_live or self.vapi_phone_number_id
        if "bathroom remodel" in key:
            return self.vapi_phone_number_bathroom_remodel or self.vapi_phone_number_id
        if "debt settlement" in key:
            return self.vapi_phone_number_debt_settlement or self.vapi_phone_number_id
        if "private health" in key:
            return self.vapi_phone_number_private_health or self.vapi_phone_number_id
        if "windows" in key:
            return self.vapi_phone_number_windows_live or self.vapi_phone_number_id
        if "hvac" in key:
            return self.vapi_phone_number_hvac or self.vapi_phone_number_id
        if "pest control" in key:
            return self.vapi_phone_number_pest_control or self.vapi_phone_number_id
        if "aca" in key or "aca health" in key:
            return self.vapi_phone_number_aca_health_insurance or self.vapi_phone_number_id
        if "plumbing" in key:
            return self.vapi_phone_number_plumbing or self.vapi_phone_number_id
        return self.vapi_phone_number_id


def _to_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def get_settings() -> Settings:
    return Settings(
        vapi_api_key=os.getenv("VAPI_API_KEY", "").strip(),
        vapi_assistant_id=os.getenv("VAPI_ASSISTANT_ID", "").strip(),

        # Existing verticals
        vapi_assistant_medicare_live=os.getenv("VAPI_ASSISTANT_MEDICARE_LIVE", "").strip(),
        vapi_assistant_final_expense_live=os.getenv("VAPI_ASSISTANT_FINAL_EXPENSE_LIVE", "").strip(),
        vapi_phone_number_id=os.getenv("VAPI_PHONE_NUMBER_ID", "").strip(),
        vapi_phone_number_medicare_live=os.getenv("VAPI_PHONE_NUMBER_MEDICARE_LIVE", "").strip(),
        vapi_phone_number_final_expense_live=os.getenv("VAPI_PHONE_NUMBER_FINAL_EXPENSE_LIVE", "").strip(),

        # New verticals — Assistant IDs
        vapi_assistant_bathroom_remodel=os.getenv("VAPI_ASSISTANT_BATHROOM_REMODEL", "").strip(),
        vapi_assistant_debt_settlement=os.getenv("VAPI_ASSISTANT_DEBT_SETTLEMENT", "").strip(),
        vapi_assistant_private_health=os.getenv("VAPI_ASSISTANT_PRIVATE_HEALTH", "").strip(),
        vapi_assistant_windows_live=os.getenv("VAPI_ASSISTANT_WINDOWS_LIVE", "").strip(),
        vapi_assistant_hvac=os.getenv("VAPI_ASSISTANT_HVAC", "").strip(),
        vapi_assistant_pest_control=os.getenv("VAPI_ASSISTANT_PEST_CONTROL", "").strip(),
        vapi_assistant_aca_health_insurance=os.getenv("VAPI_ASSISTANT_ACA_HEALTH_INSURANCE", "").strip(),
        vapi_assistant_plumbing=os.getenv("VAPI_ASSISTANT_PLUMBING", "").strip(),

        # New verticals — Phone Number IDs
        vapi_phone_number_bathroom_remodel=os.getenv("VAPI_PHONE_NUMBER_BATHROOM_REMODEL", "").strip(),
        vapi_phone_number_debt_settlement=os.getenv("VAPI_PHONE_NUMBER_DEBT_SETTLEMENT", "").strip(),
        vapi_phone_number_private_health=os.getenv("VAPI_PHONE_NUMBER_PRIVATE_HEALTH", "").strip(),
        vapi_phone_number_windows_live=os.getenv("VAPI_PHONE_NUMBER_WINDOWS_LIVE", "").strip(),
        vapi_phone_number_hvac=os.getenv("VAPI_PHONE_NUMBER_HVAC", "").strip(),
        vapi_phone_number_pest_control=os.getenv("VAPI_PHONE_NUMBER_PEST_CONTROL", "").strip(),
        vapi_phone_number_aca_health_insurance=os.getenv("VAPI_PHONE_NUMBER_ACA_HEALTH_INSURANCE", "").strip(),
        vapi_phone_number_plumbing=os.getenv("VAPI_PHONE_NUMBER_PLUMBING", "").strip(),

        min_delay_seconds=float(os.getenv("MIN_DELAY_SECONDS", "2")),
        max_delay_seconds=float(os.getenv("MAX_DELAY_SECONDS", "5")),
        max_retries=int(os.getenv("MAX_RETRIES", "2")),
        retry_delay_seconds=float(os.getenv("RETRY_DELAY_SECONDS", "2")),
        skip_called_numbers=_to_bool(os.getenv("SKIP_CALLED_NUMBERS"), default=True),
        max_concurrent_calls=max(1, int(os.getenv("MAX_CONCURRENT_CALLS", "3"))),
        vapi_base_url=os.getenv("VAPI_BASE_URL", "https://api.vapi.ai").strip(),
        db_connection_string=os.getenv("DB_CONNECTION_STRING", "").strip(),
    )