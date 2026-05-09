from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.document_service import (
    delete_document,
    delete_source_documents,
    get_source_preview,
    list_documents,
    list_unique_sources,
)

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


@router.get("/sources")
async def api_list_unique_sources(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    content_type: str = Query(default=""),
    course_name: str = Query(default=""),
    search: str = Query(default=""),
    db: Session = Depends(get_db),
):
    results, total = list_unique_sources(
        db,
        page=page,
        page_size=page_size,
        content_type=content_type,
        course_name=course_name,
        search=search,
    )
    sources = []
    for r in results:
        preview = get_source_preview(db, r.source_file, r.course_name or "")
        sources.append({
            "source_file": r.source_file,
            "source_path": r.source_path,
            "content_type": r.content_type,
            "course_name": r.course_name,
            "project_name": r.project_name,
            "chapter_name": r.chapter_name or "",
            "fragment_count": r.fragment_count,
            "preview": preview[:200] if preview else "",
        })
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "documents": sources,
    }


@router.delete("/sources")
async def api_delete_source_documents(
    source_file: str = Query(...),
    course_name: str = Query(default=""),
    project_name: str = Query(default=""),
    db: Session = Depends(get_db),
):
    deleted_count = delete_source_documents(db, source_file, course_name, project_name)
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Source not found")
    return {"deleted": True, "fragments_removed": deleted_count}


@router.delete("/{document_id}")
async def api_delete_document(document_id: int, db: Session = Depends(get_db)):
    ok = delete_document(db, document_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"deleted": True}
