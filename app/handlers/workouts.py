from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.keyboards.main import (
    TEMPLATE_LABELS,
    TEMPLATE_SUGGESTIONS,
    main_menu_keyboard,
    workout_template_keyboard,
)
from app.services.workout_service import WorkoutService
from app.states.workout import AddWorkout
from app.utils.formatters import format_volume, format_weight
from app.utils.parsers import normalize_optional_text, parse_optional_weight, parse_positive_int

router = Router(name="workouts")


@router.message(Command("add"))
@router.message(F.text == "💪 Add Workout")
async def start_add_workout(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(AddWorkout.template)
    await message.answer(
        "Choose a template for today:",
        reply_markup=workout_template_keyboard(),
    )


@router.callback_query(AddWorkout.template, F.data.startswith("tpl:"))
async def select_template(callback: CallbackQuery, state: FSMContext) -> None:
    raw = callback.data or ""
    template_key = raw.split(":", maxsplit=1)[-1]
    if template_key not in TEMPLATE_LABELS:
        await callback.answer("Unknown template", show_alert=True)
        return

    template_name = TEMPLATE_LABELS[template_key]
    suggestion = TEMPLATE_SUGGESTIONS.get(template_key, "")

    await state.update_data(template=template_name)
    await state.set_state(AddWorkout.exercise)

    prompt = (
        f"Template: <b>{template_name}</b>\n"
        "Now send exercise name (example: Bench Press)."
    )
    if suggestion:
        prompt += f"\nSuggestion: <i>{suggestion}</i>"

    if callback.message is not None:
        await callback.message.edit_text(prompt)
    await callback.answer()


@router.message(AddWorkout.exercise)
async def process_exercise(message: Message, state: FSMContext) -> None:
    if message.text is None:
        await message.answer("Send exercise as text.")
        return

    exercise = normalize_optional_text(message.text, max_len=120)
    if not exercise:
        await message.answer("Exercise cannot be empty. Send a valid name.")
        return

    await state.update_data(exercise=exercise)
    await state.set_state(AddWorkout.sets)
    await message.answer("Sets count? (1-100)")


@router.message(AddWorkout.sets)
async def process_sets(message: Message, state: FSMContext) -> None:
    if message.text is None:
        await message.answer("Send sets as a number.")
        return

    sets = parse_positive_int(message.text, min_value=1, max_value=100)
    if sets is None:
        await message.answer("Invalid number. Send sets as 1-100.")
        return

    await state.update_data(sets=sets)
    await state.set_state(AddWorkout.reps)
    await message.answer("Reps per set? (1-500)")


@router.message(AddWorkout.reps)
async def process_reps(message: Message, state: FSMContext) -> None:
    if message.text is None:
        await message.answer("Send reps as a number.")
        return

    reps = parse_positive_int(message.text, min_value=1, max_value=500)
    if reps is None:
        await message.answer("Invalid number. Send reps as 1-500.")
        return

    await state.update_data(reps=reps)
    await state.set_state(AddWorkout.weight)
    await message.answer("Weight in kg (example 60 or 60.5). Send '-' for bodyweight.")


@router.message(AddWorkout.weight)
async def process_weight(message: Message, state: FSMContext) -> None:
    if message.text is None:
        await message.answer("Send weight as text.")
        return

    ok, weight = parse_optional_weight(message.text)
    if not ok:
        await message.answer("Invalid weight. Send a positive number or '-'.")
        return

    await state.update_data(weight_kg=weight)
    await state.set_state(AddWorkout.notes)
    await message.answer("Any notes? Send '-' to skip.")


@router.message(AddWorkout.notes)
async def process_notes(
    message: Message,
    state: FSMContext,
    workout_service: WorkoutService,
) -> None:
    if message.from_user is None:
        await state.clear()
        return

    notes = normalize_optional_text(message.text or "", max_len=255)
    data = await state.get_data()

    exercise = str(data.get("exercise", "")).strip()
    template = data.get("template")
    sets = int(data.get("sets", 0))
    reps = int(data.get("reps", 0))
    weight_kg = data.get("weight_kg")

    if not exercise or sets <= 0 or reps <= 0:
        await state.clear()
        await message.answer("Workout flow got inconsistent. Please run /add again.")
        return

    workout = await workout_service.create_workout(
        telegram_id=message.from_user.id,
        exercise=exercise,
        sets=sets,
        reps=reps,
        weight_kg=weight_kg,
        template=template,
        notes=notes,
    )

    summary_lines = [
        "✅ <b>Workout saved</b>",
        f"Exercise: {workout.exercise}",
        f"Sets x Reps: {workout.sets} x {workout.reps}",
        f"Weight: {format_weight(workout.weight_kg)}",
    ]

    if workout.volume_kg > 0:
        summary_lines.append(f"Volume: {format_volume(workout.volume_kg)}")
    if workout.template:
        summary_lines.append(f"Template: {workout.template}")
    if workout.notes:
        summary_lines.append(f"Notes: {workout.notes}")

    await state.clear()
    await message.answer("\n".join(summary_lines), reply_markup=main_menu_keyboard())
