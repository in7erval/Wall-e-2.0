"""
Wall-e 2.0 - Telegram Bot (aiogram 3.x)
Точка входа
"""
import asyncio

from bot.main import run_webhook

if __name__ == '__main__':
    asyncio.run(run_webhook())
