"""
Роутер для групповых команд
"""
import logging
from typing import TYPE_CHECKING, Any

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import ChatMemberUpdated, Message

if TYPE_CHECKING:
    from database.repositories import ChatRepository

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("del"))
async def cmd_delete(message: Message):
    """Удаление сообщения по reply"""
    if message.reply_to_message:
        await message.reply_to_message.delete()
        await message.delete()
    else:
        await message.reply(
            'Необходимо ответить на сообщение, которое нужно удалить!'
        )


@router.my_chat_member()
async def on_chat_member_updated(event: ChatMemberUpdated, repos: dict[str, Any]) -> None:
    """Отслеживание добавления/удаления бота из чатов"""
    chat_repo: ChatRepository = repos.get('chat')
    if not chat_repo:
        return

    new_status = event.new_chat_member.status
    chat = event.chat

    if new_status in ('member', 'administrator'):
        # Бот добавлен в чат
        await chat_repo.upsert(
            chat_id=chat.id,
            title=chat.title or str(chat.id),
            chat_type=chat.type
        )
        logger.info(f"[CHAT] Бот добавлен в чат: {chat.title} ({chat.id})")
    elif new_status in ('left', 'kicked'):
        # Бот удалён из чата
        await chat_repo.deactivate(chat.id)
        logger.info(f"[CHAT] Бот удалён из чата: {chat.title} ({chat.id})")
