import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    vapi_api_key: str
    vapi_assistant_id: str
    vapi_phone_number_id: str
    min_delay_seconds: float
    max_delay_seconds: float
    max_retries: int
    retry_delay_seconds: float
    skip_called_numbers: bool
    max_concurrent_calls: int
    vapi_base_url: str
    db_connection_string: str  # PostgreSQL connection string


def _to_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def get_settings() -> Settings:
    return Settings(
        vapi_api_key=os.getenv("VAPI_API_KEY", "").strip(),
        vapi_assistant_id=os.getenv("VAPI_ASSISTANT_ID", "").strip(),
        vapi_phone_number_id=os.getenv("VAPI_PHONE_NUMBER_ID", "").strip(),
        min_delay_seconds=float(os.getenv("MIN_DELAY_SECONDS", "2")),
        max_delay_seconds=float(os.getenv("MAX_DELAY_SECONDS", "5")),
        max_retries=int(os.getenv("MAX_RETRIES", "2")),
        retry_delay_seconds=float(os.getenv("RETRY_DELAY_SECONDS", "2")),
        skip_called_numbers=_to_bool(os.getenv("SKIP_CALLED_NUMBERS"), default=True),
        max_concurrent_calls=max(1, int(os.getenv("MAX_CONCURRENT_CALLS", "3"))),
        vapi_base_url=os.getenv("VAPI_BASE_URL", "https://api.vapi.ai").strip(),
        db_connection_string=os.getenv("DB_CONNECTION_STRING", "").strip(),
    )
