import asyncio
import datetime
import logging
import os
import pathlib
import uuid

from aiogram import types
from aiogram.dispatcher.filters import Command, Text
from aiogram.types import InputFile, InputMediaPhoto, InputMediaDocument

from keyboards.inline.rectangles_inline import keyboard_inline, callback_data
from loader import dp, bot
from utils.db_api.quick_commands import add_rectangle_img, select_rectangle_img_by_id
from utils.misc.photos.rectangles import process

NAME_FORMAT = '{0}_{1}_{2}.jpg'

DIR = 'temp_images'
DEFAULT_FNAME = "YouArePerfect.jpg"

ROOT_PATH = pathlib.Path(__file__).parent.resolve().parent.resolve().parent.resolve()


@dp.message_handler(Command('photo_rectangles'))
async def photo_rectangles(message: types.Message):
    if not message.reply_to_message:
        await message.reply(
            text='Ответь на сообщение с фотографией для обработки'
        )
        return
    if not message.reply_to_message.photo and not message.reply_to_message.document:
        await message.reply(
            text='В отвеченном сообщении нет фотографии'
        )
        return
    path, output_file_path, name = await rectangle_photo(message)
    if message.reply_to_message.photo:
        id = await add_rectangle_img(image_id=message.reply_to_message.photo[-1].file_id)
        await message.reply_photo(
            photo=InputFile(output_file_path, filename=DEFAULT_FNAME),
            caption=f"Было использовано {name}",
            reply_markup=keyboard_inline(id=id)
        )
    else:
        id = await add_rectangle_img(image_id=message.reply_to_message.document.file_id)
        await message.reply_document(
            document=InputFile(output_file_path, filename=DEFAULT_FNAME),
            caption=f"Было использовано {name}",
            reply_markup=keyboard_inline(id=id)
        )
    await asyncio.sleep(5)
    os.remove(path)
    logging.debug(f'{path} removed')
    os.remove(output_file_path)
    logging.debug(f'{output_file_path} removed')


@dp.callback_query_handler(Text(contains='try_rectangles_button'))
async def photo_rectangles_inline(call: types.CallbackQuery):
    logging.debug(f"call: {call}")
    c_data = callback_data.parse(call.data)
    logging.debug(f"call.message.reply_to_message : {call.message.reply_to_message}")
    if not call.message.reply_to_message:
        await call.message.edit_reply_markup(
            reply_markup=None
        )
        await call.message.reply(
            text='Удалено сообщение с командой. Запустите весь процесс заново',
        )
        return
    await call.message.edit_reply_markup(None)
    id = int(c_data.get("id"))
    rectangle_img = await select_rectangle_img_by_id(id=id)
    file_id = rectangle_img.image_id
    path, output_file_path, name = await rectangle_photo_file_id(file_id=file_id, id=call.from_user.id)
    if call.message.photo:
        media = InputMediaPhoto(media=InputFile(output_file_path),
                                caption=f'Было использовано {name}')
    else:
        media = InputMediaDocument(media=InputFile(output_file_path, filename=DEFAULT_FNAME),
                                   caption=f'Было использовано {name}')
    await call.message.edit_media(
        media=media,
        reply_markup=keyboard_inline(id)
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
        await message.reply_to_message.document.download(destination_file=path)
    logging.debug(f'Saved {filename}')

    output_file_path, name = await process(str(path), random_palette=True)
    logging.debug(f'output: {output_file_path}')
    return path, output_file_path, name


async def rectangle_photo_file_id(file_id, id) -> (str, str, str):
    filename = NAME_FORMAT.format(str(id),
                                  hash(uuid.uuid4()),
                                  datetime.datetime.now().isoformat())
    path = ROOT_PATH.joinpath(f'temp_images/{filename}').resolve().absolute()
    logging.debug(f'Path determined as {path}')
    await bot.download_file_by_id(file_id, destination=path)
    logging.debug(f'Saved {filename}')

    output_file_path, name = await process(str(path), random_palette=True)
    logging.debug(f'output: {output_file_path}')
    return path, output_file_path, name
