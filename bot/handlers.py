"""
Регистрация роутеров
"""
from aiogram import Dispatcher

from bot.routers import (
    admin,
    content,
    entertainment,
    games,
    groups,
    photo_rectangles,
    reactions,
    users,
)


def register_routers(dp: Dispatcher):
    """Регистрация всех роутеров"""
    dp.include_router(users.router)
    dp.include_router(groups.router)
    dp.include_router(admin.router)
    dp.include_router(reactions.router)
    dp.include_router(entertainment.router)
    dp.include_router(games.router)
    dp.include_router(content.router)
    dp.include_router(photo_rectangles.router)
