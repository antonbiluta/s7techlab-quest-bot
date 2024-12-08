from sqlalchemy import Column, Integer, String, BigInteger
from sqlalchemy.orm import relationship
from data.base import Base


class TeamChat(Base):
    __tablename__ = 'team_chats'

    id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(BigInteger, unique=True, nullable=False)
    name = Column(String, nullable=False)
    invite_link = Column(String)
    current_number = Column(Integer, default=0)
    member_limit = Column(Integer, default=0)

    users = relationship("User", back_populates="team")

    def is_complete(self) -> bool:
        """
        Проверяет, укомплектована ли команда
        """
        return self.current_number == self.member_limit

    def count_str(self) -> str:
        return f"{self.current_number}/{self.member_limit}"

    def validate_increment(self, increment: int = 1, reverse: bool = False) -> bool:
        if not reverse and (self.is_complete() or self.current_number + increment > self.member_limit):
            return False
        if reverse and self.current_number - increment < 0:
            return False
        return True
