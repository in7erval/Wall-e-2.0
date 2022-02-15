from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

keyboard_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Попробовать ещё раз", callback_data="try_rectangles_button")
        ]
    ]
)
