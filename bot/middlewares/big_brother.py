"""
Middleware для логирования и сохранения сообщений (aiogram 3.x)
"""
import logging
import re
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Update

logger = logging.getLogger(__name__)

# Паттерн для эмодзи
RE_EMOJI = re.compile(
    "(["
    "\U0001F1E0-\U0001F1FF"
    "\U0001F300-\U0001F5FF"
    "\U0001F600-\U0001F64F"
    "\U0001F680-\U0001F6FF"
    "\U0001F700-\U0001F77F"
    "\U0001F780-\U0001F7FF"
    "\U0001F800-\U0001F8FF"
    "\U0001F900-\U0001F9FF"
    "\U0001FA00-\U0001FA6F"
    "\U0001FA70-\U0001FAFF"
    "\U00002702-\U000027B0"
    "])"
)


class BigBrotherMiddleware(BaseMiddleware):
    """
    Outer middleware на уровне Update.
    Сохраняет текстовые сообщения в БД.
    """

    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any]
    ) -> Any:
        message = event.message
        logger.info(f"[BB] Update: msg={'yes' if message else 'no'}, "
                    f"text={message.text[:50] if message and message.text else 'N/A'}, "
                    f"chat={message.chat.type if message else 'N/A'}")
        if message:
            # Трекинг чатов (группы, супергруппы, каналы)
            if message.chat.type in ('group', 'supergroup', 'channel'):
                repos = data.get('repos', {})
                chat_repo = repos.get('chat')
                if chat_repo:
                    try:
                        await chat_repo.upsert(
                            chat_id=message.chat.id,
                            title=message.chat.title or str(message.chat.id),
                            chat_type=message.chat.type
                        )
                    except Exception as e:
                        logger.error(f"[CHAT] Ошибка сохранения чата: {e}")
                        await chat_repo.session.rollback()

            # Сохранение текстовых сообщений
            if message.text:
                text = message.text
                if (not text.startswith('/')
                        and not RE_EMOJI.match(text)):
                    repos = data.get('repos', {})
                    message_repo = repos.get('message')
                    if message_repo:
                        try:
                            await message_repo.create(
                                msg_id=message.message_id,
                                chat_id=message.chat.id,
                                name=message.from_user.full_name or "Unknown",
                                message=text,
                                person_id=message.from_user.id
                            )
                            logger.info(f"[SAVE] Сохранено: {text[:50]}...")
                        except Exception as e:
                            logger.error(f"[SAVE] Ошибка: {e}")
                            await message_repo.session.rollback()

            # Сохранение голосовых сообщений и видеосообщений (кружков)
            if message.voice or message.video_note:
                repos = data.get('repos', {})
                media_repo = repos.get('media')
                if media_repo:
                    try:
                        if message.voice:
                            media = message.voice
                            media_type = 'voice'
                        else:
                            media = message.video_note
                            media_type = 'video_note'

                        await media_repo.create(
                            msg_id=message.message_id,
                            chat_id=message.chat.id,
                            person_id=message.from_user.id,
                            name=message.from_user.full_name or "Unknown",
                            media_type=media_type,
                            file_id=media.file_id,
                            file_unique_id=media.file_unique_id,
                            duration=media.duration,
                            file_size=media.file_size,
                        )
                        logger.info(f"[SAVE] Сохранено {media_type}: "
                                    f"chat={message.chat.id}, user={message.from_user.id}")
                    except Exception as e:
                        logger.error(f"[SAVE] Ошибка сохранения медиа: {e}")
                        await media_repo.session.rollback()

        return await handler(event, data)
