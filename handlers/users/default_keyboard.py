from aiogram import types
from aiogram.dispatcher.filters import Command, Text

from keyboards.default.default_keyboard import keyboard
from loader import dp


@dp.message_handler(Text(equals='К обычной клавиатуре'))
@dp.message_handler(Command('send_keyboard'))
async def get_generate_keyboard(message: types.Message):
    await message.answer(
        text='Клавиатура активирована',
        reply_markup=keyboard
    )
    await message.delete()
