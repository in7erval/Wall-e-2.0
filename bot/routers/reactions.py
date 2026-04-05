"""
Роутер для реакций на сообщения (Telegram Reactions)
Доступно с Telegram Bot API 7.0+
"""
from typing import Any

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ReactionTypeEmoji

router = Router()


# Доступные реакции
AVAILABLE_REACTIONS = {
    "👍": "like",
    "👎": "dislike",
    "❤️": "heart",
    "🔥": "fire",
    "🎉": "party",
    "😍": "love",
    "💩": "poop",
    "🤡": "clown",
    "⭐️": "star",
    "👻": "ghost",
}


@router.message(Command("react"))
async def cmd_react(message: Message, repos: dict[str, Any]) -> None:
    """
    Добавить реакцию на сообщение (reply)

    Использование: /react 👍 или /react like
    """
    if not message.reply_to_message:
        await message.reply(
            "❌ Ответьте на сообщение, чтобы добавить реакцию\n\n"
            f"Доступные реакции: {', '.join(AVAILABLE_REACTIONS.keys())}"
        )
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply(
            "❌ Укажите реакцию\n\n"
            f"Пример: /react 👍\n"
            f"Доступные: {', '.join(AVAILABLE_REACTIONS.keys())}"
        )
        return

    reaction_input = args[1].strip()

    # Определяем реакцию
    if reaction_input in AVAILABLE_REACTIONS:
        emoji = reaction_input
    elif reaction_input in AVAILABLE_REACTIONS.values():
        emoji = next(k for k, v in AVAILABLE_REACTIONS.items() if v == reaction_input)
    else:
        await message.reply(
            f"❌ Неизвестная реакция: {reaction_input}\n\n"
            f"Доступные: {', '.join(AVAILABLE_REACTIONS.keys())}"
        )
        return

    try:
        await message.bot.set_message_reaction(
            chat_id=message.chat.id,
            message_id=message.reply_to_message.message_id,
            reaction=[ReactionTypeEmoji(emoji=emoji)],
            is_big=False  # Маленькая реакция (большая платная)
        )
        await message.reply(f"✅ Реакция {emoji} добавлена!")
    except Exception as e:
        await message.reply(f"❌ Ошибка: {e}")


@router.message(Command("reactions"))
async def cmd_reactions_list(message: Message) -> None:
    """Список доступных реакций"""
    text = "🎭 <b>Доступные реакции:</b>\n\n"
    for emoji, name in AVAILABLE_REACTIONS.items():
        text += f"{emoji} — <code>/{name}</code>\n"
    text += "\nИспользование: <code>/react 👍</code> или <code>/react like</code>"

    await message.reply(text)
