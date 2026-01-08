from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup

# Create the keyboard object
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="💪 Add Workout"),
            KeyboardButton(text="📜 History")
        ],
        [
            KeyboardButton(text="📊 Stats")
        ]
    ],
    resize_keyboard=True, # Make buttons smaller (compact)
    input_field_placeholder="What are we training today?"
)
# For History
history_inline_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            # text = Что видит user
            # callback_data = Секретный код, который прилетит боту
            InlineKeyboardButton(text="🗑 Delete Last Entry", callback_data="delete_last")
        ]
    ]
)