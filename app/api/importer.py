import json
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, UploadFile, File, Form, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.import_task import ImportTask
from app.services.importer import run_import

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
        return {"error": "Task not found"}
    return {
        "task_id": task.id,
        "file_name": task.file_name,
        "status": task.status,
        "progress": task.progress,
        "total_chunks": task.total_chunks,
        "completed_chunks": task.completed_chunks,
        "error_message": task.error_message,
        "created_at": task.created_at.isoformat() if task.created_at else "",
        "updated_at": task.updated_at.isoformat() if task.updated_at else "",
    }
