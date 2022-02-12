import logging
from datetime import datetime
from typing import List

from aiogram import Dispatcher
from gino import Gino
import sqlalchemy as sa
from sqlalchemy import Integer, Column, String, DateTime

from data.config import POSTGRES_URI

db = Gino()


class BaseModel(db.Model):
    __abstract__ = True

    def __str__(self):
        model = self.__class__.__name__
        table: sa.Table = sa.inspect(self.__class__)
        columns: List[sa.Column] = table.columns
        values = {
            column.name: getattr(self, self._column_name_map[column.name])
            for column in columns
        }
        values_str = " ".join(f"{name}={value!r}" for name, value in values.items())
        return f"<{model} {values_str}>"

    # def __repr__(self):
    #     return self.__str__()


class TimeBaseModel(BaseModel):
    __abstract__ = True

    created_at = Column(DateTime(True), server_default=db.func.now())
    updated_at = Column(DateTime(True),
                        default=db.func.now(),
                        onupdate=db.func.now(),
                        server_default=db.func.now())


async def on_startup(dispatcher: Dispatcher):
    logging.info("Установка связи с PostgreSQL")
    await db.set_bind(POSTGRES_URI)
