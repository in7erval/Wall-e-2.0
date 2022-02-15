from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

callback_data = CallbackData("tictactoe_item", "number")

keyboard_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=".",
                                 callback_data=callback_data.new(number=0)),
            InlineKeyboardButton(text=".",
                                 callback_data=callback_data.new(number=1)),
            InlineKeyboardButton(text=".",
                                 callback_data=callback_data.new(number=2)),
        ],
        [
            InlineKeyboardButton(text=".",
                                 callback_data=callback_data.new(number=3)),
            InlineKeyboardButton(text=".",
                                 callback_data=callback_data.new(number=4)),
            InlineKeyboardButton(text=".",
                                 callback_data=callback_data.new(number=5)),
        ],
        [
            InlineKeyboardButton(text=".",
                                 callback_data=callback_data.new(number=6)),
            InlineKeyboardButton(text=".",
                                 callback_data=callback_data.new(number=7)),
            InlineKeyboardButton(text=".",
                                 callback_data=callback_data.new(number=8)),
        ],

    ]
)

