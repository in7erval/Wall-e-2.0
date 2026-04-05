"""
Роутер для игр: Крестики-нолики, Камень-ножницы-бумага, Виселица, Угадай число
"""
import asyncio
import random

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

router = Router()

# ==================== Крестики-нолики ====================

SPACE = 0
KREST = 1
ZERO = 2
KREST_CHAR = '❌'
ZERO_CHAR = '⭕️'
SPACE_CHAR = '⠀'

TURN_ZERO = f"Ход {ZERO_CHAR}"
TURN_KREST = f"Ход {KREST_CHAR}"


def _char_to_cell(text: str) -> int:
    if text == KREST_CHAR:
        return KREST
    elif text == ZERO_CHAR:
        return ZERO
    return SPACE


def _board_from_markup(markup: InlineKeyboardMarkup) -> list[list[int]]:
    board = [[SPACE] * 3 for _ in range(3)]
    if not markup:
        return board
    for i, row in enumerate(markup.inline_keyboard):
        for j, btn in enumerate(row):
            board[i][j] = _char_to_cell(btn.text)
    return board


def create_keyboard(mode: str, board: list, finish: bool = False) -> InlineKeyboardMarkup:
    keyboard = []
    for i in range(3):
        row = []
        for j in range(3):
            cell = board[i][j]
            text = SPACE_CHAR if cell == SPACE else (KREST_CHAR if cell == KREST else ZERO_CHAR)
            callback = f"ttt_{mode}_{i}_{j}" if not finish else "ttt_finish"
            row.append(InlineKeyboardButton(text=text, callback_data=callback))
        keyboard.append(row)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def check_winner(board: list) -> tuple[bool, int | None, bool]:
    lines = []
    for i in range(3):
        lines.append([board[i][0], board[i][1], board[i][2]])
    for j in range(3):
        lines.append([board[0][j], board[1][j], board[2][j]])
    lines.append([board[0][0], board[1][1], board[2][2]])
    lines.append([board[0][2], board[1][1], board[2][0]])

    for line in lines:
        if line[0] == line[1] == line[2] != SPACE:
            return True, line[0], False

    for row in board:
        for cell in row:
            if cell == SPACE:
                return False, None, False

    return False, None, True


@router.message(Command('tictactoe'))
async def cmd_tictactoe(message: Message) -> None:
    await message.answer(
        text='Выберите режим игры:',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='👤 Игрок против Игрока', callback_data='ttt_start_pvp')],
            [InlineKeyboardButton(text='🤖 Игрок против Бота', callback_data='ttt_start_pve')],
        ])
    )


@router.callback_query(F.data.startswith('ttt_start_'))
async def tictactoe_start(call: CallbackQuery) -> None:
    mode = call.data.split('_')[-1]
    board = [[SPACE] * 3 for _ in range(3)]
    await call.message.edit_text(
        text=f"{TURN_KREST}\n\nРежим: {'🤖 с ботом' if mode == 'pve' else '👤 с игроком'}",
        reply_markup=create_keyboard(mode, board)
    )


@router.callback_query(F.data.startswith('ttt_') & ~F.data.startswith('ttt_start_') & ~F.data.startswith('ttt_finish'))
async def tictactoe_move(call: CallbackQuery) -> None:
    parts = call.data.split('_')
    if len(parts) != 4:
        return

    mode = parts[1]
    try:
        i, j = int(parts[2]), int(parts[3])
    except (ValueError, IndexError):
        return

    board = _board_from_markup(call.message.reply_markup)

    if board[i][j] != SPACE:
        await call.answer("Клетка занята!")
        return

    current_text = call.message.text or ""
    is_krest_turn = TURN_KREST in current_text
    board[i][j] = KREST if is_krest_turn else ZERO

    is_win, winner, is_draw = check_winner(board)

    if is_win:
        winner_char = KREST_CHAR if winner == KREST else ZERO_CHAR
        text = f"🎉 Победил {winner_char}!"
        keyboard = create_keyboard(mode, board, finish=True)
    elif is_draw:
        text = "🤝 Ничья!"
        keyboard = create_keyboard(mode, board, finish=True)
    else:
        next_is_krest = not is_krest_turn
        text = f"{TURN_KREST if next_is_krest else TURN_ZERO}\n\nРежим: {'🤖 с ботом' if mode == 'pve' else '👤 с игроком'}"
        keyboard = create_keyboard(mode, board)

    await call.message.edit_text(text=text, reply_markup=keyboard)

    if mode == 'pve' and is_krest_turn and not is_win and not is_draw:
        await asyncio.sleep(0.5)
        await _bot_move(call, board, mode)


async def _bot_move(call: CallbackQuery, board: list, mode: str) -> None:
    free_cells = [(i, j) for i in range(3) for j in range(3) if board[i][j] == SPACE]
    if free_cells:
        i, j = random.choice(free_cells)
        board[i][j] = ZERO
        is_win, _winner, is_draw = check_winner(board)
        if is_win:
            text = f"🎉 Победил {ZERO_CHAR} (бот)!"
            keyboard = create_keyboard(mode, board, finish=True)
        elif is_draw:
            text = "🤝 Ничья!"
            keyboard = create_keyboard(mode, board, finish=True)
        else:
            text = f"{TURN_KREST}\n\nРежим: 🤖 с ботом"
            keyboard = create_keyboard(mode, board)
        await call.message.edit_text(text=text, reply_markup=keyboard)


@router.callback_query(F.data == "ttt_finish")
async def tictactoe_finish(call: CallbackQuery) -> None:
    await call.answer("Игра завершена!")


# ==================== Камень-ножницы-бумага ====================

RPS_CHOICES = {'rock': '🪨 Камень', 'scissors': '✂️ Ножницы', 'paper': '📄 Бумага'}
RPS_WINS = {'rock': 'scissors', 'scissors': 'paper', 'paper': 'rock'}


@router.message(Command('rps'))
@router.message(F.text.casefold() == "камень-ножницы-бумага")
async def cmd_rps(message: Message) -> None:
    """Камень-ножницы-бумага"""
    await message.answer(
        "Выбирай:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="🪨", callback_data="rps_rock"),
            InlineKeyboardButton(text="✂️", callback_data="rps_scissors"),
            InlineKeyboardButton(text="📄", callback_data="rps_paper"),
        ]])
    )


@router.callback_query(F.data.startswith("rps_"))
async def rps_play(call: CallbackQuery) -> None:
    player_choice = call.data.replace("rps_", "")
    bot_choice = random.choice(list(RPS_CHOICES.keys()))

    player_name = RPS_CHOICES[player_choice]
    bot_name = RPS_CHOICES[bot_choice]

    if player_choice == bot_choice:
        result = "🤝 Ничья!"
    elif RPS_WINS[player_choice] == bot_choice:
        result = "🎉 Ты победил!"
    else:
        result = "🤖 Бот победил!"

    await call.message.edit_text(
        f"Ты: {player_name}\nБот: {bot_name}\n\n{result}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="🔄 Ещё раз", callback_data="rps_restart"),
        ]])
    )


@router.callback_query(F.data == "rps_restart")
async def rps_restart(call: CallbackQuery) -> None:
    await call.message.edit_text(
        "Выбирай:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="🪨", callback_data="rps_rock"),
            InlineKeyboardButton(text="✂️", callback_data="rps_scissors"),
            InlineKeyboardButton(text="📄", callback_data="rps_paper"),
        ]])
    )


# ==================== Виселица ====================

HANGMAN_WORDS = [
    "программа", "клавиатура", "монитор", "компьютер", "интернет",
    "телефон", "робот", "алгоритм", "функция", "переменная",
    "массив", "строка", "число", "объект", "модуль",
    "сервер", "браузер", "система", "память", "процессор",
    "питон", "telegram", "сообщение", "кнопка", "экран",
    "библиотека", "бот", "команда", "файл", "папка",
    "картинка", "музыка", "видео", "текст", "таблица",
    "ракета", "звезда", "планета", "космос", "солнце",
    "дерево", "цветок", "кошка", "собака", "птица",
]

HANGMAN_STAGES = [
    "```\n  +---+\n      |\n      |\n      |\n      |\n=========```",
    "```\n  +---+\n  O   |\n      |\n      |\n      |\n=========```",
    "```\n  +---+\n  O   |\n  |   |\n      |\n      |\n=========```",
    "```\n  +---+\n  O   |\n /|   |\n      |\n      |\n=========```",
    "```\n  +---+\n  O   |\n /|\\  |\n      |\n      |\n=========```",
    "```\n  +---+\n  O   |\n /|\\  |\n /    |\n      |\n=========```",
    "```\n  +---+\n  O   |\n /|\\  |\n / \\  |\n      |\n=========```",
]

HANGMAN_MAX_ERRORS = len(HANGMAN_STAGES) - 1

RUSSIAN_ALPHABET = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"


class HangmanState(StatesGroup):
    playing = State()


def _hangman_display(word: str, guessed: set[str]) -> str:
    return " ".join(ch if ch in guessed or not ch.isalpha() else "▪" for ch in word)


def _hangman_keyboard(guessed: set[str]) -> InlineKeyboardMarkup:
    rows = []
    for start in range(0, len(RUSSIAN_ALPHABET), 8):
        row = []
        for ch in RUSSIAN_ALPHABET[start:start + 8]:
            if ch in guessed:
                row.append(InlineKeyboardButton(text="·", callback_data="hm_used"))
            else:
                row.append(InlineKeyboardButton(text=ch.upper(), callback_data=f"hm_{ch}"))
        rows.append(row)
    rows.append([InlineKeyboardButton(text="🏳️ Сдаться", callback_data="hm_give_up")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.message(Command('hangman'))
@router.message(F.text.casefold() == "виселица")
async def cmd_hangman(message: Message, state: FSMContext) -> None:
    """Начать игру в виселицу"""
    word = random.choice(HANGMAN_WORDS).lower()
    guessed = set()
    errors = 0

    await state.set_state(HangmanState.playing)
    await state.update_data(word=word, guessed=list(guessed), errors=errors)

    display = _hangman_display(word, guessed)
    stage = HANGMAN_STAGES[errors]

    await message.answer(
        f"🎯 Виселица\n\n{stage}\n\nСлово: {display}\nОшибки: {errors}/{HANGMAN_MAX_ERRORS}",
        reply_markup=_hangman_keyboard(guessed)
    )


@router.callback_query(F.data == "hm_used")
async def hm_used(call: CallbackQuery) -> None:
    await call.answer("Буква уже использована!")


@router.callback_query(F.data == "hm_give_up")
async def hm_give_up(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    word = data.get("word", "???")
    await state.clear()
    await call.message.edit_text(f"🏳️ Вы сдались!\n\nСлово было: <b>{word}</b>")


@router.callback_query(F.data.startswith("hm_"))
async def hm_guess(call: CallbackQuery, state: FSMContext) -> None:
    letter = call.data.replace("hm_", "")
    if len(letter) != 1:
        return

    data = await state.get_data()
    word = data.get("word", "")
    guessed = set(data.get("guessed", []))
    errors = data.get("errors", 0)

    if not word:
        await call.answer("Игра не найдена. Начните новую: /hangman")
        return

    guessed.add(letter)

    if letter not in word:
        errors += 1

    await state.update_data(guessed=list(guessed), errors=errors)

    display = _hangman_display(word, guessed)
    stage = HANGMAN_STAGES[min(errors, HANGMAN_MAX_ERRORS)]

    # Проверка победы
    if all(ch in guessed or not ch.isalpha() for ch in word):
        await state.clear()
        await call.message.edit_text(
            f"🎉 Победа!\n\n{stage}\n\nСлово: <b>{word}</b>"
        )
        return

    # Проверка проигрыша
    if errors >= HANGMAN_MAX_ERRORS:
        await state.clear()
        await call.message.edit_text(
            f"💀 Проигрыш!\n\n{stage}\n\nСлово было: <b>{word}</b>"
        )
        return

    await call.message.edit_text(
        f"🎯 Виселица\n\n{stage}\n\nСлово: {display}\nОшибки: {errors}/{HANGMAN_MAX_ERRORS}",
        reply_markup=_hangman_keyboard(guessed)
    )


# ==================== Угадай число ====================

class GuessNumberState(StatesGroup):
    playing = State()


@router.message(Command('guess'))
@router.message(F.text.casefold() == "угадай число")
async def cmd_guess(message: Message, state: FSMContext) -> None:
    """Угадай число от 1 до 100"""
    number = random.randint(1, 100)
    await state.set_state(GuessNumberState.playing)
    await state.update_data(number=number, attempts=0)
    await message.answer(
        "🔢 Я загадал число от 1 до 100.\n"
        "Попробуй угадать! Отправь число.\n"
        "Для отмены — /cancel"
    )


@router.message(GuessNumberState.playing, Command("cancel"))
async def guess_cancel(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    number = data.get("number", "?")
    await state.clear()
    await message.reply(f"🏳️ Игра отменена. Число было: <b>{number}</b>")


@router.message(GuessNumberState.playing)
async def guess_process(message: Message, state: FSMContext) -> None:
    if not message.text or not message.text.strip().isdigit():
        await message.reply("Отправь число от 1 до 100!")
        return

    guess = int(message.text.strip())
    data = await state.get_data()
    number = data.get("number", 0)
    attempts = data.get("attempts", 0) + 1
    await state.update_data(attempts=attempts)

    if guess < number:
        await message.reply(f"⬆️ Больше! (попытка {attempts})")
    elif guess > number:
        await message.reply(f"⬇️ Меньше! (попытка {attempts})")
    else:
        await state.clear()
        if attempts <= 3:
            emoji = "🏆"
        elif attempts <= 7:
            emoji = "🎉"
        else:
            emoji = "✅"
        await message.reply(f"{emoji} Верно! Число <b>{number}</b> угадано за {attempts} попыток!")
