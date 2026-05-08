import json
from typing import Optional

from sqlalchemy.orm import Session

from app.models.question import Question


def create_question(
    db: Session,
    content: str,
    question_type: str,
    answer: str = "",
    explanation: str = "",
    question_bank_name: str = "",
    question_code: str = "",
    course_name: str = "",
    source_file: str = "",
    options: list[str] | None = None,
) -> Question:
    q = Question(
        content=content,
        question_type=question_type,
        options=json.dumps(options or [], ensure_ascii=False),
        answer=answer,
        explanation=explanation,
        question_bank_name=question_bank_name,
        question_code=question_code,
        course_name=course_name,
        source_file=source_file,
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    return q


def list_questions(
    db: Session,
    keyword: Optional[str] = None,
    course_name: Optional[str] = None,
    question_type: Optional[str] = None,
    question_bank_name: Optional[str] = None,
    offset: int = 0,
    limit: int = 20,
) -> list[Question]:
    q = db.query(Question)
    if keyword:
        q = q.filter(Question.content.ilike(f"%{keyword}%"))
    if course_name:
        q = q.filter(Question.course_name == course_name)
    if question_type:
        q = q.filter(Question.question_type == question_type)
    if question_bank_name:
        q = q.filter(Question.question_bank_name == question_bank_name)
    return q.offset(offset).limit(limit).all()


def get_question(db: Session, question_id: int) -> Optional[Question]:
    return db.get(Question, question_id)
