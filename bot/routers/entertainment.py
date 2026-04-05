"""
Роутер для развлечений: генерация текста, котики, лисички, TTS, вероятность, бутерброд, кубик, выбор
"""
import os
import random
import tempfile
from typing import TYPE_CHECKING, Any

import aiohttp
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import FSInputFile, Message
from aiogram.utils.markdown import hbold

from utils.misc.generate import generate as markov_generate
from utils.misc.random_choice import random_choice
from utils.misc.random_probabilty import random_probability

if TYPE_CHECKING:
    from database.repositories import MessageRepository

router = Router()

# Константы для генерации
MIN_DICT = 10
SMALL = 5
MEDIUM = 15
LARGE = 80

# API URL
FOX_API_URL = "http://randomfox.ca/floof/"
CAT_API_URL = "https://api.thecatapi.com/v1/images/search"


async def get_text_random(message: Message, size: int = MEDIUM, repos: dict | None = None) -> tuple[str, bool]:
    """Генерация случайного текста из сообщений чата (цепи Маркова)"""
    chat_id = message.chat.id

    # Получаем сообщения из БД
    message_repo: MessageRepository = repos.get('message') if repos else None
    if message_repo:
        messages = await message_repo.get_by_chat_id(chat_id)
        messages_text = [m.message for m in messages]
    else:
        messages_text = []

    if len(messages_text) < MIN_DICT:
        return (
            f"Недостаточно сообщений для обучения.\n"
            f"Минимум: {hbold(MIN_DICT)}, сейчас: {hbold(len(messages_text))}",
            False
        )

    # Генерация по цепям Маркова
    text = markov_generate(messages_text, length=size)
    if not text:
        return "Не удалось сгенерировать текст. Попробуйте позже.", False

    return text[:4000], True


@router.message(Command('generate_random'))
@router.message(F.text == "Сгенерировать любое")
async def cmd_generate_random(message: Message, repos: dict[str, Any]) -> None:
    """Сгенерировать случайное сообщение"""
    await message.delete()
    text, _status = await get_text_random(message, random.choice([SMALL, MEDIUM, LARGE]), repos)
    await message.answer(text=text)


@router.message(Command('generate_large_random'))
@router.message(F.text == "Большой текст")
async def cmd_generate_large_random(message: Message, repos: dict[str, Any]) -> None:
    """Сгенерировать большое сообщение"""
    await message.delete()
    text, _status = await get_text_random(message, LARGE, repos)
    await message.answer(text=text)


@router.message(Command('generate_medium_random'))
@router.message(F.text == "Средний текст")
async def cmd_generate_medium_random(message: Message, repos: dict[str, Any]) -> None:
    """Сгенерировать среднее сообщение"""
    await message.delete()
    text, _status = await get_text_random(message, MEDIUM, repos)
    await message.answer(text=text)


@router.message(Command('generate_small_random'))
@router.message(F.text == "Маленький текст")
async def cmd_generate_small_random(message: Message, repos: dict[str, Any]) -> None:
    """Сгенерировать маленькое сообщение"""
    await message.delete()
    text, _status = await get_text_random(message, SMALL, repos)
    await message.answer(text=text)


@router.message(Command("get_fox"))
async def cmd_get_fox(message: Message) -> None:
    """Прислать случайное фото лисички"""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(FOX_API_URL) as response:
                if response.status != 200:
                    await message.reply("❌ Не удалось получить фото лисички. Попробуйте позже.")
                    return
                data = await response.json()
                photo_url = data.get("image")
                if photo_url:
                    await message.answer_photo(photo=photo_url)
                else:
                    await message.reply("❌ Неверный формат ответа от API.")
        except Exception as e:
            await message.reply(f"❌ Ошибка: {e}")


@router.message(Command("get_cat"))
async def cmd_get_cat(message: Message) -> None:
    """Прислать случайное фото котика"""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(CAT_API_URL) as response:
                if response.status != 200:
                    await message.reply("❌ Не удалось получить фото котика. Попробуйте позже.")
                    return
                data = await response.json()
                if data and isinstance(data, list) and len(data) > 0:
                    photo_url = data[0].get("url")
                    if photo_url:
                        await message.answer_photo(photo=photo_url)
                    else:
                        await message.reply("❌ Неверный формат ответа от API.")
                else:
                    await message.reply("❌ Неверный формат ответа от API.")
        except Exception as e:
            await message.reply(f"❌ Ошибка: {e}")


@router.message(Command("tts"))
@router.message(F.text.casefold().startswith("бот скажи"))
async def cmd_tts(message: Message) -> None:
    """Озвучить текст (Text-to-Speech)"""
    from gtts import gTTS

    text = None

    # /tts <текст>
    if message.text and message.text.startswith("/tts"):
        parts = message.text.split(maxsplit=1)
        if len(parts) > 1:
            text = parts[1]

    # "бот скажи <текст>"
    if not text and message.text and "бот скажи" in message.text.lower():
        parts = message.text.lower().split("бот скажи", 1)
        if len(parts) > 1 and parts[1].strip():
            text = parts[1].strip()

    # reply на сообщение
    if not text and message.reply_to_message and message.reply_to_message.text:
        text = message.reply_to_message.text

    if not text:
        await message.reply("Нет текста для озвучивания.\nИспользование: /tts <текст>")
        return

    tmp_path = None
    try:
        text = text[:500]
        tts = gTTS(text, lang='ru')
        with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as f:
            tmp_path = f.name
            tts.save(tmp_path)
        await message.reply_voice(voice=FSInputFile(tmp_path))
    except Exception as e:
        await message.reply(f"Ошибка при озвучивании: {e}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


# --- Вероятность ---

@router.message(F.text.casefold().startswith("бот насколько"))
@router.message(F.text.casefold().startswith("насколько"))
@router.message(F.text.casefold().startswith("на сколько"))
@router.message(F.text.casefold().startswith("бот на сколько"))
async def probability(message: Message) -> None:
    """Бот, насколько я крутой?"""
    result = random_probability(message.text.lower())
    if result:
        await message.reply(text=result)


# --- Кубик ---

@router.message(F.text.casefold().in_({"бот кинь кубик", "кинь кубик", "🎲"}))
async def kubik(message: Message) -> None:
    """Бросить кубик"""
    if message.text == '🎲':
        await message.delete()
    await message.answer_dice()


# --- Выбор ---

@router.message(F.text.casefold().startswith("бот"), F.text.contains(" или "))
async def choice(message: Message) -> None:
    """Бот, А или Б?"""
    result = random_choice(message.text)
    if result:
        await message.reply(text=result)


# --- Бутерброд ---

class ButterbrodState(StatesGroup):
    waiting = State()


START_BUTER_ID = "CAACAgIAAx0CT5KqDQACKfZey-lqcAABF5W6DVtvX6jzk_FVD8wAAh0EAAJa44oXaJW1lB4mzXcZBA"
END_BUTER_ID = "CAACAgIAAx0CT5KqDQACKfdey-ls5ffNFol-9PjTjr9qCEc_0QACFgQAAlrjihftOsVOK2ZRqRkE"


@router.message(F.text.casefold() == "бутерброд")
@router.message(F.text.contains("🥪"))
async def buterbrod(message: Message, state: FSMContext) -> None:
    """Бутерброд!"""
    await message.answer_sticker(sticker=START_BUTER_ID)
    await state.set_state(ButterbrodState.waiting)


@router.message(ButterbrodState.waiting)
async def buterbrod_end(message: Message, state: FSMContext) -> None:
    """Завершить бутерброд"""
    await message.answer_sticker(sticker=END_BUTER_ID)
    await state.clear()
