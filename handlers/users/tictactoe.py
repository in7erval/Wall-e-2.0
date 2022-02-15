import logging
import random

from aiogram import types
from aiogram.dispatcher.filters import Command, Text
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from keyboards.inline.tictactoe_inline import keyboard_inline, callback_data, SPACE_CHAR
from loader import dp

SPACE = 0
KREST = 1
ZERO = 2
KREST_CHAR = '❌'
ZERO_CHAR = '⭕️'

TURN_ZERO = f"Ход {ZERO_CHAR}"
TURN_KREST = f"Ход {KREST_CHAR}"


@dp.message_handler(Text(equals="Крестики-нолики"))
@dp.message_handler(Command('tictactoe'))
async def tictactoe_init(message: types.Message):
    await message.answer(
        text=TURN_KREST,
        reply_markup=keyboard_inline
    )
    if message.text == "Крестики-нолики":
        await message.delete()


@dp.callback_query_handler(Text(contains='tictactoe_item'))
async def tictactoe_turn(call: types.CallbackQuery):
    c_data = callback_data.parse(call.data)
    number = int(c_data.get("number"))
    reply_markup = call.message.reply_markup
    prev_text = call.message.text

    buttons_arr = await inline2array(reply_markup.inline_keyboard)

    i, j = number // 3, number % 3

    if buttons_arr[i][j] == SPACE:
        if prev_text == TURN_ZERO:
            buttons_arr[i][j] = ZERO
            text = TURN_KREST
        else:
            buttons_arr[i][j] = KREST
            text = TURN_ZERO
        is_win, who_wins = await check_win(buttons_arr)
        nospace = await check_no_space(buttons_arr)
        if nospace or is_win:
            who_wins = KREST_CHAR if who_wins == KREST else ZERO_CHAR
            text = f'Выиграл {who_wins}!' if is_win else f'Ничья!'
        else:
            await auto_turn(buttons_arr, prev_text == TURN_KREST)
            is_win, who_wins = await check_win(buttons_arr)
            nospace = await check_no_space(buttons_arr)
            if nospace or is_win:
                who_wins = KREST_CHAR if who_wins == KREST else ZERO_CHAR
                text = f'Выиграл {who_wins}!' if is_win else f'Ничья!'
        reply_markup = await array2inline(buttons_arr, adding=is_win)
        if nospace or is_win:
            reply_markup.inline_keyboard.append(
                [InlineKeyboardButton(text='Сыграем ещё?',
                                      callback_data='tictactoe_new')]
            )
        await call.message.edit_text(text, reply_markup=reply_markup)


@dp.callback_query_handler(Text(contains='tictactoe_new'))
async def tictactoe_new(call: types.CallbackQuery):
    await call.message.edit_text(TURN_KREST, reply_markup=keyboard_inline)


async def inline2array(buttons: []):
    buttons_arr = []
    for button_row in buttons:
        row = []
        for button in button_row:
            if button.text == SPACE_CHAR:
                row.append(SPACE)
            elif button.text == KREST_CHAR:
                row.append(KREST)
            else:
                row.append(ZERO)
        buttons_arr.append(row)
    return buttons_arr


async def array2inline(buttons_arr: [], adding: bool = False):
    inline_keyboard = []
    for i, button_row in enumerate(buttons_arr):
        inline_keyboard_row = []
        for j, button in enumerate(button_row):
            text = SPACE_CHAR if button == SPACE else (KREST_CHAR if button == KREST else ZERO_CHAR)
            number = i * 3 + j
            inline_keyboard_row.append(InlineKeyboardButton(text=text,
                                                            callback_data=callback_data.new(
                                                                number=number) if not adding else 'finish'))
        inline_keyboard.append(inline_keyboard_row)
    return InlineKeyboardMarkup(row_width=3, inline_keyboard=inline_keyboard)


async def check_win(arr: []):
    # check rows
    for i in range(3):
        if arr[i][0] == arr[i][1] == arr[i][2] != SPACE:
            return True, arr[i][0]
    # check columns
    for i in range(3):
        if arr[0][i] == arr[1][i] == arr[2][i] != SPACE:
            return True, arr[i][0]
    # check diag
    if arr[0][0] == arr[1][1] == arr[2][2] != SPACE:
        return True, arr[0][0]
    if arr[0][2] == arr[1][1] == arr[2][0] != SPACE:
        return True, arr[0][0]
    return False, None


async def check_no_space(arr: []):
    for row in arr:
        for elem in row:
            if elem == SPACE:
                return False
    return True


async def auto_turn(arr: [], krest_turn: bool):
    spaces = []
    for i, row in enumerate(arr):
        for j, elem in enumerate(row):
            if elem == SPACE:
                spaces.append((i, j))
    i, j = random.choice(spaces)
    if krest_turn:
        arr[i][j] = KREST
    else:
        arr[i][j] = ZERO
