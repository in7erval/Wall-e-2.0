import logging

from aiogram import types
from aiogram.dispatcher.filters import Command, Text

from keyboards.inline.tictactoe_inline import keyboard_inline, callback_data
from loader import dp


@dp.message_handler(Command('tictactoe'))
async def tictactoe_init(message: types.Message):
    await message.answer(
        text=".",
        reply_markup=keyboard_inline
    )


@dp.callback_query_handler(Text(contains='tictactoe_item'))
async def photo_rectangles_inline(call: types.CallbackQuery):
    c_data = callback_data.parse(call.data)
    number = int(c_data.get("number"))
    reply_markup = call.message.reply_markup
    logging.debug(f"number: {number}")
    logging.debug(f"reply_markup: {reply_markup}")
    logging.debug(f"reply_markup.inline_keyboard: {reply_markup.inline_keyboard}")
    await call.message.edit_reply_markup(
        reply_markup=keyboard_inline
    )



