from aiogram import types
from aiogram.dispatcher.filters import BoundFilter


class ChoiceFilter(BoundFilter):
    async def check(self, message: types.Message) -> bool:
        return message.text.lower().startswith('бот') and ' или ' in message.text.lower()
