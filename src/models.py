from dataclasses import dataclass
from typing import Optional


@dataclass
class ContactRow:
    row_number: int
    name: str
    phone_number: str
    notes: str = ""
    status: Optional[str] = None
