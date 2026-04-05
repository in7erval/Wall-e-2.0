"""
Роутер для админских команд
"""
import logging
from typing import TYPE_CHECKING, Any

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot.config import ADMINS

if TYPE_CHECKING:
    from database.repositories import ChatRepository

logger = logging.getLogger(__name__)

router = Router()


class SendMsgState(StatesGroup):
    waiting_for_message = State()


def _is_admin(user_id: int) -> bool:
    return str(user_id) in ADMINS


def _chat_type_emoji(chat_type: str) -> str:
    return {'group': '👥', 'supergroup': '👥', 'channel': '📢'}.get(chat_type, '💬')


@router.message(Command("send_msg"))
async def cmd_send_msg(message: Message, repos: dict[str, Any], state: FSMContext) -> None:
    """Отправка сообщения в чат (только для админов)"""
    if not _is_admin(message.from_user.id):
        return

    # Быстрый режим: /send_msg <chat_id> <текст>
    args = message.text.split(maxsplit=2)
    if len(args) >= 3:
        chat_id = args[1]
        text = args[2]
        try:
            await message.bot.send_message(chat_id, text)
            await message.reply(f"✅ Сообщение отправлено в {chat_id}")
        except Exception as e:
            await message.reply(f"❌ Ошибка: {e}")
        return

    # Интерактивный режим: показываем список чатов
    chat_repo: ChatRepository = repos.get('chat')
    if not chat_repo:
        await message.reply("❌ Репозиторий чатов недоступен")
        return

    chats = await chat_repo.get_active()

    if not chats:
        await message.reply(
            "📭 Нет известных чатов.\n\n"
            "Бот автоматически запоминает чаты, в которых состоит.\n"
            "Быстрый режим: /send_msg [chat_id] [текст]"
        )
        return

    buttons = []
    for chat in chats:
        emoji = _chat_type_emoji(chat.chat_type)
        title = chat.title or str(chat.id)
        buttons.append([InlineKeyboardButton(
            text=f"{emoji} {title}",
            callback_data=f"adm_send_{chat.id}"
        )])
    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="adm_send_cancel")])

    await message.answer(
        "📤 Выберите чат для отправки:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


@router.callback_query(F.data.startswith("adm_send_") & ~F.data.startswith("adm_send_cancel"))
async def on_chat_selected(call: CallbackQuery, state: FSMContext) -> None:
    """Админ выбрал чат"""
    if not _is_admin(call.from_user.id):
        await call.answer("⛔")
        return

    chat_id = call.data.replace("adm_send_", "")

    # Получаем название чата из кнопки
    chat_title = "?"
    if call.message.reply_markup:
        for row in call.message.reply_markup.inline_keyboard:
            for btn in row:
                if btn.callback_data == call.data:
                    chat_title = btn.text
                    break

    await state.set_state(SendMsgState.waiting_for_message)
    await state.update_data(chat_id=chat_id, chat_title=chat_title)

    await call.message.edit_text(
        f"📤 Отправка в {chat_title}\n\n"
        "Введите сообщение (или /cancel для отмены):"
    )


@router.callback_query(F.data == "adm_send_cancel")
async def on_send_cancel(call: CallbackQuery, state: FSMContext) -> None:
    """Отмена отправки"""
    await state.clear()
    await call.message.edit_text("❌ Отправка отменена")


@router.message(SendMsgState.waiting_for_message, Command("cancel"))
async def cancel_send(message: Message, state: FSMContext) -> None:
    """Отмена через /cancel"""
    await state.clear()
    await message.reply("❌ Отправка отменена")


@router.message(SendMsgState.waiting_for_message)
async def process_message_to_send(message: Message, state: FSMContext) -> None:
    """Получили текст — отправляем в выбранный чат"""
    if not _is_admin(message.from_user.id):
        return

    data = await state.get_data()
    chat_id = data.get('chat_id')
    chat_title = data.get('chat_title', chat_id)

    await state.clear()

    try:
        await message.bot.send_message(int(chat_id), message.text)
        await message.reply(f"✅ Сообщение отправлено в {chat_title}")
        logger.info(f"Admin {message.from_user.id} отправил сообщение в {chat_id}")
    except Exception as e:
        await message.reply(f"❌ Ошибка: {e}")
        logger.error(f"Ошибка отправки в {chat_id}: {e}")
