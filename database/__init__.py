"""
База данных (aiogram 3.x + SQLAlchemy 2.x async + asyncpg)
"""
import logging
from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from bot.config import DB_USER, POSTGRES_URI

logger = logging.getLogger(__name__)

# Создаём async engine с asyncpg
engine = create_async_engine(
    POSTGRES_URI.replace('postgresql://', 'postgresql+asyncpg://'),
    echo=False
)

# Сессия
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def on_startup():
    """Инициализация БД при запуске"""
    logger.info("Подключение к PostgreSQL")
    # Проверка подключения
    async with engine.connect() as conn:
        logger.info("БД подключена")

    # Создание таблиц — импортируем Base из models, чтобы все модели были видны
    async with engine.begin() as conn:
        from database.models import Base
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Таблицы созданы/проверены")

    # Гарантируем права на все таблицы (managed PostgreSQL может сбрасывать)
    async with engine.begin() as conn:
        await conn.execute(text(
            f"GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {DB_USER}"
        ))
        await conn.execute(text(
            f"GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {DB_USER}"
        ))
    logger.info("Права на таблицы подтверждены")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Получение сессии БД"""
    async with async_session_maker() as session:
        yield session


async def get_repository(session: AsyncSession, repo_class):
    """Фабрика репозиториев"""
    return repo_class(session)
