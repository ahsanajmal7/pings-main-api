"""Normalize phone strings to E.164 (+country...) for VAPI."""


def normalize_to_e164(phone: str) -> str:
    s = phone.strip()
    for ch in " \t\n\r()-":
        s = s.replace(ch, "")
    if s.startswith("+"):
        rest = "".join(c for c in s[1:] if c.isdigit())
        return f"+{rest}" if rest else phone.strip()

    digits = "".join(c for c in s if c.isdigit())
    if not digits:
        return phone.strip()

    # US / NANP: 10 digits (area + number)
    if len(digits) == 10:
        return f"+1{digits}"
    # US / NANP: 1 + 10 digits
    if len(digits) == 11 and digits[0] == "1":  
        return f"+{digits}"

    # Other regions: country code included, missing leading +
    return f"+{digits}"
