import asyncio
import datetime
import logging
import os
import pathlib
import uuid

from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.types import InputFile, InputMediaPhoto

from keyboards.inline.rectangles_inline import keyboard_inline
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
    elif not message.reply_to_message.photo:
        await message.reply(
            text='В отвеченном сообщении нет фотографии'
        )
        return
    elif not message.photo:
        await message.reply(
            text='Пришлите фото с командой или ответьте командой на сообщение с фотографией'
        )
        return
    path, output_file_path, name = await rectangle_photo(message)

    await message.reply_photo(
        photo=InputFile(output_file_path),
        caption=f"Было использовано {name}"
        # ,
        # reply_markup=keyboard_inline
    )
    await asyncio.sleep(5)
    os.remove(path)
    logging.debug(f'{path} removed')
    os.remove(output_file_path)
    logging.debug(f'{output_file_path} removed')


@dp.callback_query_handler(text='try_rectangles_button')
async def photo_rectangles_inline(call: types.CallbackQuery):
    logging.debug(f"call: {call}")
    logging.debug(f"call.message.reply_to_message : {call.message.reply_to_message}")
    if not call.message.reply_to_message:
        await call.message.edit_reply_markup(
            reply_markup=None
        )
        await call.message.reply(
            text='Удалено сообщение с командой. Запустите весь процесс заново',
        )
        return
    logging.debug(f"call.message.reply_to_message.reply_to_message : {call.message.reply_to_message.reply_to_message}")
    if not call.message.reply_to_message.reply_to_message:
        await call.message.edit_reply_markup(
            reply_markup=None
        )
        await call.message.reply(
            text='Удалено сообщение с фотографией. Запустите весь процесс заново'
        )
        return
    path, output_file_path, name = await rectangle_photo(call.message.reply_to_message.reply_to_message)
    await call.message.edit_media(
        media=InputMediaPhoto(media=InputFile(output_file_path),
                              caption=f'Было использовано {name}'),
        reply_markup=keyboard_inline
    )

    await asyncio.sleep(5)
    os.remove(path)
    logging.debug(f'{path} removed')
    os.remove(output_file_path)
    logging.debug(f'{output_file_path} removed')


async def rectangle_photo(message: types.Message) -> (str, str, str):
    filename = NAME_FORMAT.format(str(message.from_user.id),
                                  hash(uuid.uuid4()),
                                  datetime.datetime.now().isoformat())
    path = ROOT_PATH.joinpath(f'temp_images/{filename}').resolve().absolute()
    logging.debug(f'Path determined as {path}')
    if message.reply_to_message.photo:
        await message.reply_to_message.photo[-1].download(destination_file=path)
    else:
        await message.photo[-1].download(destination_file=path)
    logging.debug(f'Saved {filename}')

    output_file_path, name = await process(str(path), random_palette=True)
    logging.debug(f'output: {output_file_path}')
    return path, output_file_path, name
