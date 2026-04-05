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
    Возвращает dict с ключами 'user' и 'chat' (если есть) или None.
    """
    try:
        parsed = parse_qs(init_data, keep_blank_values=True)
        received_hash = parsed.pop("hash", [None])[0]
        if not received_hash:
            return None

        # Собираем строку для проверки
        data_check = []
        for key in sorted(parsed.keys()):
            val = parsed[key][0]
            data_check.append(f"{key}={val}")
        data_check_string = "\n".join(data_check)

        # Проверяем подпись
        secret_key = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
        computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

        if computed_hash != received_hash:
            return None

        result = {}
        user_json = parsed.get("user", [None])[0]
        if user_json:
            result["user"] = json.loads(user_json)
        chat_json = parsed.get("chat", [None])[0]
        if chat_json:
            result["chat"] = json.loads(chat_json)
        # chat_type передаётся отдельным полем
        chat_type = parsed.get("chat_type", [None])[0]
        if chat_type:
            result["chat_type"] = chat_type
        return result
    except Exception as e:
        logger.error(f"[API] Ошибка верификации initData: {e}")
        return None


def parse_request(request: web.Request) -> dict | None:
    """Извлекает и верифицирует данные из заголовка X-Telegram-Init-Data"""
    init_data = request.headers.get("X-Telegram-Init-Data", "")
    if not init_data:
        return None
    return verify_telegram_data(init_data)


def is_admin(data: dict) -> bool:
    """Проверяет, является ли пользователь админом"""
    user = data.get("user", {})
    return str(user.get("id", "")) in ADMINS


async def api_stats(request: web.Request) -> web.Response:
    """GET /api/stats — статистика (по чату из initData или глобальная)"""
    data = parse_request(request)
    admin = is_admin(data) if data else False

    chat = data.get("chat") if data else None
    chat_id = chat.get("id") if chat else None

    async with async_session_maker() as session:
        msg_repo = MessageRepository(session)

        if chat_id:
            # Из группового чата — показываем статистику этого чата
            users_count = await msg_repo.count_unique_users(chat_id=chat_id)
            messages_count = await msg_repo.count_by_chat_id(chat_id)
            chats_count = 1
        elif admin:
            # Админ — глобальная статистика
            user_repo = UserRepository(session)
            chat_repo = ChatRepository(session)
            users_count = await user_repo.count()
            messages_count = await msg_repo.count()
            chats_count = await chat_repo.count_active()
        elif data:
            # Авторизованный пользователь из личного чата
            user_id = data.get("user", {}).get("id")
            users_count = 1
            messages_count = await msg_repo.count_by_person(user_id) if user_id else 0
            chats_count = 0
        else:
            # Без авторизации (открыто по URL) — общая статистика без деталей
            user_repo = UserRepository(session)
            chat_repo = ChatRepository(session)
            users_count = await user_repo.count()
            messages_count = await msg_repo.count()
            chats_count = await chat_repo.count_active()

    return web.json_response({
        "users": users_count,
        "messages": messages_count,
        "chats": chats_count,
        "chat_title": chat.get("title") if chat else None,
        "is_admin": admin,
    })


async def api_profile(request: web.Request) -> web.Response:
    """GET /api/profile — профиль текущего пользователя"""
    data = parse_request(request)
    if data is None:
        return web.json_response({"error": "unauthorized"}, status=401)

    user = data.get("user", {})
    user_id = user.get("id")
    if not user_id:
        return web.json_response({"error": "no user id"}, status=400)

    chat = data.get("chat")
    chat_id = chat.get("id") if chat else None

    async with async_session_maker() as session:
        user_repo = UserRepository(session)
        msg_repo = MessageRepository(session)

        db_user = await user_repo.get(user_id)
        msg_count = await msg_repo.count_by_person(user_id, chat_id=chat_id)

    return web.json_response({
        "id": user_id,
        "name": user.get("first_name", "") + (" " + user.get("last_name", "") if user.get("last_name") else ""),
        "username": user.get("username"),
        "is_admin": is_admin(data),
        "messages_count": msg_count,
        "registered": db_user is not None,
    })


async def api_top_users(request: web.Request) -> web.Response:
    """GET /api/top — топ пользователей (по чату из initData)"""
    data = parse_request(request)
    admin = is_admin(data) if data else False

    chat = data.get("chat") if data else None
    chat_id = chat.get("id") if chat else None

    async with async_session_maker() as session:
        msg_repo = MessageRepository(session)
        if chat_id:
            # Из группы — топ этого чата
            top = await msg_repo.top_users(limit=10, chat_id=chat_id)
        elif admin:
            # Админ — глобальный топ
            top = await msg_repo.top_users(limit=10)
        else:
            # Без авторизации или обычный пользователь — глобальный топ
            top = await msg_repo.top_users(limit=10)

    return web.json_response({
        "top": [
            {"person_id": pid, "name": name, "count": cnt}
            for pid, name, cnt in top
        ]
    })


async def api_chats(request: web.Request) -> web.Response:
    """GET /api/chats — список активных чатов (только для админов)"""
    data = parse_request(request)
    if data is None:
        return web.json_response({"error": "unauthorized"}, status=401)

    if not is_admin(data):
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
    data = parse_request(request)
    if data is None:
        return web.json_response({"error": "unauthorized"}, status=401)

    if not is_admin(data):
        return web.json_response({"error": "forbidden"}, status=403)

    try:
        body = await request.json()
        chat_id = body.get("chat_id")
        text = body.get("text", "").strip()
    except Exception:
        return web.json_response({"error": "invalid json"}, status=400)

    if not chat_id or not text:
        return web.json_response({"error": "chat_id and text required"}, status=400)

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
