from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(10), nullable=False, default="user")  # "admin" or "user"
    settings_json = Column(Text, nullable=True, default='{"font_size": "normal"}')
    created_at = Column(DateTime, server_default=func.now())
