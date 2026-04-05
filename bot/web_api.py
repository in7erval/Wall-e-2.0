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
from database.repositories import ChatRepository, MediaMessageRepository, MessageRepository, UserRepository

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

        data_check = []
        for key in sorted(parsed.keys()):
            val = parsed[key][0]
            data_check.append(f"{key}={val}")
        data_check_string = "\n".join(data_check)

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


def is_admin(data: dict | None) -> bool:
    """Проверяет, является ли пользователь админом"""
    if not data:
        return False
    user = data.get("user", {})
    return str(user.get("id", "")) in ADMINS


async def api_stats(request: web.Request) -> web.Response:
    """
    GET /api/stats — статистика.
    Авторизованный пользователь видит данные только по своим чатам.
    Админ видит глобальную статистику.
    Без авторизации — ничего.
    """
    data = parse_request(request)
    if data is None:
        return web.json_response({"error": "unauthorized"}, status=401)

    admin = is_admin(data)
    user_id = data.get("user", {}).get("id")

    async with async_session_maker() as session:
        msg_repo = MessageRepository(session)

        if admin:
            user_repo = UserRepository(session)
            chat_repo = ChatRepository(session)
            users_count = await user_repo.count()
            messages_count = await msg_repo.count()
            chats_count = await chat_repo.count_active()
        else:
            # Находим чаты, в которых пользователь состоит
            user_chat_ids = await msg_repo.get_chat_ids_by_person(user_id) if user_id else []
            if user_chat_ids:
                users_count = await msg_repo.count_unique_users(chat_ids=user_chat_ids)
                messages_count = await msg_repo.count_in_chats(user_chat_ids)
                chats_count = len(user_chat_ids)
            else:
                users_count = 0
                messages_count = 0
                chats_count = 0

    return web.json_response({
        "users": users_count,
        "messages": messages_count,
        "chats": chats_count,
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

    async with async_session_maker() as session:
        user_repo = UserRepository(session)
        msg_repo = MessageRepository(session)

        db_user = await user_repo.get(user_id)
        # Считаем сообщения во всех чатах пользователя
        msg_count = await msg_repo.count_by_person(user_id)

    return web.json_response({
        "id": user_id,
        "name": user.get("first_name", "") + (" " + user.get("last_name", "") if user.get("last_name") else ""),
        "username": user.get("username"),
        "is_admin": is_admin(data),
        "messages_count": msg_count,
        "registered": db_user is not None,
    })


async def api_top_users(request: web.Request) -> web.Response:
    """
    GET /api/top — топ пользователей.
    Обычный пользователь видит топ только среди своих чатов.
    Админ видит глобальный топ.
    """
    data = parse_request(request)
    if data is None:
        return web.json_response({"error": "unauthorized"}, status=401)

    admin = is_admin(data)
    user_id = data.get("user", {}).get("id")

    async with async_session_maker() as session:
        msg_repo = MessageRepository(session)

        if admin:
            top = await msg_repo.top_users(limit=10)
        else:
            user_chat_ids = await msg_repo.get_chat_ids_by_person(user_id) if user_id else []
            if user_chat_ids:
                top = await msg_repo.top_users(limit=10, chat_ids=user_chat_ids)
            else:
                top = []

    return web.json_response({
        "top": [
            {"person_id": pid, "name": name, "count": cnt}
            for pid, name, cnt in top
        ]
    })


async def api_chats(request: web.Request) -> web.Response:
    """GET /api/chats — список активных чатов (только для админов)"""
    data = parse_request(request)
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


async def api_messages(request: web.Request) -> web.Response:
    """GET /api/messages?chat_id=X&offset=0&limit=50 — единая лента сообщений чата (только для админов)"""
    data = parse_request(request)
    if not is_admin(data):
        return web.json_response({"error": "forbidden"}, status=403)

    try:
        chat_id = int(request.query["chat_id"])
    except (KeyError, ValueError):
        return web.json_response({"error": "chat_id required"}, status=400)

    offset = int(request.query.get("offset", "0"))
    limit = min(int(request.query.get("limit", "50")), 100)

    async with async_session_maker() as session:
        msg_repo = MessageRepository(session)
        media_repo = MediaMessageRepository(session)

        # Загружаем все текстовые и медиа для этого чата
        text_messages = await msg_repo.get_by_chat_id(chat_id)
        media_messages = await media_repo.get_by_chat_id(chat_id)

        # Объединяем в единый список
        combined = []
        for m in text_messages:
            combined.append({
                "id": m.id,
                "type": "text",
                "name": m.name,
                "text": m.message,
                "person_id": m.person_id,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            })
        for m in media_messages:
            combined.append({
                "id": m.id,
                "type": m.media_type,
                "name": m.name,
                "person_id": m.person_id,
                "duration": m.duration,
                "file_size": m.file_size,
                "local_path": m.local_path,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            })

        # Сортировка по времени (новые первыми)
        combined.sort(key=lambda x: x["created_at"] or "", reverse=True)
        total = len(combined)
        page = combined[offset:offset + limit]

    return web.json_response({
        "messages": page,
        "total": total,
        "offset": offset,
        "limit": limit,
    })


async def api_send_message(request: web.Request) -> web.Response:
    """POST /api/send — отправка сообщения в чат (только для админов)"""
    data = parse_request(request)
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


async def api_media(request: web.Request) -> web.Response:
    """GET /api/media?chat_id=X&offset=0&limit=50&type=voice|video_note — медиасообщения (только для админов)"""
    data = parse_request(request)
    if not is_admin(data):
        return web.json_response({"error": "forbidden"}, status=403)

    try:
        chat_id = int(request.query["chat_id"])
    except (KeyError, ValueError):
        return web.json_response({"error": "chat_id required"}, status=400)

    offset = int(request.query.get("offset", "0"))
    limit = min(int(request.query.get("limit", "50")), 100)
    media_type = request.query.get("type")  # voice, video_note или None (все)

    async with async_session_maker() as session:
        media_repo = MediaMessageRepository(session)
        items = await media_repo.get_by_chat_id(chat_id, media_type=media_type)
        total = len(items)
        items = items[offset:offset + limit]

    return web.json_response({
        "media": [
            {
                "id": m.id,
                "name": m.name,
                "person_id": m.person_id,
                "media_type": m.media_type,
                "file_id": m.file_id,
                "duration": m.duration,
                "file_size": m.file_size,
                "local_path": m.local_path,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in items
        ],
        "total": total,
        "offset": offset,
        "limit": limit,
    })


def setup_api_routes(app: web.Application):
    """Регистрация API routes"""
    app.router.add_get("/api/stats", api_stats)
    app.router.add_get("/api/profile", api_profile)
    app.router.add_get("/api/top", api_top_users)
    app.router.add_get("/api/chats", api_chats)
    app.router.add_get("/api/messages", api_messages)
    app.router.add_post("/api/send", api_send_message)
    app.router.add_get("/api/media", api_media)
