from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message

from app.keyboards.main import history_actions_keyboard
from app.services.workout_service import WorkoutService
from app.utils.formatters import format_dt_utc, format_weight

router = Router(name="history")


def _history_text(items: list) -> str:
    if not items:
        return "📭 No workouts yet. Start with /add"

    lines = ["<b>Last workouts</b>"]
    for row in items:
        lines.append(
            "\n"
            f"• {format_dt_utc(row.performed_at)}\n"
            f"  {row.exercise} | {row.sets}x{row.reps} | {format_weight(row.weight_kg)}"
        )
    return "\n".join(lines)


async def _send_history(message: Message, workout_service: WorkoutService) -> None:
    if message.from_user is None:
        return

    rows = await workout_service.recent_workouts(message.from_user.id, limit=10)
    await message.answer(_history_text(rows), reply_markup=history_actions_keyboard())


@router.message(Command("history"))
@router.message(F.text == "📜 History")
async def cmd_history(message: Message, workout_service: WorkoutService) -> None:
    await _send_history(message, workout_service)


@router.callback_query(F.data == "history:refresh")
async def callback_history_refresh(callback: CallbackQuery, workout_service: WorkoutService) -> None:
    if callback.from_user is None or callback.message is None:
        await callback.answer()
        return

    rows = await workout_service.recent_workouts(callback.from_user.id, limit=10)
    try:
        await callback.message.edit_text(_history_text(rows), reply_markup=history_actions_keyboard())
    except TelegramBadRequest as exc:
        if "message is not modified" not in str(exc).lower():
            raise
    await callback.answer("Updated")


@router.callback_query(F.data == "history:delete_last")
async def callback_history_delete_last(callback: CallbackQuery, workout_service: WorkoutService) -> None:
    if callback.from_user is None or callback.message is None:
        await callback.answer()
        return

    deleted = await workout_service.delete_last_workout(callback.from_user.id)
    rows = await workout_service.recent_workouts(callback.from_user.id, limit=10)

    try:
        await callback.message.edit_text(_history_text(rows), reply_markup=history_actions_keyboard())
    except TelegramBadRequest as exc:
        if "message is not modified" not in str(exc).lower():
            raise
    if deleted:
        await callback.answer("Last workout deleted")
        return

    await callback.answer("Nothing to delete", show_alert=True)
