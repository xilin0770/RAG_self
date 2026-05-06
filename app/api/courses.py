from typing import Optional

from fastapi import APIRouter, Query, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.course_service import (
    list_courses,
    get_course,
    create_course,
    add_chapter,
    add_project,
)

router = APIRouter(prefix="/courses", tags=["课程"])


class CourseCreate(BaseModel):
    name: str
    description: str = ""
    prerequisites: str = ""
    target_audience: str = ""
    learning_goals: str = ""


class ChapterCreate(BaseModel):
    name: str
    order: int = 0


class ProjectCreate(BaseModel):
    name: str
    description: str = ""


@router.get("")
async def api_list_courses(
    keyword: Optional[str] = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """查询课程列表，支持关键词搜索。"""
    courses = list_courses(db, keyword=keyword, offset=offset, limit=limit)
    return [
        {
            "id": c.id,
            "name": c.name,
            "description": c.description,
            "target_audience": c.target_audience,
        }
        for c in courses
    ]


@router.post("")
async def api_create_course(body: CourseCreate, db: Session = Depends(get_db)):
    """创建新课程。"""
    course = create_course(
        db,
        name=body.name,
        description=body.description,
        prerequisites=body.prerequisites,
        target_audience=body.target_audience,
        learning_goals=body.learning_goals,
    )
    return {"id": course.id, "name": course.name}


@router.get("/{course_id}")
async def api_get_course(course_id: int, db: Session = Depends(get_db)):
    """获取课程详情，包含章节结构和项目列表。"""
    course = get_course(db, course_id)
    if not course:
        return {"error": "Course not found"}
    return {
        "id": course.id,
        "name": course.name,
        "description": course.description,
        "prerequisites": course.prerequisites,
        "target_audience": course.target_audience,
        "learning_goals": course.learning_goals,
        "chapters": [
            {"id": ch.id, "name": ch.name, "order": ch.order}
            for ch in sorted(course.chapters, key=lambda x: x.order)
        ],
        "projects": [
            {"id": p.id, "name": p.name, "description": p.description}
            for p in course.projects
        ],
    }


@router.post("/{course_id}/chapters")
async def api_add_chapter(course_id: int, body: ChapterCreate, db: Session = Depends(get_db)):
    """为课程添加章节。"""
    chapter = add_chapter(db, course_id, name=body.name, order=body.order)
    return {"id": chapter.id, "name": chapter.name, "order": chapter.order}


@router.post("/{course_id}/projects")
async def api_add_project(course_id: int, body: ProjectCreate, db: Session = Depends(get_db)):
    """为课程添加项目。"""
    project = add_project(db, course_id, name=body.name, description=body.description)
    return {"id": project.id, "name": project.name}
