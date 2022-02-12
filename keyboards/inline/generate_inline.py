from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

keyboard_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Случайный размер", callback_data="random")
        ],
        [
            InlineKeyboardButton(text="Большой", callback_data="large"),
            InlineKeyboardButton(text="Средний", callback_data="medium"),
            InlineKeyboardButton(text="Маленький", callback_data="small"),
        ]
    ]
)
