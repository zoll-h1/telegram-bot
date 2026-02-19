from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

TEMPLATE_LABELS = {
    "push": "Push Day",
    "pull": "Pull Day",
    "legs": "Leg Day",
    "full": "Full Body",
    "custom": "Custom",
}

TEMPLATE_SUGGESTIONS = {
    "push": "Bench Press",
    "pull": "Barbell Row",
    "legs": "Back Squat",
    "full": "Deadlift",
    "custom": "Any exercise you want",
}


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="💪 Add Workout"),
                KeyboardButton(text="📜 History"),
            ],
            [
                KeyboardButton(text="📊 Weekly Stats"),
                KeyboardButton(text="🏆 PRs"),
            ],
            [
                KeyboardButton(text="📤 Export CSV"),
                KeyboardButton(text="⏰ Set Reminder"),
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder="Track your next session",
    )


def workout_template_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Push", callback_data="tpl:push"),
                InlineKeyboardButton(text="Pull", callback_data="tpl:pull"),
            ],
            [
                InlineKeyboardButton(text="Legs", callback_data="tpl:legs"),
                InlineKeyboardButton(text="Full Body", callback_data="tpl:full"),
            ],
            [InlineKeyboardButton(text="Custom", callback_data="tpl:custom")],
        ]
    )


def history_actions_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🗑 Delete Last", callback_data="history:delete_last"),
                InlineKeyboardButton(text="🔄 Refresh", callback_data="history:refresh"),
            ]
        ]
    )
