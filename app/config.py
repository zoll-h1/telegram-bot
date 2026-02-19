from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    bot_token: str
    database_url: str
    log_level: str
    reminder_poll_seconds: int


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    bot_token = os.getenv("BOT_TOKEN", "").strip()
    if not bot_token:
        raise RuntimeError("BOT_TOKEN is not set. Put it in .env before running the bot.")

    database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/gym_portfolio.db").strip()
    log_level = os.getenv("LOG_LEVEL", "INFO").strip().upper()

    raw_poll_seconds = os.getenv("REMINDER_POLL_SECONDS", "30").strip()
    try:
        reminder_poll_seconds = int(raw_poll_seconds)
    except ValueError:
        reminder_poll_seconds = 30

    reminder_poll_seconds = max(10, reminder_poll_seconds)

    return Settings(
        bot_token=bot_token,
        database_url=database_url,
        log_level=log_level,
        reminder_poll_seconds=reminder_poll_seconds,
    )
