from __future__ import annotations

import re
import unicodedata
from datetime import date
from decimal import Decimal, InvalidOperation


def normalize_header(value: str) -> str:
    text = value.strip().lower()
    text = "".join(
        char
        for char in unicodedata.normalize("NFKD", text)
        if not unicodedata.combining(char)
    )
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def parse_money(value: str) -> Decimal:
    if value is None:
        raise ValueError("Currency value is missing")

    cleaned = str(value).strip()
    cleaned = cleaned.replace("R$", "").replace(" ", "")
    cleaned = re.sub(r"[^0-9,.\-]", "", cleaned)

    if not cleaned:
        return Decimal("0")

    if "," in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")
    else:
        parts = cleaned.split(".")
        if len(parts) > 1 and all(len(part) == 3 for part in parts[1:]):
            cleaned = "".join(parts)

    try:
        return Decimal(cleaned)
    except InvalidOperation as exc:
        raise ValueError(f"Invalid currency value: {value!r}") from exc


def parse_int(value: str) -> int:
    cleaned = re.sub(r"[^0-9\-]", "", str(value or ""))
    if not cleaned:
        return 0
    return int(cleaned)


def parse_date(value: str) -> date:
    return date.fromisoformat(str(value).strip())
