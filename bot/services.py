"""
Сервисные функции бота
"""
import logging

from aiogram import Bot
from aiogram.types import BotCommand

logger = logging.getLogger(__name__)


async def on_startup(bot: Bot, admins: list):
    """Действия при запуске бота"""

    # Установка команд бота
    await set_default_commands(bot)

    # Уведомление админов
    await notify_admins(bot, admins)

    logger.info("Бот успешно запущен")


async def on_shutdown(bot: Bot):
    """Действия при остановке бота"""
    logger.info("Остановка бота")
    await bot.delete_webhook()
    await bot.session.close()


async def set_default_commands(bot: Bot):
    """Установка команд бота"""
    commands = [
        # Основные
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Вывести справку"),
        BotCommand(command="send_keyboard", description="Показать клавиатуру"),

        # Игры
        BotCommand(command="tictactoe", description="Крестики-нолики"),
        BotCommand(command="rps", description="Камень-ножницы-бумага"),
        BotCommand(command="hangman", description="Виселица"),
        BotCommand(command="guess", description="Угадай число"),

        # Контент
        BotCommand(command="joke", description="Анекдот"),
        BotCommand(command="quote", description="Цитата"),
        BotCommand(command="horoscope", description="Гороскоп"),
        BotCommand(command="fact", description="Интересный факт"),
        BotCommand(command="bigtext", description="Текст из эмодзи"),

        # Социальное
        BotCommand(command="who", description="Кто сегодня [роль]?"),
        BotCommand(command="match", description="Совместимость"),

        # Развлечения
        BotCommand(command="get_fox", description="Фото лисички"),
        BotCommand(command="get_cat", description="Фото котика"),
        BotCommand(command="tts", description="Озвучить текст"),
        BotCommand(command="generate_random", description="Сгенерировать сообщение"),

        # Утилиты
        BotCommand(command="photo_rectangles", description="Обработать фото"),
        BotCommand(command="webapp", description="Открыть Web App"),
    ]
    await bot.set_my_commands(commands)


async def notify_admins(bot: Bot, admins: list):
    """Уведомление админов о запуске"""
    for admin_id in admins:
        try:
            await bot.send_message(int(admin_id), "✅ Бот запущен")
        except Exception as e:
            logger.warning(f"Не удалось уведомить админа {admin_id}: {e}")
