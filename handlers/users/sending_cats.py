import json
import logging

import requests
from aiogram import types
from aiogram.dispatcher.filters import Command, Text

from loader import dp


@dp.message_handler(Text(equals='🦊'))
@dp.message_handler(Command("get_fox"))
async def send_fox(message: types.Message):
    if message.text == '🦊':
        await message.delete()
    logging.info("Into send_fox")
    url = "http://randomfox.ca/floof/"
    contents = requests.get(url, verify=False).content
    logging.info(f"contents = {contents}")
    parsed_contents = json.loads(contents)
    logging.info(f"parsed_contents = {parsed_contents}")
    photo_url = parsed_contents["image"]
    logging.info(f"photo_url = {photo_url}")
    await message.answer_photo(
        photo=photo_url
    )


@dp.message_handler(Text(equals='🐱'))
@dp.message_handler(Command("get_cat"))
async def send_cat(message: types.Message):
    if message.text == '🐱':
        await message.delete()
    logging.info("Into send_cat")
    url = "https://api.thecatapi.com/v1/images/search"
    contents = requests.get(url, verify=False).content
    logging.info(f"contents = {contents}")
    parsed_contents = json.loads(contents)
    logging.info(f"parsed_contents = {parsed_contents}")
    photo_url = parsed_contents[0]["url"]
    logging.info(f"photo_url = {photo_url}")
    await message.answer_photo(
        photo=photo_url
    )
