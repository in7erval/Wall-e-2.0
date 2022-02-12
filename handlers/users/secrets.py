import logging

from aiogram import types
from aiogram.dispatcher.filters import Command

from filters import AdminFilter
from loader import dp, bot

CHAT_ID = -1001335011853


@dp.message_handler(AdminFilter(), Command('send_msg'))
async def send_msg(message: types.Message):
    if not message.get_args() or len(message.get_args().split(maxsplit=1)) != 2:
        await message.reply('Рядом с командой введи id чата и сообщение')
        return
    args = message.get_args().split(maxsplit=1)
    logging.debug(f'input_args: {message.get_args()}, parsed_args: {args}')
    await bot.send_message(args[0].strip(), args[1].strip())
