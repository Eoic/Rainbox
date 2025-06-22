from sqlalchemy import Column, Integer, String, Text
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(Text, nullable=False)
    api_key = Column(String(100), unique=True, nullable=True)

    @property
    def user_id(self) -> str:
        return str(self.id)
