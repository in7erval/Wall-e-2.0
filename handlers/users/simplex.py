from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InputFile
from aiogram.utils.markdown import hlink, hbold, hcode, hitalic

from loader import dp, bot
from states.Simplex import Simplex
import logging

from utils.simplex.App import parse_equation, parse_function_coefs, App

STOP_WORD = 'СТОП'
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
keyboard_method = ReplyKeyboardMarkup(row_width=3,
                                      one_time_keyboard=True,
                                      resize_keyboard=True,
                                      keyboard=[[
                                          KeyboardButton('Искусственного базиса'),
                                          KeyboardButton('Дуальная задача'),
                                          KeyboardButton('Гомори'),
                                      ],
                                          [KeyboardButton(STOP_WORD)]])


@dp.message_handler(Command('simplex'))
async def start_simplex(message: types.Message, state: FSMContext):
    await message.answer('Это интерфейс к решению задачи поиска max/min функции при наложенных ограничениях. '
                         f'{hbold("Желаешь продолжить? ;)")}\n'
                         f'В любой момент можно ввести {STOP_WORD} и закончить 🥰\n'
                         f'P.S. За {hlink("решатель", "https://github.com/JettPy/Simlex-Table")} спасибо @suslik13.\n',
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
        return
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
        return
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
            ps = hitalic('P.S. Как ты уже мог заметить для "=" используется "==" и вместо "больше" и "меньше" '
                         'используются "больше или равно" и "меньше или равно" соответственно. Учитывай это при вводе 😋')
        await message.answer('Введи коэффициенты и знаки для уравнения №1.\n'
                             f'Пример: для {hcode("x_1 + 2*x_2 + x_3 = 4")} введи {hcode("1 2 1 == 4")}.\n\n'
                             f'{ps}')
        await Simplex.Equations.set()


@dp.message_handler(state=Simplex.Equations)
async def enter_equations(message: types.Message, state: FSMContext):
    if message.text == STOP_WORD:
        await state.reset_state(with_data=True)
        return
    equation = message.text
    data = await state.get_data()
    num_entered_equations = int(data.get('num_entered_equations'))
    num_equations = int(data.get('num_equations'))
    num_variables = int(data.get('num_variables'))
    matrix_a = list(data.get('matrix_a'))
    matrix_b = list(data.get('matrix_b'))
    signs = list(data.get('signs'))

    logging.debug(f'num_entered_equations={num_entered_equations} '
                  f'num_equations={num_equations} '
                  f'num_variables={num_variables} '
                  f'matrix_a={matrix_a} '
                  f'matrix_b={matrix_b} '
                  f'signs={signs} ')

    is_error, error_str, answer = parse_equation(equation, num_variables)
    if is_error:
        await message.answer(f"{error_str}\nПопробуй ешё раз", parse_mode='Markdown')
        return
    num_entered_equations += 1
    (matrix_a_row, sign, b) = answer
    matrix_a.append(matrix_a_row)
    signs.append(sign)
    matrix_b.append(b)
    async with state.proxy() as data:
        data['matrix_a'] = matrix_a
        data['signs'] = signs
        data['matrix_b'] = matrix_b
        data['num_entered_equations'] = num_entered_equations
    if num_entered_equations == num_equations:
        await message.answer(
            "Введи коэффициенты для целевой функции\n(без свободного члена, но учитывая невошедшие переменные как 0*X_i):\n\n"
            f'Пример: для {hcode("Z(x) = 2X_1 - X_2")} с тремя переменными введи {hcode("2 -1 0")}')
        await Simplex.Function.set()
    else:
        logging.debug(f"num_entered_equations={num_entered_equations}")
        await message.answer(f'Теперь то же самое для уравнения №{num_entered_equations + 1}. :)))')


@dp.message_handler(state=Simplex.Function)
async def enter_function(message: types.Message, state: FSMContext):
    if message.text == STOP_WORD:
        await state.reset_state(with_data=True)
        return
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
async def choice_method(message: types.Message, state: FSMContext):
    if message.text == STOP_WORD:
        await state.reset_state(with_data=True)
        return
    if message.text not in ['Максимизируем 📈', 'Минимизируем  📉']:
        await message.answer('Нажми на одну из кнопок',
                             reply_markup=keyboard_maxmin)
    else:
        data = await state.get_data()
        num_vars = int(data.get('num_variables'))
        num_equats = int(data.get('num_equations'))
        matrix_a = data.get('matrix_a')
        matrix_b = data.get('matrix_b')
        matrix_c = data.get('matrix_c')
        signs = data.get('signs')
        is_maximize = 'Максимизируем' in message.text
        deb = f"Количество переменных: {num_vars}\n" \
              f"Количество уравнений: {num_equats}\n" \
              f"Матрица А: {matrix_a}\n" \
              f"Матрица B: {matrix_b}\n" \
              f"Матрица С: {matrix_c}\n" \
              f"Знаки: {signs}\n" \
              f"Максимизация: {'да' if is_maximize else 'нет'}"

        app = App(variables_count=num_vars,
                  equations_count=num_equats,
                  matrix_a=matrix_a,
                  matrix_b=matrix_b,
                  matrix_c=matrix_c,
                  signs=signs,
                  is_maximize=is_maximize,
                  filename=f'answer{message.from_user.id}.txt')
        async with state.proxy() as data:
            data['app'] = app
        await message.answer('Ты ввёл следующие данные о задаче:\n'
                             f'{hcode(deb)}\n'
                             f'{hitalic("Теперь выбери способ решения на клавиатуре")}',
                             reply_markup=keyboard_method)
        await Simplex.Method.set()


@dp.message_handler(state=Simplex.Method)
async def solve_equations(message: types.Message, state: FSMContext):
    if message.text == STOP_WORD:
        await state.reset_state(with_data=True)
        return
    if message.text not in ['Гомори', 'Искусственного базиса', 'Дуальная задача']:
        await message.answer('Нажми на одну из кнопок',
                             reply_markup=keyboard_maxmin)
    else:
        data = await state.get_data()
        app = data['app']
        try:
            open(f"answer{message.from_user.id}.txt", 'w')  # очистим файл
            if message.text == 'Гомори':
                app.do_gomori(False)
                logging.debug("Gomori done")
            elif message.text == 'Искусственного базиса':
                app.do_artificial_basis(False)
                logging.debug("ArtificialBasic done")
            else:
                app.do_dual_task(False)
                logging.debug('DualTask done')
            temp = open(f"answer{message.from_user.id}.txt", 'r')
            answer = "\n".join(temp.readlines())
            if len(answer) <= 4000:
                await message.answer('Пришёл ответ:\n'
                                     f'{hcode(answer)}\n'
                                     f'Для лучшей читаемости можно воспользоваться файлом ниже.')
            await message.answer_document(document=InputFile(f"answer{message.from_user.id}.txt"))
            await message.answer('Что-то ещё?',
                                 reply_markup=keyboard_method)
        except Exception as err:
            await message.answer(f"Ошибка! {err}\nПопробуй ввести всё заново и по желанию "
                                 f"расскажи @Dimo4kaa что вводил(а)")
            await state.reset_state(with_data=True)
            raise err


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
