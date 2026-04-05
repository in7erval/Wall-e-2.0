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

### Web App (Mini App)
- **Stats** — message and user statistics per chat
- **Profile** — user card with message count and status
- **2048** — mini-game with swipe support
- **Admin panel** — send messages to chats, browse message history

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
| Web App | Telegram Mini Apps + aiohttp static |
| CI/CD | GitHub Actions → ghcr.io |
| Linting | ruff |
| Containerization | Docker |

## Deployment

### Production (Docker image from ghcr.io)

The recommended way to deploy. No source code needed on the server — just pull the pre-built image.

```bash
# 1. Create a directory with config files
mkdir ~/walle-bot && cd ~/walle-bot

# 2. Create .env with required variables
cat > .env << EOF
BOT_TOKEN=your_bot_token
ADMINS=123456789,987654321
ip=your.server.ip
DB_USER=your_db_user
DB_PASS=your_db_pass
DB_NAME=your_db_name
DB_HOST=your_db_host
EOF

# 3. Generate SSL certificates (CN/SAN must match server IP)
openssl req -newkey rsa:2048 -sha256 -nodes \
  -keyout webhook_pkey.pem -x509 -days 3650 \
  -out webhook_cert.pem \
  -subj "/CN=your.server.ip" \
  -addext "subjectAltName=IP:your.server.ip"

# 4. Create docker-compose.yml
cat > docker-compose.yml << EOF
services:
  walle:
    container_name: bot-walle
    image: ghcr.io/in7erval/wall-e-2.0:\${IMAGE_TAG:-main}
    restart: always
    env_file:
      - .env
    network_mode: host
    volumes:
      - ./temp_images:/app/temp_images
      - ./webhook_cert.pem:/app/webhook_cert.pem:ro
      - ./webhook_pkey.pem:/app/webhook_pkey.pem:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
EOF

# 5. Pull and start
docker compose pull
docker compose up -d
```

### Update to latest version

```bash
cd ~/walle-bot
docker compose pull
docker compose up -d
```

### Deploy a specific version

```bash
IMAGE_TAG=v1.0.0 docker compose pull
IMAGE_TAG=v1.0.0 docker compose up -d
```

### Local development

```bash
git clone https://github.com/in7erval/Wall-e-2.0.git
cd Wall-e-2.0

cp .env.dist .env  # fill in required variables
pip install -r requirements.txt
bash ssl_generate.sh

python app.py
```

### Local Docker build

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
│   ├── web_api.py          # REST API for Web App
│   └── routers/
│       ├── users.py        # /start, /help, keyboards
│       ├── entertainment.py # Text gen, TTS, animals, dice
│       ├── games.py        # TicTacToe, RPS, Hangman, Guess
│       ├── content.py      # Jokes, quotes, horoscope, facts
│       ├── groups.py       # Group management
│       ├── admin.py        # /send_msg (admin only)
│       ├── web_app.py      # /webapp (Mini App)
│       └── photo_rectangles.py
├── database/
│   ├── __init__.py         # Engine, session, on_startup
│   ├── models.py           # User, Message, Chat, InlinePhoto, RectanglesImg
│   ├── repositories.py     # Repository pattern
│   └── middleware.py        # RepositoryMiddleware (DI)
├── utils/
│   ├── misc/               # Markov chain, photos, random helpers
│   └── simplex/            # Simplex method (standalone)
├── web_app/                # Telegram Mini App (HTML/CSS/JS)
├── alembic/                # Database migrations
├── .github/workflows/      # CI/CD (build & push to ghcr.io)
├── Dockerfile
├── docker-compose.yml      # Local development
├── docker-compose.prod.yml # Production (image from ghcr.io)
└── ruff.toml
```

## Commands

Send `/help` to the bot or check [bot/services.py](bot/services.py) for the full command list.

You can try me [here](https://t.me/testIntervalbot)!

![Wall-e photo](assets/pic.jpg)