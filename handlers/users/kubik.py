from aiogram import types
from aiogram.dispatcher.filters import Command, Text

from loader import dp


@dp.message_handler(Text(equals=['бот кинь кубик', 'кинь кубик', '🎲'], ignore_case=True))
async def kubik(message: types.Message):
    if message.text == '🎲':
        await message.delete()
    await message.answer_dice()
