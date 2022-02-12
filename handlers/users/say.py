import tempfile

from aiogram.types import InputFile
from gtts import gTTS
from aiogram import types
from aiogram.dispatcher.filters import Text, Command

from loader import dp

TEMP_FILE_NAME = "saytemp.ogg"


@dp.message_handler(Command("tts"))
@dp.message_handler(Text(startswith="бот скажи"))
async def bot_say(message: types.Message):
    if message.get_args():
        text = message.get_args()
    else:
        text = message.text
        parts = text.split("бот скажи", 1)
        if len(parts) < 2:
            await message.reply('Нет сообщения для озвучивания')
            return
        text = parts[1]
    if not text or text == '':
        await message.reply('Нет сообщения для озвучивания')
        return
    # fixme: оч плохо!!!!!!!!
    tts = gTTS(text, lang='ru')
    tts.save(TEMP_FILE_NAME)
    await message.reply_voice(
        voice=InputFile('saytemp.ogg')
    )
