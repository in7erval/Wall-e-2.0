from sqlalchemy import Column, String, BigInteger, sql

from utils.db_api.db_gino import TimeBaseModel


class Message(TimeBaseModel):
    __tablename__ = 'messages'

    id = Column(BigInteger, primary_key=True)
    chat_id = Column(BigInteger, primary_key=True)
    name = Column(String(100))
    message = Column(String(5000))
    person_id = Column(BigInteger)

    query: sql.Select
