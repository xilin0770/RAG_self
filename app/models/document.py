from sqlalchemy import Column, Integer, String, Text, ForeignKey

from app.core.database import Base


class DocumentFragment(Base):
    __tablename__ = "document_fragments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text, nullable=False)
    content_type = Column(String(50), nullable=False, index=True)  # course_intro, doc_fragment, project_material, question
    course_name = Column(String(255), default="")
    project_name = Column(String(255), default="")
    chapter_name = Column(String(255), default="")
    source_file = Column(String(512), default="")
    source_path = Column(String(1024), default="")
    chunk_id = Column(String(255), index=True)  # corresponding chunk id in vector store
