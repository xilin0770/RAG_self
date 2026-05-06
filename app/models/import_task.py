from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, Float, DateTime

from app.core.database import Base


class ImportTask(Base):
    __tablename__ = "import_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_name = Column(String(512), nullable=False)
    status = Column(String(50), nullable=False, default="pending", index=True)  # pending, processing, completed, failed
    progress = Column(Float, default=0.0)
    total_chunks = Column(Integer, default=0)
    completed_chunks = Column(Integer, default=0)
    error_message = Column(Text, default="")
    metadata_json = Column(Text, default="{}")  # course_name, project_name, chapter_name, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
