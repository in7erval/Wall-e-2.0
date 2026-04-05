"""
API endpoints для Telegram Web App
"""
import hashlib
import hmac
import json
import logging
from urllib.parse import parse_qs

from aiohttp import web

from bot.config import ADMINS, BOT_TOKEN
from database import async_session_maker
from database.repositories import ChatRepository, MessageRepository, UserRepository

logger = logging.getLogger(__name__)


def verify_telegram_data(init_data: str) -> dict | None:
    """
    Проверяет подпись initData от Telegram Web App.
    Возвращает распарсенные данные или None если подпись невалидна.
    """
    try:
        parsed = parse_qs(init_data, keep_blank_values=True)
        # Извлекаем hash
        received_hash = parsed.pop("hash", [None])[0]
        if not received_hash:
            return None

        # Собираем строку для проверки
        data_check = []
        for key in sorted(parsed.keys()):
            val = parsed[key][0]
            data_check.append(f"{key}={val}")
        data_check_string = "\n".join(data_check)

        # Создаём секретный ключ
        secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
        # Проверяем подпись
        computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

        if computed_hash == received_hash:
            # Парсим user
            user_json = parsed.get("user", [None])[0]
            if user_json:
                return json.loads(user_json)
            return {}
        return None
    except Exception as e:
        logger.error(f"[API] Ошибка верификации initData: {e}")
        return None


def get_user_from_request(request: web.Request) -> dict | None:
    """Извлекает и верифицирует пользователя из заголовка X-Telegram-Init-Data"""
    init_data = request.headers.get("X-Telegram-Init-Data", "")
    if not init_data:
        return None
    return verify_telegram_data(init_data)


async def api_stats(request: web.Request) -> web.Response:
    """GET /api/stats — общая статистика бота"""
    async with async_session_maker() as session:
        user_repo = UserRepository(session)
        msg_repo = MessageRepository(session)
        chat_repo = ChatRepository(session)

        users_count = await user_repo.count()
        messages_count = await msg_repo.count()
        chats_count = await chat_repo.count_active()

    return web.json_response({
        "users": users_count,
        "messages": messages_count,
        "chats": chats_count,
    })


async def api_profile(request: web.Request) -> web.Response:
    """GET /api/profile — профиль текущего пользователя"""
    user = get_user_from_request(request)
    if user is None:
        return web.json_response({"error": "unauthorized"}, status=401)

    user_id = user.get("id")
    if not user_id:
        return web.json_response({"error": "no user id"}, status=400)

    async with async_session_maker() as session:
        user_repo = UserRepository(session)
        msg_repo = MessageRepository(session)

        db_user = await user_repo.get(user_id)
        msg_count = await msg_repo.count_by_person(user_id)

    return web.json_response({
        "id": user_id,
        "name": user.get("first_name", "") + (" " + user.get("last_name", "") if user.get("last_name") else ""),
        "username": user.get("username"),
        "is_admin": db_user.is_admin if db_user else False,
        "messages_count": msg_count,
        "registered": db_user is not None,
    })


async def api_top_users(request: web.Request) -> web.Response:
    """GET /api/top — топ пользователей по сообщениям"""
    async with async_session_maker() as session:
        msg_repo = MessageRepository(session)
        top = await msg_repo.top_users(limit=10)

    return web.json_response({
        "top": [
            {"person_id": pid, "name": name, "count": cnt}
            for pid, name, cnt in top
        ]
    })


async def api_chats(request: web.Request) -> web.Response:
    """GET /api/chats — список активных чатов (только для админов)"""
    user = get_user_from_request(request)
    if user is None:
        return web.json_response({"error": "unauthorized"}, status=401)

    user_id = str(user.get("id", ""))
    if user_id not in ADMINS:
        return web.json_response({"error": "forbidden"}, status=403)

    async with async_session_maker() as session:
        chat_repo = ChatRepository(session)
        chats = await chat_repo.get_active()

    return web.json_response({
        "chats": [
            {"id": c.id, "title": c.title, "type": c.chat_type}
            for c in chats
        ]
    })


async def api_send_message(request: web.Request) -> web.Response:
    """POST /api/send — отправка сообщения в чат (только для админов)"""
    user = get_user_from_request(request)
    if user is None:
        return web.json_response({"error": "unauthorized"}, status=401)

    user_id = str(user.get("id", ""))
    if user_id not in ADMINS:
        return web.json_response({"error": "forbidden"}, status=403)

    try:
        body = await request.json()
        chat_id = body.get("chat_id")
        text = body.get("text", "").strip()
    except Exception:
        return web.json_response({"error": "invalid json"}, status=400)

    if not chat_id or not text:
        return web.json_response({"error": "chat_id and text required"}, status=400)

    # Отправляем через бота
    from bot import bot
    try:
        await bot.send_message(chat_id=int(chat_id), text=text)
        return web.json_response({"ok": True})
    except Exception as e:
        logger.error(f"[API] Ошибка отправки: {e}")
        return web.json_response({"error": str(e)}, status=500)


def setup_api_routes(app: web.Application):
    """Регистрация API routes"""
    app.router.add_get("/api/stats", api_stats)
    app.router.add_get("/api/profile", api_profile)
    app.router.add_get("/api/top", api_top_users)
    app.router.add_get("/api/chats", api_chats)
    app.router.add_post("/api/send", api_send_message)
