import io
from sys import prefix

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, AdminFilter

from filters.group_chat import IsGroup
from loader import dp, bot


@dp.message_handler(IsGroup(), Command("set_photo", prefixes="!/"))
async def set_new_photo(message: types.Message, state: FSMContext):
    source_message = message.reply_to_message
    if not source_message:
        await set_new_photo_form(message, state)
        return
    if not source_message.photo:
        await message.reply(
            'В этом сообщение нет фотографии'
        )
        return
    photo = source_message.photo[-1]
    photo = await photo.download(destination=io.BytesIO())
    input_file = types.InputFile(path_or_bytesio=photo)
    # await bot.set_chat_photo(chat_id=message.chat_id, photo=input_file)
    await message.chat.set_photo(photo=input_file)


async def set_new_photo_form(message: types.Message, state: FSMContext):
    await message.reply('Пришли фотографию')
    await state.set_state('set_photo')


@dp.message_handler(state="set_photo")
async def set_new_photo_form_end(message: types.Message, state: FSMContext):
    if not message.photo and message.text == 'отмена':
        await state.finish()
        await message.reply('Установка фотографии отменена')
        return
    if not message.photo:
        await message.reply('Пришли фотографию или отправь "отмена"!')
        return
    photo = message.photo[-1]
    photo = await photo.download(destination=io.BytesIO())
    input_file = types.InputFile(path_or_bytesio=photo)
    # await bot.set_chat_photo(chat_id=message.chat_id, photo=input_file)
    await message.chat.set_photo(photo=input_file)
    await state.finish()


@dp.message_handler(IsGroup(), Command("set_title", prefixes="!/"))
async def set_new_title(message: types.Message, state: FSMContext):
    source_message = message.reply_to_message
    if not source_message:
        await set_new_photo_form(message, state)
        return
    title = source_message.text
    await message.chat.set_title(title)


async def set_new_title_form(message: types.Message, state: FSMContext):
    await message.reply('Пришли новое название группы')
    await state.set_state('set_title')


@dp.message_handler(state="set_title")
async def set_new_title_form_end(message: types.Message, state: FSMContext):
    if (not message.text or message.text == '') and message.text == 'отмена':
        await state.finish()
        await message.reply('Установка названия группы отменена')
        return
    if not message.text or message.text == '':
        await message.reply('Пришли новое название группы или отправь "отмена"!')
        return
    title = message.text
    await message.chat.set_title(title)
    await state.finish()


@dp.message_handler(IsGroup(), Command("set_description", prefixes="!/"))
async def set_description(message: types.Message, state: FSMContext):
    source_message = message.reply_to_message
    if not source_message:
        await set_new_descr_form(message, state)
        return
    description = source_message.text
    await message.chat.set_description(description)


async def set_new_descr_form(message: types.Message, state: FSMContext):
    await message.reply('Пришли новое описание группы')
    await state.set_state('set_descr')


@dp.message_handler(state="set_descr")
async def set_new_descr_form_end(message: types.Message, state: FSMContext):
    if (not message.text or message.text == '') and message.text == 'отмена':
        await state.finish()
        await message.reply('Установка описания группы отменена')
        return
    if not message.text or message.text == '':
        await message.reply('Пришли новое описание группы или отправь "отмена"!')
        return
    description = message.text
    await message.chat.set_description(description)
    await state.finish()
