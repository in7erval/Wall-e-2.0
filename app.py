import logging

from aiogram.utils.executor import start_webhook

import filters
import handlers
import middlewares
from data.config import ADMINS, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT, WEBHOOK_URL
from loader import dp, db, ssl_context, bot, SSL_CERT
from utils.db_api import db_gino
from utils.db_api.quick_commands import add_user, update_user_admin
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    logging.info("Подключаем бд")
    await db_gino.on_startup(dispatcher)
    logging.info("Готово")

    # logging.info("Чистим базу")
    # await db.gino.drop_all()
    # logging.info("Готово")

    logging.info("Создаем таблицы")
    await db.gino.create_all()
    logging.info("Готово")

    logging.info("Загружаем админов в базу")
    for admin in ADMINS:
        try:
            try:
                await add_user(int(admin), "", is_admin=True)
            except Exception:
                await update_user_admin(int(admin), True)
        except Exception as err:
            logging.error('Ошибка при загрузке админов')
            logging.error(err)
    logging.info("Готово")

    # закомментируй для использования by LongPolling
    await bot.set_webhook(
        url=WEBHOOK_URL,
        certificate=SSL_CERT
    )

    # Рассылка админам о запуске бота
    await on_startup_notify(dispatcher)

    # Дефолтные команды бота, которые будут показываться в Telegram
    await set_default_commands(dispatcher)


if __name__ == '__main__':
    # # Расскомментируй это для использования by LongPolling и закомментируй вебхуки
    # executor.start_polling(dp,
    #                        on_startup=on_startup,
    #                        skip_updates=True)
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
        ssl_context=ssl_context
    )
    __all__ = ['middlewares', 'filters', 'handlers']
