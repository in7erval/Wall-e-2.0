"""
Роутер для пользовательских команд и клавиатуры
"""
from typing import TYPE_CHECKING, Any

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove

if TYPE_CHECKING:
    from database.repositories import UserRepository

router = Router()

# --- Клавиатуры ---

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🐱"), KeyboardButton(text="🦊"), KeyboardButton(text="🎲")],
        [KeyboardButton(text="Бутерброд 🥪"), KeyboardButton(text="Крестики-нолики"), KeyboardButton(text="✂️ КНБ")],
        [KeyboardButton(text="🎯 Виселица"), KeyboardButton(text="🔢 Угадай число"), KeyboardButton(text="🔮 Гороскоп")],
        [KeyboardButton(text="😂 Анекдот"), KeyboardButton(text="💬 Цитата"), KeyboardButton(text="💡 Факт")],
        [KeyboardButton(text="Клавиатура для генерации"), KeyboardButton(text="Убрать клавиатуру")],
    ],
    resize_keyboard=True,
    input_field_placeholder='Выбирай'
)

generate_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Сгенерировать любое"), KeyboardButton(text="Убрать клавиатуру")],
        [KeyboardButton(text="Большой текст"), KeyboardButton(text="Средний текст"), KeyboardButton(text="Маленький текст")],
        [KeyboardButton(text="Прислать инлайн"), KeyboardButton(text="К обычной клавиатуре")],
    ],
    resize_keyboard=True,
    input_field_placeholder='Выбирай'
)


# --- Команды ---

@router.message(CommandStart())
async def cmd_start(message: Message, repos: dict[str, Any]) -> None:
    """Обработчик команды /start"""
    user_repo: UserRepository = repos['user']

    user = await user_repo.get(message.from_user.id)
    if not user:
        await user_repo.create(
            user_id=message.from_user.id,
            name=message.from_user.full_name or "Unknown",
            is_admin=False
        )

    await message.answer(
        f'Привет, {message.from_user.full_name}!\n'
        f'Я Wall-e 2.0 — Telegram бот.\n\n'
        f'Отправь /help для списка команд.',
        reply_markup=main_keyboard
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Обработчик команды /help"""
    await message.answer(
        "🤖 <b>Wall-e 2.0 - Доступные команды:</b>\n\n"

        "🎮 <b>Игры:</b>\n"
        "  /tictactoe - Крестики-нолики\n"
        "  /rps - Камень-ножницы-бумага\n"
        "  /hangman - Виселица\n"
        "  /guess - Угадай число\n\n"

        "🔮 <b>Контент:</b>\n"
        "  /joke - Анекдот\n"
        "  /quote - Цитата\n"
        "  /horoscope - Гороскоп\n"
        "  /fact - Интересный факт\n"
        "  /bigtext [текст] - Текст эмодзи\n\n"

        "👥 <b>Социальное:</b>\n"
        "  /who [роль] - Кто сегодня [роль]?\n"
        "  /match - Совместимость (ответом на сообщение)\n"
        "  бот шар [вопрос] - Шар-предсказатель\n"
        "  бот оцени [что-то] - Рейтинг\n\n"

        "🦊 <b>Развлечения:</b>\n"
        "  /get_fox - Фото лисички\n"
        "  /get_cat - Фото котика\n"
        "  /tts - Озвучить текст\n"
        "  бот насколько [вопрос] - Вероятность\n"
        "  бот [A] или [Б] - Выбор\n\n"

        "📝 <b>Генерация текста:</b>\n"
        "  /generate_random - Сгенерировать сообщение\n\n"

        "📊 <b>Утилиты:</b>\n"
        "  /photo_rectangles - Обработать фото"
    )


# --- Кнопки клавиатуры ---

@router.message(Command("send_keyboard"))
@router.message(F.text == "К обычной клавиатуре")
async def send_main_keyboard(message: Message) -> None:
    """Активировать основную клавиатуру"""
    await message.answer("Клавиатура активирована", reply_markup=main_keyboard)
    await message.delete()


@router.message(Command("send_keyboard_gen"))
@router.message(F.text == "Клавиатура для генерации")
async def send_gen_keyboard(message: Message) -> None:
    """Активировать клавиатуру генерации"""
    await message.answer("Клавиатура генерации активирована", reply_markup=generate_keyboard)
    await message.delete()


@router.message(F.text == "Убрать клавиатуру")
async def remove_keyboard(message: Message) -> None:
    """Убрать клавиатуру"""
    await message.answer("Клавиатура убрана", reply_markup=ReplyKeyboardRemove())
    await message.delete()


@router.message(F.text == "🐱")
async def btn_cat(message: Message) -> None:
    """Кнопка котик"""
    await message.delete()
    from bot.routers.entertainment import cmd_get_cat
    await cmd_get_cat(message)


@router.message(F.text == "🦊")
async def btn_fox(message: Message) -> None:
    """Кнопка лисичка"""
    await message.delete()
    from bot.routers.entertainment import cmd_get_fox
    await cmd_get_fox(message)


@router.message(F.text.casefold() == "крестики-нолики")
async def btn_tictactoe(message: Message) -> None:
    """Кнопка крестики-нолики"""
    from bot.routers.games import cmd_tictactoe
    await cmd_tictactoe(message)


@router.message(F.text.in_({"✂️ КНБ", "✂️ кнб"}))
async def btn_rps(message: Message) -> None:
    from bot.routers.games import cmd_rps
    await cmd_rps(message)


@router.message(F.text == "🎯 Виселица")
async def btn_hangman(message: Message, state) -> None:
    from bot.routers.games import cmd_hangman
    await cmd_hangman(message, state)


@router.message(F.text == "🔢 Угадай число")
async def btn_guess(message: Message, state) -> None:
    from bot.routers.games import cmd_guess
    await cmd_guess(message, state)


@router.message(F.text == "🔮 Гороскоп")
async def btn_horoscope(message: Message) -> None:
    from bot.routers.content import cmd_horoscope
    await cmd_horoscope(message)


@router.message(F.text == "😂 Анекдот")
async def btn_joke(message: Message) -> None:
    from bot.routers.content import cmd_joke
    await cmd_joke(message)


@router.message(F.text == "💬 Цитата")
async def btn_quote(message: Message) -> None:
    from bot.routers.content import cmd_quote
    await cmd_quote(message)


@router.message(F.text == "💡 Факт")
async def btn_fact(message: Message) -> None:
    from bot.routers.content import cmd_fact
    await cmd_fact(message)
