import logging
import re

from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware

from data.config import banned_users
from utils.db_api.quick_commands import add_message
from utils.misc.in_inline import in_inline

RE_EMOJI = re.compile(
    "(["
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F700-\U0001F77F"  # alchemical symbols
    "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
    "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
    "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
    "\U0001FA00-\U0001FA6F"  # Chess Symbols
    "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
    "\U00002702-\U000027B0"  # Dingbats
    "])"
)


class BigBrother(BaseMiddleware):

    # 1
    async def on_pre_process_update(self, update: types.Update, data: dict):
        logging.debug("[---------------------Новый апдейт!---------------------]")
        logging.debug("1. Pre Process Update")
        logging.debug("Следующая точка: Process Update")
        data["middlewate_data"] = "Это пройдет до on_post_process_update"
        if update.message:
            user = update.message.from_user.id
        elif update.callback_query:
            user = update.callback_query.from_user.id
        else:
            return

        if user in banned_users:
            raise CancelHandler()

    # 2
    async def on_process_update(self, update: types.Update, data: dict):
        logging.debug(f"2. Process Update, {data=}")
        logging.debug("Следующая точка: Pre Process Message")

    # 3
    async def on_pre_process_message(self, message: types.Message, data: dict):
        logging.debug(f"3. Pre Process Message, {data=}")
        logging.debug("Следующая точка: Filters, Process Message")
        data["middleware_data"] = "Это пройдёт в on_process_message"
        if message.text is not None and message.text != '' and not message.text.startswith('/') \
                and not in_inline(message.text) and not RE_EMOJI.match(message.text):
            await add_message(id=message.message_id, chat_id=message.chat.id,
                              name=message.from_user.full_name, message=message.text,
                              person_id=message.from_user.id)

    # 4 Filters

    # 5
    async def on_process_message(self, message: types.Message, data: dict):
        logging.debug(f"5. Process Message")
        logging.debug("Следующая точка: Handler")
        data['middleware_data'] = "Это попадёт в хендлер"

    # 6 Handler

    # 7
    async def on_post_process_message(self, message: types.Message, data_from_handler: list, data: dict):
        logging.debug(f"7. Post Process Message, {data=}, {data_from_handler=}")
        logging.debug("Следующая точка: Post Process Update")

    # 8
    async def on_post_process_update(self, update: types.Update, data_from_handler: list, data: dict):
        logging.debug(f"8. Post Process Update, {data=}, {data_from_handler=}")
        logging.debug("[----------------------Выход----------------------]")

    # async def on_pre_process_callback_query(self, cq: types.CallbackQuery, data: dict):
    #     await cq.answer()
