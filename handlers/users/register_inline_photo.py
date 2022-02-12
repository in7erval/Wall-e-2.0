from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.utils.markdown import hcode, hbold

from loader import dp
from utils.db_api.quick_commands import add_inline_photo, del_inline_photo


@dp.message_handler(Command('register_inline_photo'))
async def register_inline_photo(message: types.Message):
    query = message.get_args()
    if not query:
        await message.reply(
            text='Нет запроса, по которому будет производится поиск фото.'
                 '\nФормат: \n' + hcode('/register_inline_photo QUERY')
        )
        return
    if not message.reply_to_message.photo:
        await message.reply(
            text='Для использования ответь на сообщение с фотографией'
        )
        return
    photo_id = message.reply_to_message.photo[-1].file_id
    await add_inline_photo(id=photo_id, query=query)
    await message.reply(
        text='Фото успешно добавлено'
    )


@dp.message_handler(Command('unregister_inline_photo'))
async def unregister_inline_photo(message: types.Message):
    reply_message = message.reply_to_message
    if not reply_message:
        await message.reply(
            text='Ответьте на сообщение с фотографией и, если нужно '
                 'удалить данное фото только из какого-то конкретного запроса, '
                 'то укажите его после команды. \n'
                 f'По умолчанию фото удаляется из {hbold("всех")} запросов.'

        )
        return
    photo_id = reply_message.photo[-1].file_id
    args = message.get_args()
    if not args:
        status = await del_inline_photo(id=photo_id)
    else:
        status = await del_inline_photo(id=photo_id, query=args)
    if status:
        await message.reply(
            text='Фото успешно удалено'
        )
    else:
        await message.reply(
            text='Ошибка при удалении. Обратитесь к администратору.'
        )
