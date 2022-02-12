from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from loader import dp

START_BUTER_ID = "CAACAgIAAx0CT5KqDQACKfZey-lqcAABF5W6DVtvX6jzk_FVD8wAAh0EAAJa44oXaJW1lB4mzXcZBA"
END_BUTER_ID = "CAACAgIAAx0CT5KqDQACKfdey-ls5ffNFol-9PjTjr9qCEc_0QACFgQAAlrjihftOsVOK2ZRqRkE"


@dp.message_handler(Text(equals=['бутерброд'], ignore_case=True))
@dp.message_handler(Text(contains='🥪'))
async def buterbrod(message: types.Message, state: FSMContext):
    await message.answer_sticker(
        sticker=START_BUTER_ID
    )
    await state.set_state("buterbrod")


@dp.message_handler(state="buterbrod")
async def buterbrod_end(message: types.Message, state: FSMContext):
    await message.answer_sticker(
        sticker=END_BUTER_ID
    )
    await state.finish()
