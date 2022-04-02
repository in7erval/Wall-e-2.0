from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            # types.BotCommand("start", "Запустить бота"),
            types.BotCommand("help", "Вывести справку"),
            types.BotCommand("tictactoe", 'Игра "крестики-нолики"'),
            types.BotCommand("get_fox", "Прислать рандомное фото лисички (кто не любит лисичек???)"),
            types.BotCommand("get_cat", "Прислать рандомное фото котика (кто не любит котиков???)"),
            types.BotCommand('send_keyboard', 'Активировать клавиатуру'),
            types.BotCommand('send_keyboard_gen', 'Активировать клавиатуру для сообщений генерации'),
            types.BotCommand('generate_random', 'Сгенерировать сообщение'),
            types.BotCommand('generate_large_random', 'Сгенерировать большое сообщение'),
            types.BotCommand('generate_medium_random', 'Сгенерировать среднее сообщение'),
            types.BotCommand('generate_small_random', 'Сгенерировать маленькое сообщение'),
            types.BotCommand('ro', 'Замьютить пользователя'),
            types.BotCommand('unro', 'Размьютить пользователя'),
            types.BotCommand('ban', 'Забанить пользователя'),
            types.BotCommand('unban', 'Разбанить пользователя'),
            types.BotCommand('set_photo', 'Установить фото группы'),
            types.BotCommand('set_title', 'Установить заголовок группы'),
            types.BotCommand('set_description', 'Установить описание группы'),
            types.BotCommand('addadmin', 'Назначить пользователя администратором'),
            types.BotCommand('deladmin', 'Убрать пользователя из администратором'),
            types.BotCommand('getadmins', 'Список всех администраторов'),
            types.BotCommand('register_inline_photo', 'Зарегистрировать инлайн-фото'),
            # types.BotCommand('unregister_inline_photo', 'Удалить инлайн-фото из запросов'),
            types.BotCommand("del", "Удалить данное сообщение и reply на другое"),
            types.BotCommand('tts', 'Озвучить сообщение'),
            types.BotCommand('photo_rectangles', 'Преобразовать фото'),
            types.BotCommand('simplex', 'Задача нахождения min/max функции с учетом ограничений')
        ]
    )
