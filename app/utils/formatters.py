from __future__ import annotations

from datetime import datetime, timezone


def format_utc_offset(minutes: int) -> str:
    sign = "+" if minutes >= 0 else "-"
    absolute = abs(minutes)
    hours, remainder = divmod(absolute, 60)
    if remainder:
        return f"UTC{sign}{hours}:{remainder:02d}"
    return f"UTC{sign}{hours}"


def format_weight(weight_kg: float | None) -> str:
    if weight_kg is None:
        return "bodyweight"
    return f"{weight_kg:.1f} kg"


def format_volume(volume_kg: float) -> str:
    return f"{volume_kg:.1f} kg"


def format_dt_utc(dt: datetime) -> str:
    value = dt
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
