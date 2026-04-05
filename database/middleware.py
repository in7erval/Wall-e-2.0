"""
Dependency injection для репозиториев
"""
import logging
from functools import wraps

from aiogram import BaseMiddleware

from database import async_session_maker
from database.repositories import (
    ChatRepository,
    InlinePhotoRepository,
    MessageRepository,
    RectanglesImgRepository,
    UserRepository,
)

logger = logging.getLogger(__name__)


class RepositoryMiddleware(BaseMiddleware):
    """Middleware для добавления репозиториев в data"""

    async def __call__(self, handler, event, data):
        logger.debug(f"RepositoryMiddleware: добавляем repos для {type(event).__name__}")
        try:
            # Создаём сессию и репозитории
            async with async_session_maker() as session:
                data['repos'] = {
                    'user': UserRepository(session),
                    'message': MessageRepository(session),
                    'photo': InlinePhotoRepository(session),
                    'rectangles': RectanglesImgRepository(session),
                    'chat': ChatRepository(session),
                }
                data['session'] = session
                logger.debug(f"RepositoryMiddleware: repos={list(data['repos'].keys())}")
                return await handler(event, data)
        except Exception as e:
            logger.error(f"RepositoryMiddleware error: {e}")
            # Продолжаем обработку даже если репозитории не доступны
            return await handler(event, data)


def with_repository(handler_func):
    """
    Декоратор для получения репозиториев в хендлере

    Пример использования:
        @router.message(Command('start'))
        @with_repository
        async def cmd_start(message: Message, repos: dict):
            user_repo = repos['user']
            user = await user_repo.get(message.from_user.id)
    """
    @wraps(handler_func)
    async def wrapper(message, **kwargs):
        async with async_session_maker() as session:
            repos = {
                'user': UserRepository(session),
                'message': MessageRepository(session),
                'photo': InlinePhotoRepository(session),
                'rectangles': RectanglesImgRepository(session),
                'chat': ChatRepository(session),
            }
            return await handler_func(message, repos=repos, **kwargs)
    return wrapper
