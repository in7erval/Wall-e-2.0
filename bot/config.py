"""
Конфигурация бота Wall-e 2.0
"""
import os

from environs import Env

env = Env()
env.read_env()

# Telegram
BOT_TOKEN = env.str("BOT_TOKEN")

# Admins
ADMINS = env.list("ADMINS")

# Server IP
IP = env.str("ip")

# Database
DB_USER = env.str("DB_USER")
DB_PASS = env.str("DB_PASS")
DB_NAME = env.str("DB_NAME")
DB_HOST = env.str("DB_HOST", "192.168.0.4")
POSTGRES_URI = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

# SSL Certificates
WEBHOOK_SSL_CERT = "webhook_cert.pem"
WEBHOOK_SSL_PRIV = "webhook_pkey.pem"

# Webhook settings
WEBHOOK_HOST = f"https://{IP}"
WEBHOOK_PORT = 8443
WEBHOOK_PATH = f"/bot/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}:{WEBHOOK_PORT}{WEBHOOK_PATH}"

# Webserver settings
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("WEBAPP_PORT", "3001"))

# Bot settings
BANNED_USERS = []
CHANNELS = [-1001733004987]
ALLOWED_USERS = []
