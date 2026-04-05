"""
Репозитории для работы с БД (SQLAlchemy 2.x async)
"""

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Chat, InlinePhoto, Message, RectanglesImg, User


class UserRepository:
    """Репозиторий для работы с пользователями"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, user_id: int) -> User | None:
        """Получить пользователя по ID"""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, user_id: int, name: str, is_admin: bool = False) -> User:
        """Создать нового пользователя"""
        user = User(id=user_id, name=name, is_admin=is_admin)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_admin(self, user_id: int, is_admin: bool) -> User | None:
        """Обновить статус администратора"""
        user = await self.get(user_id)
        if user:
            user.is_admin = is_admin
            await self.session.commit()
            await self.session.refresh(user)
        return user

    async def add_or_update(self, user_id: int, name: str, is_admin: bool = False) -> User:
        """Добавить или обновить пользователя"""
        user = await self.get(user_id)
        if user:
            user.name = name
            user.is_admin = is_admin
            await self.session.commit()
            await self.session.refresh(user)
            return user
        return await self.create(user_id, name, is_admin)

    async def delete(self, user_id: int) -> bool:
        """Удалить пользователя"""
        user = await self.get(user_id)
        if user:
            await self.session.delete(user)
            await self.session.commit()
            return True
        return False

    async def get_all(self) -> list[User]:
        """Получить всех пользователей"""
        result = await self.session.execute(select(User))
        return list(result.scalars().all())

    async def get_all_admins(self) -> list[User]:
        """Получить всех администраторов"""
        result = await self.session.execute(
            select(User).where(User.is_admin)
        )
        return list(result.scalars().all())

    async def count(self) -> int:
        """Получить количество пользователей"""
        result = await self.session.execute(
            select(func.count(User.id))
        )
        return result.scalar()


class MessageRepository:
    """Репозиторий для работы с сообщениями"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        msg_id: int,
        chat_id: int,
        name: str,
        message: str,
        person_id: int
    ) -> Message:
        """Создать сообщение"""
        msg = Message(
            id=msg_id,
            chat_id=chat_id,
            name=name,
            message=message,
            person_id=person_id
        )
        self.session.add(msg)
        await self.session.commit()
        await self.session.refresh(msg)
        return msg

    async def get_by_chat_id(self, chat_id: int) -> list[Message]:
        """Получить все сообщения для чата"""
        result = await self.session.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at)
        )
        return list(result.scalars().all())

    async def get_all(self) -> list[Message]:
        """Получить все сообщения"""
        result = await self.session.execute(select(Message))
        return list(result.scalars().all())

    async def count_by_chat_id(self, chat_id: int) -> int:
        """Получить количество сообщений в чате"""
        result = await self.session.execute(
            select(func.count(Message.id)).where(Message.chat_id == chat_id)
        )
        return result.scalar()

    async def count(self) -> int:
        """Получить общее количество сообщений"""
        result = await self.session.execute(
            select(func.count(Message.id))
        )
        return result.scalar()

    async def count_by_person(self, person_id: int, chat_ids: list[int] | None = None) -> int:
        """Получить количество сообщений пользователя (опционально в конкретных чатах)"""
        stmt = select(func.count(Message.id)).where(Message.person_id == person_id)
        if chat_ids:
            stmt = stmt.where(Message.chat_id.in_(chat_ids))
        result = await self.session.execute(stmt)
        return result.scalar()

    async def get_chat_ids_by_person(self, person_id: int) -> list[int]:
        """Получить ID чатов, в которых пользователь писал сообщения"""
        result = await self.session.execute(
            select(Message.chat_id).where(Message.person_id == person_id).distinct()
        )
        return [row[0] for row in result.all()]

    async def count_unique_users(self, chat_ids: list[int] | None = None) -> int:
        """Количество уникальных пользователей (опционально в конкретных чатах)"""
        stmt = select(func.count(func.distinct(Message.person_id)))
        if chat_ids:
            stmt = stmt.where(Message.chat_id.in_(chat_ids))
        result = await self.session.execute(stmt)
        return result.scalar()

    async def count_in_chats(self, chat_ids: list[int]) -> int:
        """Количество сообщений в указанных чатах"""
        result = await self.session.execute(
            select(func.count(Message.id)).where(Message.chat_id.in_(chat_ids))
        )
        return result.scalar()

    async def top_users(self, limit: int = 10, chat_ids: list[int] | None = None) -> list[tuple[int, str, int]]:
        """Топ пользователей по количеству сообщений (опционально в конкретных чатах)"""
        stmt = select(
            Message.person_id,
            Message.name,
            func.count(Message.id).label("cnt")
        )
        if chat_ids:
            stmt = stmt.where(Message.chat_id.in_(chat_ids))
        stmt = (
            stmt
            .group_by(Message.person_id, Message.name)
            .order_by(func.count(Message.id).desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return [(row[0], row[1], row[2]) for row in result.all()]

    async def get_paginated(self, chat_id: int, limit: int = 50, offset: int = 0) -> list[Message]:
        """Получить сообщения чата с пагинацией (новые первыми)"""
        result = await self.session.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())


class InlinePhotoRepository:
    """Репозиторий для работы с inline фото"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, photo_id: str, query_text: str) -> InlinePhoto:
        """Добавить фото"""
        photo = InlinePhoto(id=photo_id, query_text=query_text)
        self.session.add(photo)
        await self.session.commit()
        await self.session.refresh(photo)
        return photo

    async def get_by_query(self, query_text: str) -> list[InlinePhoto]:
        """Получить фото по запросу"""
        result = await self.session.execute(
            select(InlinePhoto).where(InlinePhoto.query_text == query_text)
        )
        return list(result.scalars().all())

    async def get_all_queries(self) -> set[str]:
        """Получить все уникальные запросы"""
        result = await self.session.execute(
            select(InlinePhoto.query_text).distinct()
        )
        return {row[0] for row in result.all()}

    async def delete(self, photo_id: str, query_text: str | None = None) -> bool:
        """Удалить фото"""
        stmt = delete(InlinePhoto).where(InlinePhoto.id == photo_id)
        if query_text:
            stmt = stmt.where(InlinePhoto.query_text == query_text)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0


class RectanglesImgRepository:
    """Репозиторий для работы с изображениями прямоугольников"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, image_id: str) -> int:
        """Добавить изображение"""
        img = RectanglesImg(image_id=image_id)
        self.session.add(img)
        await self.session.commit()
        await self.session.refresh(img)
        return img.id

    async def get_by_id(self, img_id: int) -> RectanglesImg | None:
        """Получить изображение по ID"""
        result = await self.session.execute(
            select(RectanglesImg).where(RectanglesImg.id == img_id)
        )
        return result.scalar_one_or_none()


class ChatRepository:
    """Репозиторий для работы с чатами бота"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, chat_id: int) -> Chat | None:
        """Получить чат по ID"""
        result = await self.session.execute(
            select(Chat).where(Chat.id == chat_id)
        )
        return result.scalar_one_or_none()

    async def upsert(self, chat_id: int, title: str, chat_type: str) -> Chat:
        """Добавить или обновить чат"""
        chat = await self.get(chat_id)
        if chat:
            chat.title = title or chat.title
            chat.chat_type = chat_type
            chat.is_active = True
        else:
            chat = Chat(id=chat_id, title=title, chat_type=chat_type, is_active=True)
            self.session.add(chat)
        await self.session.commit()
        await self.session.refresh(chat)
        return chat

    async def deactivate(self, chat_id: int) -> None:
        """Пометить чат как неактивный (бот удалён)"""
        chat = await self.get(chat_id)
        if chat:
            chat.is_active = False
            await self.session.commit()

    async def get_active(self) -> list[Chat]:
        """Получить все активные чаты"""
        result = await self.session.execute(
            select(Chat).where(Chat.is_active).order_by(Chat.title)
        )
        return list(result.scalars().all())

    async def count_active(self) -> int:
        """Получить количество активных чатов"""
        result = await self.session.execute(
            select(func.count(Chat.id)).where(Chat.is_active)
        )
        return result.scalar()
