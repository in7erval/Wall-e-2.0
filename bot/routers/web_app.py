"""
Роутер для Web App (Mini App)
Telegram Web Apps позволяют запускать веб-приложения внутри Telegram
"""

from aiogram import F, Router, html
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, Message, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

# URL вашего Web App (должен быть HTTPS)
# Для разработки можно использовать ngrok или GitHub Pages
WEB_APP_URL = "https://your-username.github.io/walle-web-app/"


def create_web_app_keyboard() -> InlineKeyboardMarkup:
    """Создаёт клавиатуру с Web App кнопкой"""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🚀 Открыть Web App",
        web_app=WebAppInfo(url=WEB_APP_URL)
    )
    builder.button(
        text="📱 Открыть в браузере",
        url=WEB_APP_URL
    )
    return builder.adjust(1).as_markup()


@router.message(Command("webapp"))
async def cmd_webapp(message: Message) -> None:
    """
    Показать кнопку для открытия Web App

    Web App — это полноценное веб-приложение, которое открывается
    прямо внутри Telegram без перехода в браузер.
    """
    await message.answer(
        text=(
            "🌐 <b>Wall-e Web App</b>\n\n"
            "Нажмите на кнопку ниже, чтобы открыть приложение:\n\n"
            "• Приложение открывается внутри Telegram\n"
            "• Можно взаимодействовать с ботом через интерфейс\n"
            "• Поддерживает тёмную тему Telegram\n"
        ),
        reply_markup=create_web_app_keyboard(),
        parse_mode="HTML"
    )


@router.message(Command("webapp_info"))
async def cmd_webapp_info(message: Message) -> None:
    """Информация о Web App"""
    await message.answer(
        text=(
            "📱 <b>Telegram Web Apps (Mini Apps)</b>\n\n"
            "Web Apps — это технология от Telegram, которая позволяет:\n\n"
            "• Запускать веб-приложения внутри Telegram\n"
            "• Использовать HTML, CSS, JavaScript\n"
            "• Интегрироваться с Telegram API\n"
            "• Получать данные пользователя (с разрешения)\n"
            "• Отправлять данные обратно боту\n\n"
            "<b>Примеры использования:</b>\n"
            "• Интернет-магазины\n"
            "• Игры\n"
            "• Формы обратной связи\n"
            "• Панели управления\n"
            "• И многое другое!\n\n"
            "📚 Документация: https://core.telegram.org/bots/webapps"
        ),
        parse_mode="HTML"
    )


@router.message(F.web_app_data)
async def handle_web_app_data(message: Message) -> None:
    """
    Обработка данных, полученных из Web App

    Web App может отправить данные обратно боту через web_app_data
    """
    data = message.web_app_data.data
    await message.answer(
        text=(
            f"📥 <b>Получены данные из Web App:</b>\n\n"
            f"<code>{html.quote(data)}</code>"
        ),
        parse_mode="HTML"
    )
