from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    template_name = Column(String(100), nullable=False)  # plain string, not FK
    original_filename = Column(String(255), nullable=False)
    output_excel_path = Column(String(255), nullable=False)
    rows_extracted = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, server_default=func.now())
