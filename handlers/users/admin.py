import logging

from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.types import InputFile
from aiogram.utils.markdown import hbold
from asyncpg import UniqueViolationError

from data.config import ADMINS
from filters import AdminFilter
from loader import dp
from utils.db_api.quick_commands import select_all_messages, select_messages_by_chat_id, select_user, add_user, \
    update_user_admin, select_all_admins

FORMAT = "{},{},{},{},{},{},{}\n"


@dp.message_handler(Command('send_history'), user_id=ADMINS)
async def admin_send_history(m: types.Message):
    if m.get_args():
        arg = m.get_args()
        if arg == 'all':
            messages = await get_messages()
        elif arg.isnumeric():
            messages = await get_messages(int(arg))
        else:
            await m.reply("Неправильный формат id")
            return
    else:
        messages = await get_messages(m.chat.id)
    temp = open("history.csv", 'w+')
    temp.write('id,chat_id,name,message,person_id,created_at,updated_at\n')
    for message in messages:
        temp.write(FORMAT.format(
            message.id, message.chat_id, message.name, message.message,
            message.person_id, message.created_at, message.updated_at)
        )
    temp.close()
    await m.answer_document(
        document=InputFile("history.csv")
    )


async def get_messages(id: int = None):
    if not id:
        messages = await select_all_messages()
    else:
        messages = await select_messages_by_chat_id(id)
    return messages


@dp.message_handler(AdminFilter(), Command('addadmin'))
async def add_admin(message: types.Message):
    source_message = message.reply_to_message
    if not source_message:
        await message.reply(
            'Необходимо ответить на сообщение пользователя, '
            'которого хотите назначить администратором'
        )
        return
    user = source_message.from_user
    try:
        try:
            await add_user(user.id, user.full_name, True)
        except UniqueViolationError:
            logging.error(f'Пользователя ({user.id}){user.full_name} не получилось добавить в базу. Пробуем обновить')
            await update_user_admin(user.id, True)
    except Exception as err:
        logging.error(err)
        await message.reply(f'Ошибка при добавлении')
    await message.reply(f'Пользователь {hbold(user.full_name)} назначен администратором')


@dp.message_handler(AdminFilter(), Command('deladmin'))
async def del_admin(message: types.Message):
    source_message = message.reply_to_message
    if not source_message:
        await message.reply(
            'Необходимо ответить на сообщение пользователя, '
            'которого хотите убрать из администраторов'
        )
        return
    user = source_message.from_user
    try:
        try:
            await add_user(user.id, user.full_name, False)
        except UniqueViolationError:
            logging.error(f'Пользователя ({user.id}){user.full_name} не получилось добавить в базу. Пробуем обновить')
            await update_user_admin(user.id, False)
    except Exception as err:
        logging.error(err)
        await message.reply(f'Ошибка при удалении')
    await message.reply(f'Пользователь {hbold(user.full_name)} больше не администратор')


@dp.message_handler(Command('getadmins'))
async def get_admins(message: types.Message):
    users = await select_all_admins()
    text = 'Следующие пользователи являются администраторами:\n' + \
           "\n".join(
               [user.name for user in users]
           )
    await message.reply(text=text)


@dp.message_handler(Command('addadmin'))
@dp.message_handler(Command('deladmin'))
async def not_admin(message: types.Message):
    await message.reply(
        'Вы не являетесь администратором данной группы.\n'
        'Попросите одного из администраторов добавить Вас с помощью команды /addadmin'
    )
