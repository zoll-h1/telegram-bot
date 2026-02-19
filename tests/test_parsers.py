from datetime import time

from app.utils.parsers import (
    normalize_optional_text,
    parse_hhmm,
    parse_optional_weight,
    parse_positive_int,
    parse_utc_offset_to_minutes,
)


def test_parse_positive_int() -> None:
    assert parse_positive_int("12") == 12
    assert parse_positive_int("0") is None
    assert parse_positive_int("abc") is None


def test_parse_optional_weight() -> None:
    assert parse_optional_weight("-") == (True, None)
    assert parse_optional_weight("80") == (True, 80.0)
    assert parse_optional_weight("80,5") == (True, 80.5)
    assert parse_optional_weight("-10") == (False, None)


def test_parse_utc_offset_to_minutes() -> None:
    assert parse_utc_offset_to_minutes("UTC+3") == 180
    assert parse_utc_offset_to_minutes("UTC-5:30") == -330
    assert parse_utc_offset_to_minutes("+2") == 120
    assert parse_utc_offset_to_minutes("UTC+99") is None


def test_parse_hhmm() -> None:
    assert parse_hhmm("07:45") == time(hour=7, minute=45)
    assert parse_hhmm("25:10") is None


def test_normalize_optional_text() -> None:
    assert normalize_optional_text("  hello  ", max_len=20) == "hello"
    assert normalize_optional_text("-", max_len=20) is None
    assert normalize_optional_text("a" * 300, max_len=10) == "a" * 10
