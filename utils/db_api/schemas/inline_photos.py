from sqlalchemy import Column, sql, VARCHAR

from utils.db_api.db_gino import TimeBaseModel


class InlinePhoto(TimeBaseModel):
    __tablename__ = 'inline_photos'

    id = Column(VARCHAR(255), primary_key=True)
    query_text = Column(VARCHAR(255), nullable=False)

    query: sql.Select
