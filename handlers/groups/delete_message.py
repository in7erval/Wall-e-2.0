from aiogram import types
from aiogram.dispatcher.filters import Command

from filters.group_chat import IsGroup
from loader import dp


@dp.message_handler(IsGroup(), Command("del"))
async def delete_message(m: types.Message):
    if m.reply_to_message:
        await m.reply_to_message.delete()
        await m.delete()
    else:
        await m.reply(
            'Необходимо ответить на сообщение, которое нужно удалить!'
        )
