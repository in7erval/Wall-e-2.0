"""
Фильтры для aiogram 3.x
"""
from aiogram import Dispatcher
from aiogram.types import Message


def setup_filters(dp: Dispatcher):
    """Настройка фильтров"""
    # В aiogram 3.x фильтры регистрируются автоматически через роутеры
    pass


class AdminFilter:
    """Фильтр для проверки прав администратора"""

    def __init__(self, admin_ids: list):
        self.admin_ids = [int(uid) for uid in admin_ids]

    async def __call__(self, event: Message) -> bool:
        return event.from_user.id in self.admin_ids
