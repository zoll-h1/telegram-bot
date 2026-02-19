from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.services.workout_service import WorkoutService
from app.states.reminder import ReminderSetup
from app.utils.formatters import format_utc_offset
from app.utils.parsers import parse_hhmm, parse_utc_offset_to_minutes

router = Router(name="reminders")


@router.message(Command("reminder"))
@router.message(F.text == "⏰ Set Reminder")
async def cmd_reminder(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(ReminderSetup.timezone)
    await message.answer("Send timezone offset in format UTC+3 or UTC-5:30")


@router.message(ReminderSetup.timezone)
async def process_timezone(message: Message, state: FSMContext) -> None:
    text = message.text or ""
    offset = parse_utc_offset_to_minutes(text)
    if offset is None:
        await message.answer("Invalid offset. Examples: UTC+2, UTC-4, UTC+5:30")
        return

    await state.update_data(offset_minutes=offset)
    await state.set_state(ReminderSetup.time)
    await message.answer("Now send reminder time in 24h format HH:MM (example 18:30)")


@router.message(ReminderSetup.time)
async def process_time(
    message: Message,
    state: FSMContext,
    workout_service: WorkoutService,
) -> None:
    if message.from_user is None:
        await state.clear()
        return

    parsed_time = parse_hhmm(message.text or "")
    if parsed_time is None:
        await message.answer("Invalid time. Use HH:MM, for example 07:45")
        return

    data = await state.get_data()
    offset_minutes = int(data.get("offset_minutes", 0))

    await workout_service.set_reminder(
        telegram_id=message.from_user.id,
        offset_minutes=offset_minutes,
        reminder_time=parsed_time,
    )
    await state.clear()

    await message.answer(
        "✅ Reminder saved\n"
        f"Timezone: {format_utc_offset(offset_minutes)}\n"
        f"Time: {parsed_time.strftime('%H:%M')}"
    )


@router.message(Command("reminder_off"))
async def cmd_reminder_off(message: Message, workout_service: WorkoutService) -> None:
    if message.from_user is None:
        return

    disabled = await workout_service.disable_reminder(message.from_user.id)
    if disabled:
        await message.answer("Reminder disabled.")
        return

    await message.answer("Reminder was not enabled.")
