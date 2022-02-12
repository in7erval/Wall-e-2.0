from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.utils.markdown import hlink, hbold, hcode, hitalic, hpre, hspoiler, hstrikethrough, hunderline, hide_link

from loader import dp

html_text = "\n".join([
    hbold("Жирный") + " текст",
    hitalic("Курсивный") + " текст",
    hspoiler("Спойлер") + " текст",
    hcode("print('Hello world!')") + " инлайн-код",
    hpre("print('Hello world!')") + " код",
    hunderline("Подчеркнутый") + " текст",
    hstrikethrough("Зачеркнутый") + " текст",
    hlink("Ссылка", "https://in7erval.github.io"),
    hide_link("https://in7erval.github.io") + " а тут скрытая ссылочка"
])


@dp.message_handler(Command("parse_mode_html"))
async def show_parse_mode(message: types.Message):
    await message.answer(html_text)
