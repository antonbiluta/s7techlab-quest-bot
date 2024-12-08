from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from data.base import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=True)
    team_id = Column(Integer, ForeignKey('team_chats.id'), nullable=True)

    team = relationship('TeamChat', back_populates='users')
