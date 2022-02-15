import asyncio
import datetime
import logging
import os
import pathlib
import uuid

from aiogram import types
from aiogram.dispatcher.filters import Command

from loader import dp
from utils.misc.photos.rectangles import process

NAME_FORMAT = '{0}_{1}_{2}.jpg'

DIR = 'temp_images'

ROOT_PATH = pathlib.Path(__file__).parent.resolve().parent.resolve().parent.resolve()


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
    path = ROOT_PATH.joinpath(f'temp_images/{filename}').resolve().absolute()
    logging.debug(f'Path determined as {path}')
    await message.reply_to_message.photo[-1].download(destination_file=path)
    logging.debug(f'Saved {filename}')

    output_file_path, name = await process(str(path), random_palette=True)
    await message.reply_photo(
        photo=output_file_path,
        caption=f"Было использовано {name}"
    )
    await asyncio.sleep(5)
    os.remove(path)
    logging.debug(f'{path} removed')
    os.remove(output_file_path)
    logging.debug(f'{output_file_path} removed')




