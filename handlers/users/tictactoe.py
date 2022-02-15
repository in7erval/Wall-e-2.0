import logging

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


@dp.message_handler(Command('tictactoe'))
async def tictactoe_init(message: types.Message):
    await message.answer(
        text=TURN_KREST,
        reply_markup=keyboard_inline
    )


@dp.callback_query_handler(Text(contains='tictactoe_item'))
async def tictactoe_turn(call: types.CallbackQuery):
    c_data = callback_data.parse(call.data)
    number = int(c_data.get("number"))
    reply_markup = call.message.reply_markup

    logging.debug(f"number: {number}")
    logging.debug(f"reply_markup: {reply_markup}")
    logging.debug(f"reply_markup.inline_keyboard: {reply_markup.inline_keyboard}")

    buttons_arr = await inline2array(reply_markup.inline_keyboard)
    prev_text = call.message.text
    i, j = number // 3, number % 3
    button = buttons_arr[i][j]
    if button == SPACE:
        if prev_text == TURN_ZERO:
            buttons_arr[i][j] = ZERO
            text = TURN_KREST
        else:
            buttons_arr[i][j] = KREST
            text = TURN_ZERO
        if await check_no_space(buttons_arr):
            is_win, who_wins = await check_win(buttons_arr)
            if is_win:
                await call.message.edit_text(f'Выиграл {KREST_CHAR if who_wins == KREST else ZERO_CHAR}!')
            else:
                await call.message.edit_text(f'Ничья!')
            await call.message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup(row_width=1,
                                                  inline_keyboard=[
                                                      [InlineKeyboardButton(text='Сыграем ещё?',
                                                                            callback_data='tictactoe_new')]
                                                  ])
            )
        else:
            await call.message.edit_text(
                text
            )
            await call.message.edit_reply_markup(
                reply_markup=await array2inline(buttons_arr)
            )


@dp.callback_query_handler(Text(contains='tictactoe_new'))
async def tictactoe_turn(call: types.CallbackQuery):
    await call.message.edit_text(TURN_KREST)
    await call.message.edit_reply_markup(
        reply_markup=keyboard_inline
    )


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
    return buttons


async def array2inline(buttons_arr: []):
    inline_keyboard = []
    for i, button_row in enumerate(buttons_arr):
        inline_keyboard_row = []
        for j, button in enumerate(button_row):
            text = SPACE_CHAR if button == SPACE else (KREST_CHAR if button == KREST else ZERO_CHAR)
            number = i * 3 + j
            inline_keyboard_row.append(InlineKeyboardButton(text=text,
                                                            callback_data=callback_data.new(number=number)))
        inline_keyboard.append(inline_keyboard_row)
    return InlineKeyboardMarkup(row_width=3, inline_keyboard=inline_keyboard)


async def check_win(arr: []):
    # check rows
    for i in range(3):
        if arr[i][0] == arr[i][1] == arr[i][2]:
            return True, arr[i][0]
    # check columns
    for i in range(3):
        if arr[0][i] == arr[1][i] == arr[2][i]:
            return True, arr[i][0]
    # check diag
    if arr[0][0] == arr[1][1] == arr[2][2]:
        return True, arr[0][0]
    if arr[0][2] == arr[1][1] == arr[2][0]:
        return True, arr[0][0]
    return False, None


async def check_no_space(arr: []):
    for row in arr:
        for elem in row:
            if elem == SPACE:
                return False
    return True
