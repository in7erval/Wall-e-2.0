"""
Middleware для aiogram 3.x
"""
from aiogram import Dispatcher

from bot.middlewares.big_brother import BigBrotherMiddleware
from bot.middlewares.throttling import ThrottlingMiddleware
from database.middleware import RepositoryMiddleware


def setup_middlewares(dp: Dispatcher):
    """Настройка middleware"""
    # Outer middleware вызывается для ВСЕХ апдейтов (даже без хендлера)
    dp.update.outer_middleware(RepositoryMiddleware())
    dp.update.outer_middleware(BigBrotherMiddleware())
    # Inner middleware — только когда есть подходящий хендлер
    dp.message.middleware(ThrottlingMiddleware())
