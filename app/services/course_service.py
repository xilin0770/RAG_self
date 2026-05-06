from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.models.course import Course, Project, Chapter


def create_course(db: Session, name: str, description: str = "",
                  prerequisites: str = "", target_audience: str = "",
                  learning_goals: str = "") -> Course:
    course = Course(
        name=name,
        description=description,
        prerequisites=prerequisites,
        target_audience=target_audience,
        learning_goals=learning_goals,
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def list_courses(db: Session, keyword: Optional[str] = None,
                 offset: int = 0, limit: int = 20) -> list[Course]:
    q = db.query(Course)
    if keyword:
        q = q.filter(
            Course.name.ilike(f"%{keyword}%") |
            Course.description.ilike(f"%{keyword}%")
        )
    return q.offset(offset).limit(limit).all()


def get_course(db: Session, course_id: int) -> Optional[Course]:
    return (
        db.query(Course)
        .options(joinedload(Course.projects), joinedload(Course.chapters))
        .filter(Course.id == course_id)
        .first()
    )


def add_chapter(db: Session, course_id: int, name: str, order: int = 0) -> Chapter:
    chapter = Chapter(name=name, order=order, course_id=course_id)
    db.add(chapter)
    db.commit()
    db.refresh(chapter)
    return chapter


def add_project(db: Session, course_id: int, name: str, description: str = "") -> Project:
    project = Project(name=name, description=description, course_id=course_id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project
