import datetime
import logging
import pathlib
import uuid

from aiogram import types
from aiogram.dispatcher.filters import Command

from loader import dp
from utils.misc.photos.rectangles import process

NAME_FORMAT = '{0}_{1}_{2}.jpg'

DIR = 'temp_images'

ROOT_PATH = pathlib.Path(__file__).parent.resolve().parent.resolve()


@dp.message_handler(Command('photo_rectangles'))
async def photo_rectangles(message: types.Message):
    if not message.reply_to_message:
        await message.reply(
            text='Ответь на сообщение с фотографией для обработки'
        )
        return
    if not message.reply_to_message.photo:
        await message.reply(
            text='В отвеченном сообщении нет фотографии'
        )
        return
    filename = NAME_FORMAT.format(str(message.from_user.id),
                                  hash(uuid.uuid4()),
                                  datetime.datetime.now().isoformat())
    await message.reply_to_message.photo[-1].download(destination_file=filename)
    logging.info(f'Saved {filename}')
    path = ROOT_PATH.joinpath(f'temp_images/{filename}').resolve()
    logging.info(f'Path determined as {path}')
    output_file_path, name = await process(str(path), random_palette=True)
    await message.reply_photo(
        photo=output_file_path,
        caption=f"Было использовано {name}"
    )



