"""
SQLAlchemy 2.x модели для Wall-e 2.0
"""
from datetime import datetime, timezone

from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass


class TimeStampMixin:
    """Миксин для автоматического created_at / updated_at"""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )


class User(Base, TimeStampMixin):
    """Модель пользователя"""
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_admin: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, name='{self.name}', is_admin={self.is_admin})>"


class Message(Base, TimeStampMixin):
    """Модель сообщения для генерации текста"""
    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    person_id: Mapped[int] = mapped_column(BigInteger, index=True)

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, chat_id={self.chat_id}, person_id={self.person_id})>"


class InlinePhoto(Base, TimeStampMixin):
    """Модель для inline фото"""
    __tablename__ = 'inline_photos'

    id: Mapped[str] = mapped_column(String(255), primary_key=True)
    query_text: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<InlinePhoto(id='{self.id}', query='{self.query_text}')>"


class Chat(Base, TimeStampMixin):
    """Модель чата, в котором состоит бот"""
    __tablename__ = 'chats'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    chat_type: Mapped[str] = mapped_column(String(20), nullable=False, default='group')
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    def __repr__(self) -> str:
        return f"<Chat(id={self.id}, title='{self.title}', type='{self.chat_type}', active={self.is_active})>"


class MediaMessage(Base, TimeStampMixin):
    """Модель для голосовых сообщений и видеосообщений (кружков)"""
    __tablename__ = 'media_messages'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    person_id: Mapped[int] = mapped_column(BigInteger, index=True)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    media_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 'voice' или 'video_note'
    file_id: Mapped[str] = mapped_column(String(255), nullable=False)
    file_unique_id: Mapped[str] = mapped_column(String(255), nullable=False)
    duration: Mapped[int | None] = mapped_column(Integer, nullable=True)
    file_size: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    local_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    def __repr__(self) -> str:
        return f"<MediaMessage(id={self.id}, chat_id={self.chat_id}, type='{self.media_type}')>"


class RectanglesImg(Base, TimeStampMixin):
    """Модель для изображений с прямоугольниками"""
    __tablename__ = 'rectangles_img'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    image_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    def __repr__(self) -> str:
        return f"<RectanglesImg(id={self.id}, image_id='{self.image_id}')>"
