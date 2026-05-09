from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, Float, DateTime

from app.core.database import Base


class ImportTask(Base):
    __tablename__ = "import_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_name = Column(String(512), nullable=False)
    content_type = Column(String(50), default="", index=True)
    status = Column(String(50), nullable=False, default="pending", index=True)  # pending, processing, completed, failed
    progress = Column(Float, default=0.0)
    total_chunks = Column(Integer, default=0)
    completed_chunks = Column(Integer, default=0)
    questions_extracted = Column(Integer, default=0)
    courses_extracted = Column(Integer, default=0)
    error_message = Column(Text, default="")
    metadata_json = Column(Text, default="{}")  # course_name, project_name, chapter_name, etc.
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
