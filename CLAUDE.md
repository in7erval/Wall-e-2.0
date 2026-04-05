# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Wall-e 2.0 — Telegram-бот на Python (aiogram 3.x + SQLAlchemy 2.0 async). Работает через webhook с self-signed SSL на выделенном сервере.

## Commands

```bash
# Запуск (требуется .env и SSL-сертификаты)
python app.py

# Docker
docker-compose up --build

# Генерация SSL-сертификатов (CN и SAN должны совпадать с IP сервера)
bash ssl_generate.sh

# Установка зависимостей
pip install -r requirements.txt

# Линтинг и форматирование
ruff check .
black .
isort .
mypy .

# Тесты
pytest
pytest tests/test_specific.py -v
```

## Environment Variables (.env)

Обязательные: `BOT_TOKEN`, `ADMINS` (список ID через запятую), `ip` (публичный IP сервера для webhook), `DB_USER`, `DB_PASS`, `DB_NAME`, `DB_HOST`.

## Deployment

Сервер: Ubuntu 72.56.245.135, PostgreSQL: 72.56.243.140. SSH: `ssh -i ~/.ssh/wall-e-server root@72.56.245.135`. Бот на сервере: `/root/Wall-e-2.0/`, venv: `.venv/`.

```bash
# Деплой файлов
rsync -avz --exclude='.venv' --exclude='__pycache__' --exclude='.git' --exclude='.idea' \
  -e "ssh -i ~/.ssh/wall-e-server" ./bot/ root@72.56.245.135:/root/Wall-e-2.0/bot/

# Перезапуск
ssh -i ~/.ssh/wall-e-server root@72.56.245.135 \
  "ps aux | grep app.py | grep -v grep | awk '{print \$2}' | xargs -r kill; \
   sleep 2; cd /root/Wall-e-2.0 && .venv/bin/python app.py > bot.log 2>&1 &"

# Логи
ssh -i ~/.ssh/wall-e-server root@72.56.245.135 "tail -50 /root/Wall-e-2.0/bot.log"
```

## Architecture

### Точка входа
`app.py` → `bot/main.py:run_webhook()` — инициализация БД, регистрация роутеров/фильтров/middleware, запуск aiohttp webhook-сервера с SSL через `SimpleRequestHandler`.

### bot/ — ядро бота
- `bot/__init__.py` — создание `Bot` (с `DefaultBotProperties`), `Dispatcher`, `ssl_context`
- `bot/config.py` — конфигурация из `.env` через `environs`
- `bot/handlers.py` — `register_routers(dp)` — подключение всех роутеров
- `bot/services.py` — `on_startup`/`on_shutdown`, установка команд бота, уведомление админов
- `bot/filters/__init__.py` — `AdminFilter` (по списку ID из ADMINS)

### Middleware (bot/middlewares/)
Регистрация в `setup_middlewares(dp)`:
- `dp.update.outer_middleware(RepositoryMiddleware())` — инъекция `repos` dict для всех апдейтов
- `dp.update.outer_middleware(BigBrotherMiddleware())` — логирование сообщений в БД + автотрекинг чатов
- `dp.message.middleware(ThrottlingMiddleware())` — антиспам (только для обработанных сообщений)

**Важно**: `outer_middleware` срабатывает на ВСЕ апдейты, `dp.message.middleware` — только когда есть подходящий хендлер.

### bot/routers/ — обработчики команд
- `users.py` — /start, /help, клавиатуры (main_keyboard, generate_keyboard), кнопочные хендлеры
- `entertainment.py` — генерация текста, /get_fox, /get_cat, /tts, вероятность, выбор, кубик, бутерброд (FSM)
- `games.py` — крестики-нолики (PvP/PvE), камень-ножницы-бумага, виселица (FSM), угадай число (FSM)
- `content.py` — /joke, /quote, /horoscope, /fact, /bigtext, шар-предсказатель, рейтинг, /who, /match
- `groups.py` — /del (удаление сообщений), `my_chat_member` (трекинг добавления/удаления бота)
- `admin.py` — /send_msg (скрытая команда, только ADMINS, FSM с inline-клавиатурой чатов)
- `photo_rectangles.py` — обработка фото прямоугольниками
- `reactions.py`, `web_app.py`, `forum.py` — отключены (закомментированы в handlers.py)

### database/ — слой БД (SQLAlchemy 2.0 async + asyncpg)
- `database/models.py` — `Base` (единственный DeclarativeBase), модели: `User`, `Message`, `Chat`, `InlinePhoto`, `RectanglesImg` с `TimeStampMixin`
- `database/repositories.py` — паттерн Repository: `UserRepository`, `MessageRepository`, `ChatRepository`, `InlinePhotoRepository`, `RectanglesImgRepository`
- `database/middleware.py` — `RepositoryMiddleware` (инъекция `repos` dict в data хендлеров)
- `database/__init__.py` — `engine`, `async_session_maker`, `on_startup()` (create_all через Base из models.py)

**Важно**: `Base` определён ТОЛЬКО в `database/models.py`. В `database/__init__.py` он импортируется оттуда для `create_all`.

### Паттерн доступа к БД в хендлерах
Хендлеры получают `repos: dict` через `RepositoryMiddleware`. Ключи: `user`, `message`, `chat`, `photo`, `rectangles`.
```python
@router.message(CommandStart())
async def cmd_start(message: Message, repos: dict[str, Any]):
    user_repo: UserRepository = repos['user']
    user = await user_repo.get(message.from_user.id)
```

### utils/ — переиспользуемые утилиты
- `utils/misc/` — генерация текста (`generate.py`), обработка фото (`photos/rectangles.py`), вероятность, выбор
- `utils/simplex/` — симплекс-метод (не подключён к боту, на будущее)

## Key Patterns

- **FSM** (finite state machine) используется для многошаговых команд: бутерброд, виселица, угадай число, /send_msg
- **Inline-клавиатуры** с callback_data для игр и интерактивных команд. Префиксы: `ttt_` (крестики-нолики), `rps_` (КНБ), `hm_` (виселица), `horo_` (гороскоп), `adm_send_` (админ отправка)
- **Детерминированный рандом** по дате для гороскопа, /who, /match — результат стабилен в течение дня
- **Webhook с self-signed SSL**: CN и SAN в сертификате должны совпадать с IP сервера. При деплое не перезаписывать серверные `webhook_cert.pem`/`webhook_pkey.pem`

## Language

Комментарии и логирование в коде на русском языке.