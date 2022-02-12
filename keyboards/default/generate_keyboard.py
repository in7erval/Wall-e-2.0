from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Сгенерировать любое"),
            KeyboardButton(text="Убрать клавиатуру")
        ],
        [
            KeyboardButton(text="Большой текст"),
            KeyboardButton(text="Средний текст"),
            KeyboardButton(text="Маленький текст")
        ],
        [
            KeyboardButton(text='Прислать инлайн'),
            KeyboardButton(text='К обычной клавиатуре'),
        ]

    ],
    resize_keyboard=True,
    input_field_placeholder='Выбирай'
)
