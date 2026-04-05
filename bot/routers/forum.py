"""
Роутер для работы с Forum Topics (темы в форумах)
Доступно с Telegram Bot API 6.1+
"""

from aiogram import Router
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("createtopic"))
async def cmd_create_topic(message: Message) -> None:
    """
    Создать новую тему в форуме группы

    Использование: /createtopic Название темы
    """
    # Проверяем, что это группа с включенными темами
    if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        await message.reply("❌ Эта команда работает только в группах")
        return

    # Проверяем, есть ли название темы
    topic_name = message.text.split(maxsplit=1)
    if len(topic_name) < 2:
        await message.reply(
            "❌ Укажите название темы\n\n"
            "Пример: /createtopic Обсуждение проекта"
        )
        return

    topic_name = topic_name[1].strip()

    try:
        # Создаём тему
        forum_topic = await message.bot.create_forum_topic(
            chat_id=message.chat.id,
            name=topic_name,
            icon_color=0x6FB9F0  # Голубой цвет (опционально)
        )

        await message.reply(
            f"✅ Тема <b>{topic_name}</b> создана!\n\n"
            f"ID темы: <code>{forum_topic.message_thread_id}</code>\n\n"
            f"Теперь вы можете писать в эту тему."
        )
    except Exception as e:
        await message.reply(
            f"❌ Ошибка при создании темы: {e}\n\n"
            "Убедитесь, что в группе включены темы (Forum Enabled)"
        )


@router.message(Command("closetopic"))
async def cmd_close_topic(message: Message) -> None:
    """
    Закрыть тему в форуме

    Использование: /closetopic (в ответ на сообщение в теме)
    """
    if message.message_thread_id is None:
        await message.reply(
            "❌ Эта команда должна использоваться внутри темы\n\n"
            "Ответьте на сообщение в теме, которую хотите закрыть"
        )
        return

    try:
        await message.bot.close_forum_topic(
            chat_id=message.chat.id,
            message_thread_id=message.message_thread_id
        )
        await message.reply("✅ Тема закрыта")
    except Exception as e:
        await message.reply(f"❌ Ошибка: {e}")


@router.message(Command("opentopic"))
async def cmd_open_topic(message: Message) -> None:
    """
    Открыть закрытую тему в форуме

    Использование: /opentopic (в ответ на сообщение в теме)
    """
    if message.message_thread_id is None:
        await message.reply(
            "❌ Эта команда должна использоваться внутри темы"
        )
        return

    try:
        await message.bot.reopen_forum_topic(
            chat_id=message.chat.id,
            message_thread_id=message.message_thread_id
        )
        await message.reply("✅ Тема открыта")
    except Exception as e:
        await message.reply(f"❌ Ошибка: {e}")


@router.message(Command("deletetopic"))
async def cmd_delete_topic(message: Message) -> None:
    """
    Удалить тему из форума

    Использование: /deletetopic (в ответ на сообщение в теме)
    """
    if message.message_thread_id is None:
        await message.reply(
            "❌ Эта команда должна использоваться внутри темы"
        )
        return

    try:
        await message.bot.delete_forum_topic(
            chat_id=message.chat.id,
            message_thread_id=message.message_thread_id
        )
        await message.reply("✅ Тема удалена")
    except Exception as e:
        await message.reply(f"❌ Ошибка: {e}")


@router.message(Command("edittopic"))
async def cmd_edit_topic(message: Message) -> None:
    """
    Редактировать тему (название, иконку)

    Использование: /edittopic Новое название
    """
    if message.message_thread_id is None:
        await message.reply(
            "❌ Эта команда должна использоваться внутри темы"
        )
        return

    topic_name = message.text.split(maxsplit=1)
    if len(topic_name) < 2:
        await message.reply(
            "❌ Укажите новое название темы\n\n"
            "Пример: /edittopic Обновлённое название"
        )
        return

    topic_name = topic_name[1].strip()

    try:
        await message.bot.edit_forum_topic(
            chat_id=message.chat.id,
            message_thread_id=message.message_thread_id,
            name=topic_name
        )
        await message.reply(f"✅ Название темы изменено на <b>{topic_name}</b>")
    except Exception as e:
        await message.reply(f"❌ Ошибка: {e}")


@router.message(Command("unpinalltopic"))
async def cmd_unpin_all_topic(message: Message) -> None:
    """
    Открепить все закреплённые сообщения в теме

    Использование: /unpinalltopic (в ответ на сообщение в теме)
    """
    if message.message_thread_id is None:
        await message.reply(
            "❌ Эта команда должна использоваться внутри темы"
        )
        return

    try:
        await message.bot.unpin_all_chat_messages(
            chat_id=message.chat.id,
            message_thread_id=message.message_thread_id
        )
        await message.reply("✅ Все закреплённые сообщения откреплены")
    except Exception as e:
        await message.reply(f"❌ Ошибка: {e}")
