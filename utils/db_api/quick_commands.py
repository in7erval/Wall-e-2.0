import logging

from asyncpg import UniqueViolationError

from utils.db_api.db_gino import db
from utils.db_api.schemas.inline_photos import InlinePhoto
from utils.db_api.schemas.message import Message
from utils.db_api.schemas.rectangles_img import RectanglesImg
from utils.db_api.schemas.user import User


# ---------------------- User -----------------------------------


async def add_user(id: int, name: str, is_admin: bool = False):
    user = User(id=id, name=name, is_admin=is_admin)
    await user.create()


async def select_all_users():
    users = await User.query.gino.all()
    return users


async def select_user(id: int):
    user = await User.query.where(User.id == id).gino.first()
    return user


async def count_users():
    total = await db.func.count(User.id).gino.scalar()
    return total


async def update_user_admin(id, is_admin):
    user: User = await User.get(id)
    await user.update(is_admin=is_admin).apply()


async def select_all_admins() -> list:
    users = await User.query.where(User.is_admin == True).gino.all()
    return users


# ---------------- Message ---------------------------------------------------


async def add_message(id: int, chat_id: int, name: str, message: str, person_id: int):
    try:
        message = Message(id=id, chat_id=chat_id, name=name, message=message, person_id=person_id)
        await message.create()
    except UniqueViolationError:
        pass


async def select_all_messages():
    messages = await Message.query.gino.all()
    return messages


async def select_messages_by_chat_id(id):
    messages = await Message.query.where(Message.chat_id == id).gino.all()
    return messages


# ------------ InlinePhotos ------------------------------------------------

async def add_inline_photo(id: int, query: str):
    try:
        photo = InlinePhoto(id=id, query_text=query)
        await photo.create()
    except UniqueViolationError:
        pass


async def del_inline_photo(id: str, query: str = None):
    try:
        if query is None:
            logging.info(await InlinePhoto.delete.where(InlinePhoto.id == id).gino.status())
        else:
            logging.info(await InlinePhoto.delete.where(InlinePhoto.id == id)
                         .where(InlinePhoto.query_text == query).gino.status())
        return True
    except Exception as err:
        logging.error(err)
        return False


# async def select_all_photos() -> list:
#     photos = await InlinePhoto.query.gino.all()
#     return photos


async def select_all_queries() -> set:
    photos = await InlinePhoto.query.gino.all()
    all_queries = set([photo.query_text for photo in photos])
    return all_queries


async def select_photos_by_query(query_text: str) -> list:
    photos = await InlinePhoto.query.where(InlinePhoto.query_text == query_text).gino.all()
    return photos


# ------------- RectanglesImg ------------

async def select_rectangle_img_by_id(id):
    rectangle_img = await RectanglesImg.query.where(RectanglesImg.id == id).gino.first()
    return rectangle_img


async def add_rectangle_img(image_id) -> int:
    try:
        rectangle_img = RectanglesImg(image_id=image_id)
        await rectangle_img.create()
        return rectangle_img.id
    except UniqueViolationError:
        pass
