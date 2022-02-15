from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

keyboard_inline = lambda id: InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Попробовать ещё раз",
                                 callback_data=callback_data.new(id=id))
        ]
    ]
)


callback_data = CallbackData("try_rectangles_button", "id")
