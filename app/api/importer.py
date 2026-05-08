import json
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Query, UploadFile, File, Form, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.import_task import ImportTask
from app.services.importer import run_import, list_import_tasks

router = APIRouter(prefix="/import", tags=["内容导入"])


@router.post("")
async def import_documents(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    content_type: str = Form(default="doc_fragment"),
    course_name: str = Form(default=""),
    project_name: str = Form(default=""),
    chapter_name: str = Form(default=""),
    source_path: str = Form(default=""),
    chunk_size: int = Form(default=500),
    chunk_overlap: int = Form(default=50),
    db: Session = Depends(get_db),
):
    """上传一个或多个文档并异步导入到知识库。"""
    metadata = {
        "content_type": content_type,
        "course_name": course_name,
        "project_name": project_name,
        "chapter_name": chapter_name,
        "source_path": source_path,
    }
    results = []

    for file in files:
        file_bytes = await file.read()

        task = ImportTask(
            file_name=file.filename or "unknown",
            content_type=metadata.get("content_type", ""),
            status="pending",
            metadata_json=json.dumps(metadata, ensure_ascii=False),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(task)
        db.commit()
        db.refresh(task)

        background_tasks.add_task(
            run_import, task.id, file_bytes, file.filename, metadata,
            chunk_size, chunk_overlap,
        )
        results.append({"task_id": task.id, "status": task.status, "file_name": task.file_name})

    return results


@router.get("/{task_id}/status")
async def get_import_status(task_id: int, db: Session = Depends(get_db)):
    """查询导入任务状态。"""
    task = db.get(ImportTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "task_id": task.id,
        "file_name": task.file_name,
        "content_type": task.content_type,
        "status": task.status,
        "progress": task.progress,
        "total_chunks": task.total_chunks,
        "completed_chunks": task.completed_chunks,
        "error_message": task.error_message,
        "created_at": task.created_at.isoformat() if task.created_at else "",
        "updated_at": task.updated_at.isoformat() if task.updated_at else "",
    }


@router.get("")
async def api_list_import_tasks(
    status: str = Query(default=""),
    content_type: str = Query(default=""),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    tasks, total = list_import_tasks(db, status=status, content_type=content_type, page=page, page_size=page_size)
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "tasks": [
            {
                "task_id": t.id,
                "file_name": t.file_name,
                "content_type": t.content_type,
                "status": t.status,
                "progress": t.progress,
                "total_chunks": t.total_chunks,
                "completed_chunks": t.completed_chunks,
                "error_message": t.error_message,
                "created_at": t.created_at.isoformat() if t.created_at else "",
                "updated_at": t.updated_at.isoformat() if t.updated_at else "",
            }
            for t in tasks
        ],
    }
