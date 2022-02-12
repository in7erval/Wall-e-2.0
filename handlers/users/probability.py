from aiogram import types
from aiogram.dispatcher.filters import Text

from loader import dp
from utils.misc.random_probabilty import random_probability


@dp.message_handler(Text(startswith=['бот насколько', 'насколько',
                                     'на сколько', 'бот на сколько'],
                         ignore_case=True))
async def probability(message: types.Message):
    await message.reply(
        text=random_probability(message.text.lower())
    )
