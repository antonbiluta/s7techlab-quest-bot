from sqlalchemy import Column, Integer, String, Boolean, JSON
from data.base import Base


class Settings(Base):
    __tablename__ = 'settings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)
    is_work = Column(Boolean, default=False)
    params = Column(JSON, nullable=True)
