from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🐱"),
            KeyboardButton(text="🦊"),
        ],
        [
            KeyboardButton(text="Бутерброд 🥪"),
            KeyboardButton(text="🎲"),
            KeyboardButton(text="Крестики-нолики")
        ],
        [
            KeyboardButton(text='Клавиатура для генерации'),
            KeyboardButton(text="Убрать клавиатуру")
        ]

    ],
    resize_keyboard=True,
    input_field_placeholder='Выбирай'
)
