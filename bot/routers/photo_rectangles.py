"""
Роутер для обработки фото прямоугольниками
"""
import asyncio
import datetime
import logging
import os
import pathlib
import uuid

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaDocument,
    InputMediaPhoto,
    Message,
)

from utils.misc.photos.rectangles import process

router = Router()
logger = logging.getLogger(__name__)

NAME_FORMAT = '{0}_{1}_{2}.jpg'
DIR = 'temp_images'
DEFAULT_FNAME = "YouArePerfect.jpg"
ROOT_PATH = pathlib.Path(__file__).parent.resolve().parent.resolve().parent.resolve()


def keyboard_inline(img_id: int) -> InlineKeyboardMarkup:
    """Инлайн-клавиатура 'Попробовать ещё'"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Попробовать ещё", callback_data=f"try_rectangles_{img_id}")]
    ])


@router.message(Command('photo_rectangles'))
async def photo_rectangles(message: Message, repos: dict) -> None:
    """Обработать фото прямоугольниками"""
    if not message.reply_to_message:
        await message.reply("Ответь на сообщение с фотографией для обработки")
        return
    if not message.reply_to_message.photo and not message.reply_to_message.document:
        await message.reply("В отвеченном сообщении нет фотографии")
        return

    path, output_file_path, name = await _download_and_process(message)

    rectangles_repo = repos.get('rectangles')
    if message.reply_to_message.photo:
        img_id = await rectangles_repo.create(image_id=message.reply_to_message.photo[-1].file_id)
        await message.reply_photo(
            photo=FSInputFile(output_file_path, filename=DEFAULT_FNAME),
            caption=f"Было использовано {name}",
            reply_markup=keyboard_inline(img_id)
        )
    else:
        img_id = await rectangles_repo.create(image_id=message.reply_to_message.document.file_id)
        await message.reply_document(
            document=FSInputFile(output_file_path, filename=DEFAULT_FNAME),
            caption=f"Было использовано {name}",
            reply_markup=keyboard_inline(img_id)
        )

    await asyncio.sleep(5)
    _safe_remove(path)
    _safe_remove(output_file_path)


@router.callback_query(F.data.startswith("try_rectangles_"))
async def photo_rectangles_retry(call: CallbackQuery, repos: dict) -> None:
    """Повторная обработка по кнопке"""
    img_id = int(call.data.split("_")[-1])

    if not call.message.reply_to_message:
        await call.message.edit_reply_markup(reply_markup=None)
        await call.message.reply("Удалено сообщение с командой. Запустите процесс заново")
        return

    await call.message.edit_reply_markup(reply_markup=None)

    rectangles_repo = repos.get('rectangles')
    rectangle_img = await rectangles_repo.get_by_id(img_id)
    if not rectangle_img:
        await call.message.reply("Изображение не найдено в базе")
        return

    file_id = rectangle_img.image_id
    path, output_file_path, name = await _process_by_file_id(file_id, call.from_user.id, call.bot)

    if call.message.photo:
        media = InputMediaPhoto(media=FSInputFile(output_file_path), caption=f"Было использовано {name}")
    else:
        media = InputMediaDocument(media=FSInputFile(output_file_path, filename=DEFAULT_FNAME),
                                   caption=f"Было использовано {name}")
    await call.message.edit_media(media=media, reply_markup=keyboard_inline(img_id))

    await asyncio.sleep(5)
    _safe_remove(path)
    _safe_remove(output_file_path)


async def _download_and_process(message: Message) -> tuple[str, str, str]:
    """Скачать фото из reply и обработать"""
    filename = NAME_FORMAT.format(
        message.from_user.id, hash(uuid.uuid4()), datetime.datetime.now().isoformat()
    )
    path = str(ROOT_PATH / DIR / filename)
    logger.debug(f'Path: {path}')

    if message.reply_to_message.photo:
        await message.bot.download(message.reply_to_message.photo[-1], destination=path)
    else:
        await message.bot.download(message.reply_to_message.document, destination=path)

    output_file_path, name = await process(path, random_palette=True)
    return path, output_file_path, name


async def _process_by_file_id(file_id: str, user_id: int, bot) -> tuple[str, str, str]:
    """Скачать по file_id и обработать"""
    filename = NAME_FORMAT.format(
        user_id, hash(uuid.uuid4()), datetime.datetime.now().isoformat()
    )
    path = str(ROOT_PATH / DIR / filename)
    await bot.download(file_id, destination=path)

    output_file_path, name = await process(path, random_palette=True)
    return path, output_file_path, name


def _safe_remove(path: str):
    """Безопасное удаление файла"""
    try:
        if os.path.exists(path):
            os.remove(path)
    except OSError as e:
        logger.warning(f"Не удалось удалить {path}: {e}")
