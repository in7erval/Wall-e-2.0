import asyncio
import random

from aiogram import types
from aiogram.dispatcher.filters import Command, Text
from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.markdown import hbold, hitalic, hstrikethrough

from keyboards.default.generate_keyboard import keyboard
from keyboards.inline.generate_inline import keyboard_inline
from loader import dp
from utils.db_api.quick_commands import select_messages_by_chat_id
from utils.misc.generate import generate

MIN_DICT = 10
SMALL = 5
MEDIUM = 15
LARGE = 80


@dp.message_handler(Text(equals='Сгенерировать любое'))
@dp.message_handler(Command('generate_random'))
async def generate_random(message: types.Message):
    text, status = await get_text_random(message,
                                         random.choice([SMALL, MEDIUM, LARGE]))
    await message.delete()
    await message.answer(text=text)


@dp.message_handler(Text(equals='Большой текст'))
@dp.message_handler(Command('generate_large_random'))
async def generate_large_random(message: types.Message):
    text, status = await get_text_random(message, LARGE)
    await message.delete()
    await message.answer(text=text)


@dp.message_handler(Text(equals='Средний текст'))
@dp.message_handler(Command('generate_medium_random'))
async def generate_medium_random(message: types.Message):
    text, status = await get_text_random(message, MEDIUM)
    await message.delete()
    await message.answer(text=text)


@dp.message_handler(Text(equals='Маленький текст'))
@dp.message_handler(Command('generate_small_random'))
async def generate_small_random(message: types.Message):
    text, status = await get_text_random(message, SMALL)
    await message.delete()
    await message.answer(text=text)


@dp.message_handler(Text(equals="Клавиатура для генерации"))
@dp.message_handler(Command('send_keyboard_gen'))
async def get_generate_keyboard(message: types.Message):
    await message.answer(
        text='Клавиатура активирована',
        reply_markup=keyboard
    )
    await message.delete()


@dp.message_handler(Text(equals='Убрать клавиатуру'))
async def delete_generate_keyboard(message: types.Message):
    await message.reply(
        text='Клавиатура скрыта',
        reply_markup=ReplyKeyboardRemove()
    )


@dp.message_handler(Text('Прислать инлайн'))
async def get_inline(message: types.Message):
    await message.delete()
    await message.answer(
        text="Выбери опцию",
        reply_markup=keyboard_inline
    )


@dp.callback_query_handler(text='random')
async def generate_random_inline(call: types.CallbackQuery):
    await call.message.edit_text(
        text=await get_answer_text_inline(call, LARGE),
        reply_markup=keyboard_inline
    )


@dp.callback_query_handler(text='large')
async def generate_random_large_inline(call: types.CallbackQuery):
    await call.message.edit_text(
        text=await get_answer_text_inline(call, LARGE),
        reply_markup=keyboard_inline
    )


@dp.callback_query_handler(text='medium')
async def generate_random_medium_inline(call: types.CallbackQuery):
    await call.message.edit_text(
        text=await get_answer_text_inline(call, MEDIUM),
        reply_markup=keyboard_inline
    )


@dp.callback_query_handler(text='small')
async def generate_random_smallinline(call: types.CallbackQuery):
    await call.message.edit_text(
        text=await get_answer_text_inline(call, SMALL),
        reply_markup=keyboard_inline
    )


async def get_text_random(message: types.Message, size: int = MEDIUM) -> (str, bool):
    id = message.chat.id
    messages = await select_messages_by_chat_id(id)
    messages_text = [m.message for m in messages]
    if len(messages_text) < 10:
        return f"Недостаточно сообщений для обучения. \n" \
               f"Минимум: {hbold(MIN_DICT)}, сейчас: {hbold(len(messages_text))}", False
    await message.answer_chat_action('typing')
    return await generate(messages_text, size), True


async def get_answer_text_inline(call: types.CallbackQuery, size: int):
    await call.message.edit_text(hbold('Сообщение обновляется 🔄, пожалуйста подожди...'))
    text, status = await get_text_random(call.message, size)
    await asyncio.sleep(0.5)
    if not status:
        answer_text = text
    else:
        answer_text = "\n".join([
            'Сгенерированное сообщение:',
            hstrikethrough('- - - - - - - - - - - - - - - - - - - - -'),
            hitalic(text),
            hstrikethrough('- - - - - - - - - - - - - - - - - - - - -'),
            hbold('Try again?')
        ])
    return answer_text
