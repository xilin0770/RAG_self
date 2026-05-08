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


def delete_document(db: Session, document_id: int) -> bool:
    fragment = db.get(DocumentFragment, document_id)
    if not fragment:
        return False
    if fragment.chunk_id:
        delete_by_ids([fragment.chunk_id])
    db.delete(fragment)
    db.commit()
    return True
