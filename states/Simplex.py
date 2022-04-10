from aiogram.dispatcher.filters.state import StatesGroup, State


class Simplex(StatesGroup):
    Start = State()
    NumVariables = State()
    NumEquations = State()
    Equations = State()
    Function = State()
    Maximize = State()
    Method = State()
