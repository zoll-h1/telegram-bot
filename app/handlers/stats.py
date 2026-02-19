from __future__ import annotations

from datetime import datetime, timezone

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, Message

from app.services.workout_service import WorkoutService
from app.utils.formatters import format_volume

router = Router(name="stats")


@router.message(Command("stats"))
@router.message(F.text == "📊 Weekly Stats")
async def cmd_stats(message: Message, workout_service: WorkoutService) -> None:
    if message.from_user is None:
        return

    stats = await workout_service.weekly_stats(message.from_user.id)
    if stats.workouts == 0:
        await message.answer("No workouts in the last 7 days.")
        return

    lines = [
        "<b>Weekly stats (last 7 days)</b>",
        f"Workouts: {stats.workouts}",
        f"Total reps: {stats.total_reps}",
        f"Total volume: {format_volume(stats.total_volume_kg)}",
        f"Most frequent exercise: {stats.top_exercise or '-'}",
    ]
    await message.answer("\n".join(lines))


@router.message(Command("prs"))
@router.message(F.text == "🏆 PRs")
async def cmd_prs(message: Message, workout_service: WorkoutService) -> None:
    if message.from_user is None:
        return

    records = await workout_service.personal_records(message.from_user.id)
    if not records:
        await message.answer("No weighted workouts yet, so no PR table available.")
        return

    lines = ["<b>Personal records (max weight)</b>"]
    for record in records:
        lines.append(f"• {record.exercise}: {record.best_weight_kg:.1f} kg")

    await message.answer("\n".join(lines))


@router.message(Command("export"))
@router.message(F.text == "📤 Export CSV")
async def cmd_export(message: Message, workout_service: WorkoutService) -> None:
    if message.from_user is None:
        return

    csv_bytes = await workout_service.export_csv_bytes(message.from_user.id)
    if csv_bytes is None:
        await message.answer("No data to export yet.")
        return

    date_part = datetime.now(timezone.utc).strftime("%Y%m%d")
    filename = f"workouts_{message.from_user.id}_{date_part}.csv"
    document = BufferedInputFile(csv_bytes, filename=filename)

    await message.answer_document(document, caption="Your workout export is ready.")
