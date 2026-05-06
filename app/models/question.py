from sqlalchemy import Column, Integer, String, Text

from app.core.database import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False, index=True)  # single_choice, multi_choice, true_false, fill_blank, short_answer
    options = Column(Text, default="")  # JSON string
    answer = Column(Text, default="")
    explanation = Column(Text, default="")
    question_bank_name = Column(String(255), default="", index=True)
    question_code = Column(String(100), default="", index=True)
    course_name = Column(String(255), default="", index=True)
    source_file = Column(String(512), default="")
