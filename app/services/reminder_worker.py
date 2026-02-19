from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import logging

from aiogram import Bot

from app.keyboards.main import main_menu_keyboard
from app.services.workout_service import WorkoutService


class ReminderWorker:
    def __init__(self, bot: Bot, workout_service: WorkoutService, poll_seconds: int = 30) -> None:
        self._bot = bot
        self._workout_service = workout_service
        self._poll_seconds = poll_seconds
        self._stop_event = asyncio.Event()
        self._task: asyncio.Task[None] | None = None
        self._logger = logging.getLogger(__name__)

    async def start(self) -> None:
        if self._task is not None and not self._task.done():
            return

        self._stop_event.clear()
        self._task = asyncio.create_task(self._run(), name="reminder-worker")

    async def stop(self) -> None:
        self._stop_event.set()
        if self._task is None:
            return

        await self._task
        self._task = None

    async def _run(self) -> None:
        while not self._stop_event.is_set():
            now_utc = datetime.now(timezone.utc).replace(second=0, microsecond=0)
            due_items = await self._workout_service.find_due_reminders(now_utc)

            for due in due_items:
                try:
                    await self._bot.send_message(
                        due.telegram_id,
                        "⏰ Workout reminder: time to train and log your session.",
                        reply_markup=main_menu_keyboard(),
                    )
                except Exception:
                    self._logger.exception("Failed to send reminder to user=%s", due.telegram_id)
                    continue

                await self._workout_service.mark_reminded(due.telegram_id, due.local_date)

            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=self._poll_seconds)
            except TimeoutError:
                continue
