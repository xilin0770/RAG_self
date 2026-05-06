import json
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, Form, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.import_task import ImportTask
from app.services.importer import run_import

router = APIRouter(prefix="/import", tags=["内容导入"])


@router.post("")
async def import_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    content_type: str = Form(default="doc_fragment"),
    course_name: str = Form(default=""),
    project_name: str = Form(default=""),
    chapter_name: str = Form(default=""),
    source_path: str = Form(default=""),
    db: Session = Depends(get_db),
):
    """上传文档并异步导入到知识库。"""
    file_bytes = await file.read()

    metadata = {
        "content_type": content_type,
        "course_name": course_name,
        "project_name": project_name,
        "chapter_name": chapter_name,
        "source_path": source_path,
    }

    task = ImportTask(
        file_name=file.filename or "unknown",
        status="pending",
        metadata_json=json.dumps(metadata, ensure_ascii=False),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    background_tasks.add_task(run_import, task.id, file_bytes, file.filename, metadata)

    return {"task_id": task.id, "status": task.status, "file_name": task.file_name}


@router.get("/{task_id}/status")
async def get_import_status(task_id: int, db: Session = Depends(get_db)):
    """查询导入任务状态。"""
    task = db.query(ImportTask).get(task_id)
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
        "created_at": task.updated_at.isoformat() if task.updated_at else None,
    }
