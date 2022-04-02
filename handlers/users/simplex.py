import os

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InputFile
from aiogram.utils.markdown import hlink, hbold, hcode

from loader import dp
from states.Simplex import Simplex
import logging

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
                                          KeyboardButton('Максимизируем'),
                                          KeyboardButton('Минимизируем')
                                      ]])


@dp.message_handler(Command('simplex'))
async def start_simplex(message: types.Message, state: FSMContext):
    await message.answer('Это интерфейс к решению задачи поиска max/min функции при наложенных ограничениях. '
                         f'За {hlink("решатель", "https://github.com/JettPy/Simlex-Table")} спасибо @suslik13.\n' \
                         f'{hbold("Желаешь продолжить? ;)")}',
                         reply_markup=keyboard_start,
                         disable_web_page_preview=True)
    await Simplex.Start.set()


@dp.message_handler(state=Simplex.Start)
async def stop_or_variables(message: types.Message, state: FSMContext):
    if message.text == 'Нет':
        await state.reset_state(with_data=True)
    elif message.text != 'Да':
        await message.answer('Нажми на одну из кнопок',
                             reply_markup=keyboard_start)
    else:
        await message.answer('Введи количество переменных:')
        await Simplex.NumVariables.set()


@dp.message_handler(state=Simplex.NumVariables)
async def enter_num_variables(message: types.Message, state: FSMContext):
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
    num_eq = message.text
    if not num_eq.isnumeric():
        await message.answer('Введённое значение не число, попробуй ещё раз')
    else:
        async with state.proxy() as data:
            data['num_equations'] = num_eq
        await message.answer('Введи коэффициенты и знаки для уравнений.\n'
                             'В каждой строке одно уравнение!\n'
                             'Пример: для "x_1 + 2*x_2 + x_3 = 4" введите "1 2 1 = 4".')
        await Simplex.Equations.set()


@dp.message_handler(state=Simplex.Equations)
async def enter_equations(message: types.Message, state: FSMContext):
    equations = message.text.split('\n')
    data = await state.get_data()
    num_equations = int(data.get('num_equations'))
    num_variables = int(data.get('num_variables'))
    check_passed = True
    if num_equations != len(equations):
        await message.answer(f"Количество введённых уравнений не соответствует введённому количеству! Попробуй ешё раз")
        check_passed = False
    if check_passed:
        for i, equation in enumerate(equations):
            if equation.count('=') != 1:
                await message.answer(f"В уравнении #{i + 1} {equation.count('=')} знаков =! Попробуй еще раз.")
                check_passed = False
            else:
                if len(equation.split()) != num_variables + 2:
                    await message.answer(
                        f"В уравнении #{i + 1} количество введённых переменных не соответствует введённому количеству! Попробуй ешё раз")
                    check_passed = False
                else:
                    for token in equation.split():
                        if not is_number(token) and token not in ['=', '>=', '<=']:
                            await message.answer(f"В уравнении #{i + 1} '{token}' не число и не =! Попробуй еще раз.\n"
                                                 f"Знаки 'больше' и 'меньше' заменяй соответственно на '>=' и '<='",
                                                 parse_mode='Markdown')
                            check_passed = False
    if check_passed:
        async with state.proxy() as data:
            data['equations'] = equations
        await message.answer(
            "Введи коэффициенты для целевой функции (учитывая свободный член и невошедшие переменные с 0):\n"
            f'Пример: для {hbold("Z(x) = 2X_1 - X_2")} введи {hbold("2 -1 0")}')
        await Simplex.Function.set()


@dp.message_handler(state=Simplex.Function)
async def enter_function(message: types.Message, state: FSMContext):
    check_passed = True
    function = message.text
    data = await state.get_data()
    num_variables = int(data.get('num_variables'))
    if len(function.split()) != num_variables + 1:
        await message.answer(
            f"Введённое количество коэффициентов не совпадает с количеством переменных (или просто забыл свободный член). Попробуй ещё раз")
        check_passed = False
    else:
        for token in function.split():
            if not is_number(token):
                await message.answer(f"В функции '{token}' не число! Попробуй еще раз.")
                check_passed = False
    if check_passed:
        async with state.proxy() as data:
            data['function'] = function
        await message.answer('Что делаем?',
                             reply_markup=keyboard_maxmin)
        await Simplex.Maximize.set()


@dp.message_handler(state=Simplex.Maximize)
async def solve_equations(message: types.Message, state: FSMContext):
    if message.text not in ['Максимизируем', 'Минимизируем']:
        await message.answer('Нажми на одну из кнопок',
                             reply_markup=keyboard_maxmin)
    else:
        data = await state.get_data()
        num_vars = data.get('num_variables')
        num_equats = data.get('num_equations')
        equats = '\n '.join(list(data.get('equations')))
        function = data.get('function')
        maximize = 'y' if message.text == 'Максимизируем' else 'n'
        input_str = f'{num_vars}\n' \
                    f'{num_equats}\n' \
                    f'{equats}\n' \
                    f'{function}\n' \
                    f'{maximize}\n\n'
        command = f'echo "{input_str}" | ./simplex_table'
        logging.info(command)
        answer = await execute_command(command)
        temp = open(f"answer{message.from_user.id}.txt", 'w+')
        temp.write(answer)
        temp.close()
        msg = ('Пришёл ответ:\n'
               f'{hcode(answer)}\n'
               f'Для лучшей читаемости можно воспользоваться файлом ниже.')
        if len(msg) <= 4000:
            await message.answer('Пришёл ответ:\n'
                                 f'{hcode(answer)}\n'
                                 f'Для лучшей читаемости можно воспользоваться файлом ниже.')
        await message.answer_document(document=InputFile(f"answer{message.from_user.id}.txt"))
        await state.reset_state(with_data=True)


async def execute_command(command: str):
    return os.popen(command).read()


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
