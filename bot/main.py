"""
Точка входа бота Wall-e 2.0 (aiogram 3.x)
"""
import asyncio
import logging

from aiogram.types import FSInputFile
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from bot import bot, dp, ssl_context
from bot.config import ADMINS, WEBAPP_HOST, WEBHOOK_PATH, WEBHOOK_PORT, WEBHOOK_SSL_CERT, WEBHOOK_URL
from bot.filters import setup_filters
from bot.handlers import register_routers
from bot.middlewares import setup_middlewares
from bot.services import on_shutdown, on_startup
from database import on_startup as db_on_startup

logger = logging.getLogger(__name__)


async def on_bot_startup(**kwargs):
    """Действия при запуске бота"""
    # Инициализация БД
    await db_on_startup()

    # On startup
    await on_startup(bot, ADMINS)

    # Установка webhook с self-signed сертификатом
    await bot.set_webhook(
        url=WEBHOOK_URL,
        certificate=FSInputFile(WEBHOOK_SSL_CERT)
    )
    logger.info(f"Webhook установлен: {WEBHOOK_URL}")


async def on_bot_shutdown(**kwargs):
    """Действия при остановке бота"""
    await on_shutdown(bot)


async def run_webhook():
    """Запуск webhook сервера"""

    # Регистрация роутеров
    register_routers(dp)

    # Настройка фильтров
    setup_filters(dp)

    # Настройка middleware
    setup_middlewares(dp)

    # Регистрация startup/shutdown
    dp.startup.register(on_bot_startup)
    dp.shutdown.register(on_bot_shutdown)

    # Создание aiohttp приложения
    app = web.Application()

    # Стандартный обработчик webhook от aiogram
    webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    # Запуск с SSL
    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(
        runner,
        host=WEBAPP_HOST,
        port=WEBHOOK_PORT,
        ssl_context=ssl_context
    )
    await site.start()

    logger.info(f"Сервер запущен на {WEBAPP_HOST}:{WEBHOOK_PORT}")

    try:
        while True:
            await asyncio.sleep(3600)
    except (asyncio.CancelledError, KeyboardInterrupt):
        await runner.cleanup()


if __name__ == '__main__':
    try:
        asyncio.run(run_webhook())
    except KeyboardInterrupt:
        logger.info("Бот остановлен")
