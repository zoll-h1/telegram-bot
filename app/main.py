from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import get_settings
from app.db.bootstrap import init_db
from app.db.session import create_engine_and_session_factory
from app.handlers import setup_routers
from app.services.reminder_worker import ReminderWorker
from app.services.workout_service import WorkoutService


async def _on_startup(reminder_worker: ReminderWorker, **_: object) -> None:
    await reminder_worker.start()


async def _on_shutdown(reminder_worker: ReminderWorker, **_: object) -> None:
    await reminder_worker.stop()


async def run() -> None:
    settings = get_settings()
    logging.basicConfig(
        level=getattr(logging, settings.log_level, logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    engine, session_factory = create_engine_and_session_factory(settings.database_url)
    await init_db(engine)

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dispatcher = Dispatcher(storage=MemoryStorage())

    workout_service = WorkoutService(session_factory)
    reminder_worker = ReminderWorker(bot, workout_service, poll_seconds=settings.reminder_poll_seconds)

    dispatcher["workout_service"] = workout_service
    dispatcher["reminder_worker"] = reminder_worker

    setup_routers(dispatcher)
    dispatcher.startup.register(_on_startup)
    dispatcher.shutdown.register(_on_shutdown)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dispatcher.start_polling(bot, allowed_updates=dispatcher.resolve_used_update_types())
    finally:
        await bot.session.close()
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(run())
