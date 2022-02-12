from sqlalchemy import Column, BigInteger, String, sql, Boolean

from utils.db_api.db_gino import TimeBaseModel


class User(TimeBaseModel):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True)
    name = Column(String(100))
    is_admin = Column(Boolean, nullable=True)

    query: sql.Select
