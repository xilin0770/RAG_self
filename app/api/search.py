from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.search_service import search_documents

router = APIRouter(prefix="/search", tags=["检索"])


class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = None
    course_name: Optional[str] = None
    content_type: Optional[str] = None


@router.post("/documents")
async def api_search_documents(body: SearchRequest, db: Session = Depends(get_db)):
    """文档语义检索，返回相关片段及来源信息。"""
    results = search_documents(
        query=body.query,
        db=db,
        top_k=body.top_k,
        course_name=body.course_name,
        content_type=body.content_type,
    )
    return {"query": body.query, "total": len(results), "results": results}
