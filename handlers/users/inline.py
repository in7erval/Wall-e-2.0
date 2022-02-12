import asyncio
import logging

from aiogram import types
from aiogram.dispatcher.filters import Text

from loader import dp
from utils.db_api.quick_commands import select_all_queries, select_photos_by_query


@dp.inline_handler(text="")
async def empty_query(query: types.InlineQuery):
    await query.answer(
        results=await get_queries(),
        cache_time=5,

    )


@dp.inline_handler()
async def some_query(query: types.InlineQuery):
    text = query.query
    chat_id = query.from_user.id
    all_queries = await select_all_queries()
    logging.info(f"all_queries : {all_queries}, chat_id = {chat_id}")
    if text in all_queries:
        results = await get_queries_for_text(text)
    else:
        results = await get_queries()
    await query.answer(
        results=results,
        cache_time=5
    )


async def get_queries():
    all_queries = await select_all_queries()
    results = [
        types.InlineQueryResultArticle(
            id=str(i),
            title=query,
            input_message_content=types.InputTextMessageContent(
                message_text="Не обязательно жать при этом на кнопку"
            )
        ) for i, query in enumerate(list(all_queries))

    ]
    results.insert(0,
                   types.InlineQueryResultArticle(
                       id="info_id",
                       title="Выбери один из QUERY и впиши его...",
                       input_message_content=types.InputTextMessageContent(
                           message_text="Не обязательно жать при этом на кнопку"
                       )
                   )
                   )
    results.insert(1,
                   types.InlineQueryResultArticle(
                       id="info_id1",
                       title="...кликать не нужно",
                       input_message_content=types.InputTextMessageContent(
                           message_text="Не обязательно жать при этом на кнопку"
                       )
                   )
                   )
    return results


async def get_queries_for_text(text: str):
    all_photos = await select_photos_by_query(text)
    results = [
        types.InlineQueryResultCachedPhoto(
            id=str(i),
            title=text + str(i),
            photo_file_id=photo.id
        ) for i, photo in enumerate(list(all_photos))
    ]
    return results


@dp.message_handler(Text(equals="Не обязательно жать при этом на кнопку"))
async def delete_info_message(message: types.Message):
    await asyncio.sleep(0.5)
    await message.delete()
