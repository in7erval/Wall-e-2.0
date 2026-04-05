"""
Middleware для ограничения частоты запросов (aiogram 3.x)
"""
import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import CallbackQuery, Message


class ThrottlingMiddleware(BaseMiddleware):
    """
    Middleware для throttling (антиспам)
    """

    def __init__(self, rate_limit: float = 1.0):
        self.rate_limit = rate_limit
        self._cache: dict[str, float] = {}

    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: dict[str, Any]
    ) -> Any:
        # Получаем rate_limit из флага хендлера
        rate_limit = get_flag(data, "throttling_rate_limit", default=self.rate_limit)

        # Формируем ключ для кэша
        if isinstance(event, Message):
            key = f"throttle_{event.from_user.id}_{event.chat.id}"
        elif isinstance(event, CallbackQuery):
            key = f"throttle_{event.from_user.id}_{event.message.chat.id if event.message else event.from_user.id}"
        else:
            return await handler(event, data)

        now = asyncio.get_event_loop().time()
        if key in self._cache:
            last_call = self._cache[key]
            if now - last_call < rate_limit:
                return  # Игнорируем слишком частые запросы

        self._cache[key] = now
        return await handler(event, data)
