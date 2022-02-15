from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData


SPACE_CHAR = ' '


callback_data = CallbackData("tictactoe_item", "number", 'mode')

keyboard_inline = lambda mode: InlineKeyboardMarkup(
    row_width=3,
    inline_keyboard=[
        [
            InlineKeyboardButton(text=SPACE_CHAR,
                                 callback_data=callback_data.new(number=0, mode=mode)),
            InlineKeyboardButton(text=SPACE_CHAR,
                                 callback_data=callback_data.new(number=1, mode=mode)),
            InlineKeyboardButton(text=SPACE_CHAR,
                                 callback_data=callback_data.new(number=2, mode=mode)),
        ],
        [
            InlineKeyboardButton(text=SPACE_CHAR,
                                 callback_data=callback_data.new(number=3, mode=mode)),
            InlineKeyboardButton(text=SPACE_CHAR,
                                 callback_data=callback_data.new(number=4, mode=mode)),
            InlineKeyboardButton(text=SPACE_CHAR,
                                 callback_data=callback_data.new(number=5, mode=mode)),
        ],
        [
            InlineKeyboardButton(text=SPACE_CHAR,
                                 callback_data=callback_data.new(number=6, mode=mode)),
            InlineKeyboardButton(text=SPACE_CHAR,
                                 callback_data=callback_data.new(number=7, mode=mode)),
            InlineKeyboardButton(text=SPACE_CHAR,
                                 callback_data=callback_data.new(number=8, mode=mode)),
        ],

    ]

)

callback_data_init = CallbackData("tictactoe_init", "mode", "turn")

keyboard_init = InlineKeyboardMarkup(
    row_width=2,
    inline_keyboard=[
        [
            InlineKeyboardButton(text='С другом',
                                 callback_data=callback_data_init.new(mode='pvp', turn='krest'))
        ],
        [
            InlineKeyboardButton(text='За ❌ с компьютером',
                                 callback_data=callback_data_init.new(mode='pve', turn='krest')),
            InlineKeyboardButton(text='За ⭕️ с компьютером',
                                 callback_data=callback_data_init.new(mode='pve', turn='zero'))
        ]
    ]

)

