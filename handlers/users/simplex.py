from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InputFile
from aiogram.utils.markdown import hlink, hbold, hcode

from loader import dp
from states.Simplex import Simplex
import logging

from utils.simplex.App import parse_equation, parse_function_coefs, App

keyboard_start = ReplyKeyboardMarkup(row_width=2,
                                     resize_keyboard=True,
                                     one_time_keyboard=True,
                                     keyboard=[[
                                         KeyboardButton(text='Да'),
                                         KeyboardButton(text='Нет')
                                     ]])
keyboard_maxmin = ReplyKeyboardMarkup(row_width=2,
                                      one_time_keyboard=True,
                                      resize_keyboard=True,
                                      keyboard=[[
                                          KeyboardButton('Максимизируем 📈'),
                                          KeyboardButton('Минимизируем  📉')
                                      ]])

STOP_WORD = 'СТОП'


@dp.message_handler(Command('simplex'))
async def start_simplex(message: types.Message, state: FSMContext):
    await message.answer('Это интерфейс к решению задачи поиска max/min функции при наложенных ограничениях. '
                         f'За {hlink("решатель", "https://github.com/JettPy/Simlex-Table")} спасибо @suslik13.\n' \
                         f'{hbold("Желаешь продолжить? ;)")}\n'
                         f'В любой момент можно ввести {STOP_WORD} и закончить 🥰',
                         reply_markup=keyboard_start,
                         disable_web_page_preview=True)
    await Simplex.Start.set()


@dp.message_handler(state=Simplex.Start)
async def stop_or_variables(message: types.Message, state: FSMContext):
    if message.text in ['Нет', STOP_WORD]:
        await state.reset_state(with_data=True)
    elif message.text != 'Да':
        await message.answer('Нажми на одну из кнопок',
                             reply_markup=keyboard_start)
    else:
        await message.answer('Введи количество переменных:')
        await Simplex.NumVariables.set()


@dp.message_handler(state=Simplex.NumVariables)
async def enter_num_variables(message: types.Message, state: FSMContext):
    if message.text == STOP_WORD:
        await state.reset_state(with_data=True)
    num_var = message.text
    if not num_var.isnumeric():
        await message.answer('Введённое значение не число, попробуй ещё раз')
    else:
        async with state.proxy() as data:
            data['num_variables'] = num_var
        await message.answer('Введи количество ограничений:')
        await Simplex.NumEquations.set()


@dp.message_handler(state=Simplex.NumEquations)
async def enter_num_equations(message: types.Message, state: FSMContext):
    if message.text == STOP_WORD:
        await state.reset_state(with_data=True)
    num_eq = message.text
    if not num_eq.isnumeric():
        await message.answer('Введённое значение не число, попробуй ещё раз')
    else:
        async with state.proxy() as data:
            data['num_equations'] = num_eq
            data['num_entered_equations'] = 0
            data['matrix_a'] = []
            data['matrix_b'] = []
            data['signs'] = []
        await message.answer('Введи коэффициенты и знаки для уравнения №1.'
                             'Пример: для "x_1 + 2*x_2 + x_3 = 4" введите "1 2 1 == 4".'
                             'Как ты уже мог заметить для "=" используется "==" и вместо ">" и "<"'
                             'используются ">=" и "<=" соответственно. Учитывай это при вводе 😋',
                             parse_mode='Markdown')
        await Simplex.Equations.set()


@dp.message_handler(state=Simplex.Equations)
async def enter_equations(message: types.Message, state: FSMContext):
    if message.text == STOP_WORD:
        await state.reset_state(with_data=True)
    data = await state.get_data()
    num_entered_equations = int(data.get('num_entered_equations'))
    equation = message.text
    num_equations = int(data.get('num_equations'))
    num_variables = int(data.get('num_variables'))
    matrix_a = list(data.get('matrix_a'))
    matrix_b = list(data.get('matrix_b'))
    signs = list(data.get('signs'))

    is_error, error_str, (matrix_a_row, sign, b) = parse_equation(equation, num_variables)
    if is_error:
        await message.answer(f"{error_str}\nПопробуй ешё раз", parse_mode='Markdown')
        return
    matrix_a.append(matrix_a_row)
    signs.append(sign)
    matrix_b.append(b)
    data['matrix_a'] = matrix_a
    data['signs'] = signs
    data['matrix_b'] = matrix_b

    if num_entered_equations + 1 == num_equations:
        await message.answer(
            "Введи коэффициенты для целевой функции (учитывая свободный член и невошедшие переменные с 0):\n"
            f'Пример: для {hbold("Z(x) = 2X_1 - X_2")} введи {hbold("2 -1 0")}', parse_mode='Markdown')
        await Simplex.Function.set()
    else:
        data['num_entered_equations'] = num_entered_equations + 1
        await message.answer(f'Теперь то же самое для уравнения №{num_entered_equations + 1}. :)))',
                             parse_mode='Markdown')


@dp.message_handler(state=Simplex.Function)
async def enter_function(message: types.Message, state: FSMContext):
    if message.text == STOP_WORD:
        await state.reset_state(with_data=True)
    function = message.text
    data = await state.get_data()
    num_variables = int(data.get('num_variables'))

    is_error, error_str, matrix_c = parse_function_coefs(function, num_variables)
    if is_error:
        await message.answer(f"{error_str}\nПопробуй ешё раз", parse_mode='Markdown')
        return
    async with state.proxy() as data:
        data['matrix_c'] = matrix_c
    await message.answer('Что делаем?',
                         reply_markup=keyboard_maxmin)
    await Simplex.Maximize.set()


@dp.message_handler(state=Simplex.Maximize)
async def solve_equations(message: types.Message, state: FSMContext):
    if message.text == STOP_WORD:
        await state.reset_state(with_data=True)
    if message.text not in ['Максимизируем', 'Минимизируем']:
        await message.answer('Нажми на одну из кнопок',
                             reply_markup=keyboard_maxmin)
    else:
        data = await state.get_data()
        num_vars = data.get('num_variables')
        num_equats = data.get('num_equations')
        matrix_a = data.get('matrix_a')
        matrix_b = data.get('matrix_b')
        matrix_c = data.get('matrix_c')
        signs = data.get('signs')
        is_maximize = message.text == 'Максимизируем'

        app = App(variables_count=num_vars,
                  equations_count=num_equats,
                  matrix_a=matrix_a,
                  matrix_b=matrix_b,
                  matrix_c=matrix_c,
                  signs=signs,
                  is_maximize=is_maximize)
        app.do_artificial_basis(False)
        #
        # input_str = f'{num_vars}\n' \
        #             f'{num_equats}\n' \
        #             f'{equats}\n' \
        #             f'{function}\n' \
        #             f'{maximize}\n\n'
        # command = './simplex_table'
        # logging.info(command)
        # answer = await execute_command(command, input_str)
        temp = open(f"answer.txt", 'r')
        # temp.write(answer)
        # temp.close()
        answer = "\n".join(temp.readlines())
        if len(answer) <= 4000:
            await message.answer('Пришёл ответ:\n'
                                 f'{hcode(answer)}\n'
                                 f'Для лучшей читаемости можно воспользоваться файлом ниже.')
        await message.answer_document(document=InputFile(f"answer.txt"))
        await state.reset_state(with_data=True)


def is_number(s: str):
    if s.count('.') != 0:
        try:
            float(s)
            return True
        except ValueError:
            return False
    else:
        try:
            int(s)
            return True
        except ValueError:
            return False
