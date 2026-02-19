from __future__ import annotations

from datetime import time
import re


UTC_OFFSET_RE = re.compile(r"^(?:UTC)?\s*([+-])\s*(\d{1,2})(?::?(\d{2}))?$", re.IGNORECASE)


def parse_positive_int(value: str, min_value: int = 1, max_value: int = 10000) -> int | None:
    text = value.strip()
    if not text.isdigit():
        return None

    parsed = int(text)
    if parsed < min_value or parsed > max_value:
        return None

    return parsed


def parse_optional_weight(value: str) -> tuple[bool, float | None]:
    text = value.strip().lower().replace(",", ".")
    if text in {"-", "skip", "none", "no"}:
        return True, None

    try:
        parsed = float(text)
    except ValueError:
        return False, None

    if parsed <= 0 or parsed > 2000:
        return False, None

    return True, round(parsed, 2)


def parse_utc_offset_to_minutes(value: str) -> int | None:
    text = value.strip()
    match = UTC_OFFSET_RE.match(text)
    if not match:
        return None

    sign, hours_raw, minutes_raw = match.groups()
    hours = int(hours_raw)
    minutes = int(minutes_raw or "0")

    if hours > 14 or minutes >= 60:
        return None

    total = hours * 60 + minutes
    if sign == "-":
        total *= -1

    return total


def parse_hhmm(value: str) -> time | None:
    text = value.strip()
    parts = text.split(":")
    if len(parts) != 2:
        return None

    hour_raw, minute_raw = parts
    if not (hour_raw.isdigit() and minute_raw.isdigit()):
        return None

    hour = int(hour_raw)
    minute = int(minute_raw)
    if hour < 0 or hour > 23 or minute < 0 or minute > 59:
        return None

    return time(hour=hour, minute=minute)


def normalize_optional_text(value: str, max_len: int) -> str | None:
    text = value.strip()
    if text in {"", "-"}:
        return None

    if len(text) > max_len:
        text = text[:max_len]

    return text
