from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.document import DocumentFragment
from app.services.vector_store import delete_by_ids


def list_documents(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    content_type: str = "",
    course_name: str = "",
    search: str = "",
):
    q = db.query(DocumentFragment)
    if content_type:
        q = q.filter(DocumentFragment.content_type == content_type)
    if course_name:
        q = q.filter(DocumentFragment.course_name == course_name)
    if search:
        pattern = f"%{search}%"
        q = q.filter(
            DocumentFragment.content.ilike(pattern)
            | DocumentFragment.source_file.ilike(pattern)
        )
    total = q.count()
    results = q.order_by(DocumentFragment.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return results, total


def list_unique_sources(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    content_type: str = "",
    course_name: str = "",
    search: str = "",
):
    q = db.query(
        DocumentFragment.source_file,
        DocumentFragment.source_path,
        DocumentFragment.content_type,
        DocumentFragment.course_name,
        DocumentFragment.project_name,
        func.count(DocumentFragment.id).label("fragment_count"),
        func.min(DocumentFragment.id).label("representative_id"),
        func.max(DocumentFragment.chapter_name).label("chapter_name"),
    )
    if content_type:
        q = q.filter(DocumentFragment.content_type == content_type)
    if course_name:
        q = q.filter(DocumentFragment.course_name == course_name)
    if search:
        pattern = f"%{search}%"
        q = q.filter(DocumentFragment.source_file.ilike(pattern))

    q = q.group_by(
        DocumentFragment.source_file,
        DocumentFragment.source_path,
        DocumentFragment.content_type,
        DocumentFragment.course_name,
        DocumentFragment.project_name,
    )

    subq = q.subquery()
    total = db.query(func.count()).select_from(subq).scalar()

    results = (
        q.order_by(func.max(DocumentFragment.id).desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return results, total


def get_source_preview(db: Session, source_file: str, course_name: str = "") -> str:
    q = db.query(DocumentFragment.content).filter(
        DocumentFragment.source_file == source_file
    )
    if course_name:
        q = q.filter(DocumentFragment.course_name == course_name)
    row = q.order_by(DocumentFragment.id.asc()).first()
    return row.content if row else ""


def delete_source_documents(
    db: Session, source_file: str, course_name: str = "", project_name: str = ""
) -> int:
    q = db.query(DocumentFragment).filter(DocumentFragment.source_file == source_file)
    if course_name:
        q = q.filter(DocumentFragment.course_name == course_name)
    if project_name:
        q = q.filter(DocumentFragment.project_name == project_name)
    fragments = q.all()
    chunk_ids = [f.chunk_id for f in fragments if f.chunk_id]
    if chunk_ids:
        delete_by_ids(chunk_ids)
    for f in fragments:
        db.delete(f)
    db.commit()
    return len(fragments)


def delete_document(db: Session, document_id: int) -> bool:
    fragment = db.get(DocumentFragment, document_id)
    if not fragment:
        return False
    if fragment.chunk_id:
        delete_by_ids([fragment.chunk_id])
    db.delete(fragment)
    db.commit()
    return True
