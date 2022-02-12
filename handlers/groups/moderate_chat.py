import asyncio
import datetime
import re

from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.utils.exceptions import BadRequest

from filters import IsGroup, AdminFilter
from loader import dp, bot


@dp.message_handler(IsGroup(), Command("ro", prefixes='!/'), AdminFilter())
async def read_only_mode(message: types.Message):
    """
        !ro
        !ro 5
        !ro 5 test
        и вместо ! - /
    """
    if not message.reply_to_message:
        await message.reply(
            'Ответь на сообщение пользователя'
        )
        return
    member = message.reply_to_message.from_user
    member_id = member.id
    chat_id = message.chat.id
    command_parse = re.compile(r"(!ro|/ro) ?(\d+)? ?([\w+\D]+)?")
    parsed = command_parse.match(message.text)
    time = parsed.group(2)
    comment = parsed.group(3)
    time = 5 if not time else int(time)
    until_date = datetime.datetime.now() + datetime.timedelta(minutes=time)

    ReadOnlyPermissions = types.ChatPermissions(
        can_send_messages=False,
        can_send_media_messages=False,
        can_send_polls=False,
        can_send_other_messages=False,
        can_add_web_page_previews=False,
        can_invite_users=True,
        can_change_info=False,
        can_pin_messages=False
    )
    try:
        await bot.restrict_chat_member(chat_id, user_id=member_id, permissions=ReadOnlyPermissions,
                                       until_date=until_date)
        await message.reply(f"Пользователю {member.get_mention(as_html=True)} "
                            f"запрещено писать {time} минут. По причине: {comment}")
    except BadRequest:
        await message.answer("Пользователь является администратором")
    except Exception as err:
        await message.answer(f"Ошибка: {err.__class__.__name__}: {err}")
    service_message = await message.reply("Сообщение самоуничтожится через 5 секунд.")
    await asyncio.sleep(5)
    await message.delete()
    await service_message.delete()


@dp.message_handler(IsGroup(), Command("unro", prefixes='!/'), AdminFilter())
async def undo_read_only_mode(message: types.Message):
    if not message.reply_to_message:
        await message.reply(
            'Ответь на сообщение пользователя'
        )
        return
    member = message.reply_to_message.from_user
    member_id = member.id

    user_allowed = types.ChatPermissions(
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_polls=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True,
        can_invite_users=True,
        can_change_info=False,
        can_pin_messages=False
    )
    await message.chat.restrict(user_id=member_id, permissions=user_allowed,
                                until_date=0)
    await message.reply(f"Пользователь {member.get_mention(as_html=True)} разбанен")


@dp.message_handler(IsGroup(), Command("ban", prefixes="!/"), AdminFilter())
async def ban_user(message: types.Message):
    if not message.reply_to_message:
        await message.reply(
            'Ответь на сообщение пользователя'
        )
        return
    member = message.reply_to_message.from_user
    if not member:
        await message.answer("Необходимо ответить на сообщение с юзером, которого "
                             "нужно удалить!")
        return
    member_id = member.id
    if member.full_name == 'Wall•e':
        await message.reply(f'Я не могу забанить сам себя')
        return
    await message.chat.kick(user_id=member_id)
    await message.reply(f"Пользователь {member.get_mention(as_html=True)} был забанен")


@dp.message_handler(IsGroup(), Command("unban", prefixes="!/"), AdminFilter())
async def unban_user(message: types.Message):
    if not message.reply_to_message:
        await message.reply(
            'Ответь на сообщение пользователя'
        )
        return
    member = message.reply_to_message.from_user
    if not member:
        await message.answer("Необходимо ответить на сообщение с юзером, которого "
                             "нужно удалить!")
        return
    member_id = member.id
    if member.full_name == 'Wall•e':
        await message.reply(f'Я не могу разбанить сам себя')
        return
    await message.chat.unban(user_id=member_id)
    await message.reply(f"Пользователь {member.get_mention(as_html=True)} был разбанен")


@dp.message_handler(IsGroup(), Command("ro", prefixes='!/'))
@dp.message_handler(IsGroup(), Command("unro", prefixes='!/'))
@dp.message_handler(IsGroup(), Command("ban", prefixes="!/"))
@dp.message_handler(IsGroup(), Command("unban", prefixes="!/"))
async def not_admin(message: types.Message):
    await message.reply(
        'Вы не являетесь администратором данной группы.\n'
        'Попросите одного из администраторов добавить Вас с помощью команды /addadmin'
    )
