# Wall-e 2.0

<p align="left">
<img src="https://raster.shields.io/github/last-commit/in7erval/Wall-e-2.0">
<img src="https://raster.shields.io/badge/made_by-in7erval-blue">
<img src="https://img.shields.io/badge/Python-3.10+-1f425f.svg">
<img src="https://raster.shields.io/github/repo-size/in7erval/Wall-e-2.0">
</p>

> Upgraded version of [Wall-e](https://github.com/in7erval/Wall-e):
> * **aiogram 3.x** (async Telegram Bot framework)
> * **SQLAlchemy 2.0** (async ORM with asyncpg)
> * **Webhook** with self-signed SSL
> * **Alembic** for database migrations
> * **Docker** support
>
> *Time goes by and I'm not getting younger...*

## Features

### Games
- **Крестики-нолики** — PvP and PvE with inline keyboard
- **Камень-ножницы-бумага** — classic RPS game
- **Виселица** — hangman with inline alphabet keyboard
- **Угадай число** — number guessing game

### Content
- **Анекдоты** — random jokes
- **Цитаты** — quotes from Forismatic API
- **Гороскоп** — daily horoscope with zodiac sign selection
- **Факты** — interesting facts
- **Шар-предсказатель** — magic 8-ball
- **Рейтинг** — rate anything on a 1-10 scale

### Social
- **/who** — "Who is today's [role]?" (deterministic random per day)
- **/match** — compatibility percentage between users
- **/bigtext** — render text in large emoji font

### Entertainment
- **Text generation** — Markov chain from chat history
- **TTS** — text-to-speech via Google TTS
- **Photos** — random fox/cat photos from APIs
- **Dice, probability, choice** — fun random generators
- **Photo rectangles** — artistic photo processing

### Groups
- Auto-tracking of chats where the bot is added
- Message deletion for admins
- Message logging (Big Brother middleware)

### Admin
- **/send_msg** — send message to any tracked chat via interactive inline keyboard

## Tech Stack

| Component | Technology |
|-----------|------------|
| Bot framework | aiogram 3.x |
| Database | PostgreSQL + SQLAlchemy 2.0 async |
| Migrations | Alembic |
| HTTP client | aiohttp |
| TTS | gTTS |
| Image processing | Pillow, scikit-image, numpy |
| Linting | ruff |
| Containerization | Docker |

## Quick Start

```bash
# Clone
git clone https://github.com/in7erval/Wall-e-2.0.git
cd Wall-e-2.0

# Setup
cp .env.example .env  # fill in BOT_TOKEN, ADMINS, ip, DB_*
pip install -r requirements.txt

# Generate SSL certificates (CN/SAN must match server IP)
bash ssl_generate.sh

# Run
python app.py
```

### Docker

```bash
docker compose up --build
```

## Project Structure

```
Wall-e-2.0/
├── app.py                  # Entry point
├── bot/
│   ├── __init__.py         # Bot, Dispatcher, ssl_context
│   ├── config.py           # .env configuration
│   ├── handlers.py         # Router registration
│   ├── services.py         # Startup/shutdown, bot commands
│   ├── filters/            # AdminFilter
│   ├── middlewares/         # BigBrother, Throttling
│   └── routers/
│       ├── users.py        # /start, /help, keyboards
│       ├── entertainment.py # Text gen, TTS, animals, dice
│       ├── games.py        # TicTacToe, RPS, Hangman, Guess
│       ├── content.py      # Jokes, quotes, horoscope, facts
│       ├── groups.py       # Group management
│       ├── admin.py        # /send_msg (admin only)
│       └── photo_rectangles.py
├── database/
│   ├── __init__.py         # Engine, session, on_startup
│   ├── models.py           # User, Message, Chat, InlinePhoto, RectanglesImg
│   ├── repositories.py     # Repository pattern
│   └── middleware.py        # RepositoryMiddleware (DI)
├── utils/
│   ├── misc/               # Markov chain, photos, random helpers
│   └── simplex/            # Simplex method (standalone)
├── alembic/                # Database migrations
├── Dockerfile
├── docker-compose.yml
└── ruff.toml
```

## Commands

Send `/help` to the bot or check [bot/services.py](bot/services.py) for the full command list.

You can try me [here](https://t.me/testIntervalbot)!

![Wall-e photo](assets/pic.jpg)