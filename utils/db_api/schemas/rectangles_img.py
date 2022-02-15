from sqlalchemy import Column, String, BigInteger, sql

from utils.db_api.db_gino import TimeBaseModel


class RectanglesImg(TimeBaseModel):
    __tablename__ = 'rectangles_img'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    image_id = Column(String, primary_key=True)

    query: sql.Select
