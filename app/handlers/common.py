from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from app.keyboards.main import main_menu_keyboard
from app.services.workout_service import WorkoutService

router = Router(name="common")


WELCOME_TEXT = (
    "🏋️ <b>Gym Progress Coach</b>\n"
    "Track workouts, review stats, and stay consistent.\n\n"
    "Use menu buttons or commands below to start."
)

HELP_TEXT = (
    "<b>Commands</b>\n"
    "/start - Open bot menu\n"
    "/add - Add workout entry\n"
    "/history - Last workout logs\n"
    "/stats - Weekly summary\n"
    "/prs - Personal records by weight\n"
    "/export - Download CSV\n"
    "/reminder - Setup daily reminder\n"
    "/reminder_off - Disable reminder\n"
    "/cancel - Cancel current flow"
)


@router.message(Command("start"))
async def cmd_start(message: Message, workout_service: WorkoutService) -> None:
    if message.from_user is None:
        return

    await workout_service.ensure_profile(message.from_user.id)
    await message.answer(WELCOME_TEXT, reply_markup=main_menu_keyboard())


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT)


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext) -> None:
    if await state.get_state() is None:
        await message.answer("No active flow.", reply_markup=main_menu_keyboard())
        return

    await state.clear()
    await message.answer("Current action cancelled.", reply_markup=main_menu_keyboard())


@router.message(F.text == "🏠 Menu")
async def text_menu(message: Message) -> None:
    await message.answer("Menu opened.", reply_markup=main_menu_keyboard())
