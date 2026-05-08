from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.document_service import list_documents, delete_document

router = APIRouter(prefix="/documents", tags=["文档管理"])


@router.get("")
async def api_list_documents(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    content_type: str = Query(default=""),
    course_name: str = Query(default=""),
    search: str = Query(default=""),
    db: Session = Depends(get_db),
):
    results, total = list_documents(
        db,
        page=page,
        page_size=page_size,
        content_type=content_type,
        course_name=course_name,
        search=search,
    )
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "documents": [
            {
                "id": f.id,
                "content": f.content[:300],
                "content_type": f.content_type,
                "course_name": f.course_name,
                "project_name": f.project_name,
                "chapter_name": f.chapter_name,
                "source_file": f.source_file,
                "source_path": f.source_path,
                "chunk_id": f.chunk_id,
            }
            for f in results
        ],
    }


@router.delete("/{document_id}")
async def api_delete_document(document_id: int, db: Session = Depends(get_db)):
    ok = delete_document(db, document_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"deleted": True}
