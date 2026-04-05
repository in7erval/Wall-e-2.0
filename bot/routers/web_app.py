"""
Роутер для Web App (Telegram Mini App)
"""

from aiogram import F, Router, html
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, Message, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

# URL Web App — Let's Encrypt SSL на порту 443
WEB_APP_URL = "https://walle-bot.duckdns.org/webapp/index.html"


def create_web_app_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с Web App кнопкой"""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🚀 Открыть Web App",
        web_app=WebAppInfo(url=WEB_APP_URL)
    )
    return builder.as_markup()


@router.message(Command("webapp"))
async def cmd_webapp(message: Message) -> None:
    """Открыть Web App"""
    await message.answer(
        text=(
            "🌐 <b>Wall-e Web App</b>\n\n"
            "Статистика, профиль, игра 2048 и админ-панель — "
            "всё в одном приложении внутри Telegram."
        ),
        reply_markup=create_web_app_keyboard(),
    )


@router.message(F.web_app_data)
async def handle_web_app_data(message: Message) -> None:
    """Обработка данных из Web App"""
    data = message.web_app_data.data
    await message.answer(
        f"📥 <b>Данные из Web App:</b>\n\n<code>{html.quote(data)}</code>",
    )
