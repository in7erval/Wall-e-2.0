"""
Точка входа бота Wall-e 2.0 (aiogram 3.x)
"""
import asyncio
import logging
import ssl
from pathlib import Path

from aiogram.types import FSInputFile
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from bot import bot, dp, ssl_context
from bot.config import ADMINS, WEBAPP_HOST, WEBHOOK_PATH, WEBHOOK_PORT, WEBHOOK_SSL_CERT, WEBHOOK_URL
from bot.filters import setup_filters
from bot.handlers import register_routers
from bot.middlewares import setup_middlewares
from bot.services import on_shutdown, on_startup
from bot.web_api import setup_api_routes
from database import on_startup as db_on_startup

logger = logging.getLogger(__name__)

# Путь к директории web_app
WEB_APP_DIR = Path(__file__).parent.parent / "web_app"

# Let's Encrypt сертификаты для Web App (порт 443)
LE_CERT = Path("/etc/letsencrypt/live/walle-bot.duckdns.org/fullchain.pem")
LE_KEY = Path("/etc/letsencrypt/live/walle-bot.duckdns.org/privkey.pem")
WEBAPP_PORT = 443


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

    # === Webhook приложение (порт 8443, self-signed SSL) ===
    app = web.Application()
    webhook_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    runner = web.AppRunner(app)
    await runner.setup()
    webhook_site = web.TCPSite(runner, host=WEBAPP_HOST, port=WEBHOOK_PORT, ssl_context=ssl_context)
    await webhook_site.start()
    logger.info(f"Webhook сервер запущен на {WEBAPP_HOST}:{WEBHOOK_PORT}")

    # === Web App (порт 443, Let's Encrypt SSL) ===
    webapp_runner = None
    if LE_CERT.exists() and LE_KEY.exists() and WEB_APP_DIR.exists():
        le_ssl = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        le_ssl.load_cert_chain(str(LE_CERT), str(LE_KEY))

        webapp_app = web.Application()

        # API endpoints
        setup_api_routes(webapp_app)

        # Раздача статики
        webapp_app.router.add_get("/", lambda r: web.HTTPFound("/webapp/index.html"))
        webapp_app.router.add_get("/webapp", lambda r: web.HTTPFound("/webapp/index.html"))
        webapp_app.router.add_static("/webapp/", path=str(WEB_APP_DIR), name="webapp")

        webapp_runner = web.AppRunner(webapp_app)
        await webapp_runner.setup()
        webapp_site = web.TCPSite(webapp_runner, host=WEBAPP_HOST, port=WEBAPP_PORT, ssl_context=le_ssl)
        await webapp_site.start()
        logger.info("Web App запущен на https://walle-bot.duckdns.org/webapp/")
    else:
        logger.warning("Let's Encrypt сертификаты не найдены, Web App не запущен")

    try:
        while True:
            await asyncio.sleep(3600)
    except (asyncio.CancelledError, KeyboardInterrupt):
        await runner.cleanup()
        if webapp_runner:
            await webapp_runner.cleanup()


if __name__ == '__main__':
    try:
        asyncio.run(run_webhook())
    except KeyboardInterrupt:
        logger.info("Бот остановлен")
