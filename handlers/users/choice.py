from aiogram import types

from filters.choice_filter import ChoiceFilter
from loader import dp
from utils.misc.random_choice import random_choice


@dp.message_handler(ChoiceFilter())
async def choice(message: types.Message):
    await message.reply(
        text=random_choice(message.text)
    )
