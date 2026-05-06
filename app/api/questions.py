import json
from typing import Optional

from fastapi import APIRouter, Query, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.question_service import (
    list_questions,
    get_question,
    create_question,
)

router = APIRouter(prefix="/questions", tags=["题库"])


class QuestionCreate(BaseModel):
    content: str
    question_type: str  # single_choice, multi_choice, true_false, fill_blank, short_answer
    options: list[str] = []
    answer: str = ""
    explanation: str = ""
    question_bank_name: str = ""
    question_code: str = ""
    course_name: str = ""
    source_file: str = ""


@router.get("")
async def api_list_questions(
    keyword: Optional[str] = Query(None),
    course_name: Optional[str] = Query(None),
    question_type: Optional[str] = Query(None),
    question_bank_name: Optional[str] = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """查询题目列表，支持按课程、题型、题库、关键词检索。"""
    questions = list_questions(
        db,
        keyword=keyword,
        course_name=course_name,
        question_type=question_type,
        question_bank_name=question_bank_name,
        offset=offset,
        limit=limit,
    )
    return [
        {
            "id": q.id,
            "content": q.content,
            "question_type": q.question_type,
            "question_bank_name": q.question_bank_name,
            "question_code": q.question_code,
            "course_name": q.course_name,
        }
        for q in questions
    ]


@router.post("")
async def api_create_question(body: QuestionCreate, db: Session = Depends(get_db)):
    """创建新题目。"""
    q = create_question(
        db,
        content=body.content,
        question_type=body.question_type,
        answer=body.answer,
        explanation=body.explanation,
        question_bank_name=body.question_bank_name,
        question_code=body.question_code,
        course_name=body.course_name,
        source_file=body.source_file,
        options=body.options,
    )
    return {"id": q.id, "content": q.content, "question_type": q.question_type}


@router.get("/{question_id}")
async def api_get_question(question_id: int, db: Session = Depends(get_db)):
    """获取题目详情，包含题型、选项、答案与解析。"""
    q = get_question(db, question_id)
    if not q:
        return {"error": "Question not found"}
    return {
        "id": q.id,
        "content": q.content,
        "question_type": q.question_type,
        "options": json.loads(q.options) if q.options else [],
        "answer": q.answer,
        "explanation": q.explanation,
        "question_bank_name": q.question_bank_name,
        "question_code": q.question_code,
        "course_name": q.course_name,
        "source_file": q.source_file,
    }
