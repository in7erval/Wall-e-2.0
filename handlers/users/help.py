from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp
from aiogram.utils.markdown import hbold, hcode, hitalic

from loader import dp

ADDITIONAL = f"Команда {hcode('/send_keyboard_gen')} присылает клавиатуру, а при нажатии на её кнопку 'Прислать инлайн' " \
             "присылается сообщение с инлайн-клавиатурой для генерации (попробуй!). \n" \
             f"Команда {hcode('/register_inline_photo QUERY')} позволяет зарегистрировать фотографию для выдачи " \
             f"в инлайн запросах: {hcode('@testIntervalbot')}. При пустом запросе показываются все QUERY, " \
             f"которые можно указать. Например, если ранее была зарегистрирована фотография через " \
             f"{hcode('/register_inline_photo cat')}, то при вводе {hcode('@testIntervalbot cat')} " \
             f"будет выведена эта фотография. Можно регистровать несколько фотографий под одним QUERY.\n\n" \
             f"При запросе '" + hbold("бот кинь кубик") + "' или '" + hbold("кинь кубик") + "' будет прислана " \
                                                                                            "анимация кубика. \n" \
                                                                                            f"При запросе '" + hbold(
    "бот насколько ") + hitalic("[что-то]") + "' или '" + hbold("насколько ") + hitalic("[что-то]") + "' " \
                                                                                                      "будет выведен " \
                                                                                                      "ответ 'Я думаю, " \
                                                                                                      "что на " + \
             hitalic("(сколько-то)") + "%'\n" \
                                       "При запросе 'бот X или Y [или Z [или ...]]' будет выведен ответ " \
                                       "'Определённо [X|Y|Z|...]' (один из " \
                                       "представленных)\n" \
                                       "При запросе '" + hbold("бот скажи ") + hitalic(
    "что-то") + "' будет озвучено сообщение."
COMMANDS = {'help': 'Эта справка',
            'tictactoe': 'Игра "крестики-нолики"',
            'get_cat': 'Прислать рандомное фото котика (кто не любит котиков???)',
            'get_fox': 'Прислать рандомное фото лисички (кто не любит лисичек???)',
            'generate_random': 'Сгенерировать сообщение из текущего диалога',
            'generate_{large, medium, small}_random': 'Сгенерировать сообщение одного из размеров',
            'send_keyboard': 'Активировать клавиатуру',
            'send_keyboard_gen': 'Активировать клавиатуру для генерации сообщений',
            'ro [ВРЕМЯ (в минутах)] [ПРИЧИНА]': f"Замьютить пользователя на ВРЕМЯ по причине ПРИЧИНА. "
                                                f"По умолчанию время = 5 минут. {hitalic('adminonly')}",
            'unro': f'Размьютить пользователя {hitalic("adminonly")}',
            'ban': f'Забанить (с удалением из группы) пользователя {hitalic("adminonly")}',
            'unban': f'Разбанить пользователя {hitalic("adminonly")}',
            'register_inline_photo QUERY': f'Зарегистрировать фото для инлайн режима с QUERY. См. далее',
            # 'register_inline_photo [QUERY]': f'Удалить фото из инлайн режима [для QUERY]',
            'del': 'Удалить сообщение под реплаем',
            'set_photo': 'Установить фотографию группы',
            'set_title': 'Установить заголовок группы',
            'set_description': 'Установить описание группы',
            'addadmin': f'Назначить пользователя администратором {hitalic("adminonly")}',
            'deladmin': f'Убрать пользователя из администраторов {hitalic("adminonly")}',
            'getadmins': 'Список всех администраторов',
            'tts': 'Озвучить сообщение',
            'send_history': f'Получить файл истории сообщений {hitalic("adminonly")}',
            }


@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message):
    text = "Список команд:\n"
    for command, descr in COMMANDS.items():
        text += f'\t{hcode("/" + command)} - {descr}' + '\n'
    text += '\n' + ADDITIONAL
    await message.answer(text)
