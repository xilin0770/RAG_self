import threading
from datetime import datetime, timezone

from langchain_text_splitters import RecursiveCharacterTextSplitter

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.import_task import ImportTask
from app.models.document import DocumentFragment
from app.services.parser import parse_document
from app.services.embedding import embed_texts
from app.services.vector_store import add_chunks
from app.services.extractor import extract_structured_content
from app.services.question_service import create_question
from app.services.course_service import create_course


def run_extraction(
    task_id: int,
    text: str,
    filename: str,
    metadata: dict,
):
    """Run LLM structured extraction and persist results to DB."""
    db = SessionLocal()
    try:
        result = extract_structured_content(text, filename)

        questions_count = 0
        courses_count = 0
        course_name = metadata.get("course_name", "")

        for q in result.get("questions", []):
            try:
                create_question(
                    db=db,
                    content=q.get("content", ""),
                    question_type=q.get("question_type", "short_answer"),
                    options=q.get("options", []),
                    answer=q.get("answer", ""),
                    explanation=q.get("explanation", ""),
                    course_name=course_name,
                    source_file=filename,
                )
                questions_count += 1
            except Exception:
                pass

        for c in result.get("courses", []):
            try:
                create_course(
                    db=db,
                    name=c.get("name", ""),
                    description=c.get("description", ""),
                    prerequisites=c.get("prerequisites", ""),
                    target_audience=c.get("target_audience", ""),
                    learning_goals=c.get("learning_goals", ""),
                )
                courses_count += 1
            except Exception:
                pass

        task = db.get(ImportTask, task_id)
        if task:
            task.questions_extracted = questions_count
            task.courses_extracted = courses_count
            task.updated_at = datetime.now(timezone.utc)
            db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


def run_import(
    task_id: int,
    file_bytes: bytes,
    filename: str,
    metadata: dict,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
):
    """Run the full import pipeline and update task status."""
    db = SessionLocal()
    try:
        task = db.get(ImportTask, task_id)
        if not task:
            return

        task.status = "processing"
        task.updated_at = datetime.now(timezone.utc)
        db.commit()

        # 1. Parse
        text = parse_document(file_bytes, filename)

        # 2. Start extraction in parallel for question/course types
        content_type = metadata.get("content_type", "")
        if content_type in ("question", "course_intro"):
            t = threading.Thread(
                target=run_extraction,
                args=(task_id, text, filename, metadata),
                daemon=True,
            )
            t.start()

        # 3. Chunk with user-specified parameters
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "。", ".", " ", ""],
        )
        chunks = splitter.split_text(text)
        chunks = [c.strip() for c in chunks if c.strip()]
        if not chunks:
            raise ValueError("No text chunks produced")

        task.total_chunks = len(chunks)
        db.commit()

        # 3. Embed
        embeddings = embed_texts(chunks)

        # 4. Store in vector DB
        chunk_metadatas = [
            {
                "content_type": metadata.get("content_type", ""),
                "course_name": metadata.get("course_name", ""),
                "project_name": metadata.get("project_name", ""),
                "chapter_name": metadata.get("chapter_name", ""),
                "source_file": filename,
                "source_path": metadata.get("source_path", ""),
            }
            for _ in chunks
        ]
        chunk_ids = add_chunks(chunks, embeddings, chunk_metadatas)

        # 5. Write metadata to SQL
        for i, chunk in enumerate(chunks):
            fragment = DocumentFragment(
                content=chunk,
                content_type=metadata.get("content_type", ""),
                course_name=metadata.get("course_name", ""),
                project_name=metadata.get("project_name", ""),
                chapter_name=metadata.get("chapter_name", ""),
                source_file=filename,
                source_path=metadata.get("source_path", ""),
                chunk_id=chunk_ids[i],
            )
            db.add(fragment)

        # 6. Complete
        task.status = "completed"
        task.completed_chunks = len(chunks)
        task.progress = 100.0
        task.updated_at = datetime.now(timezone.utc)
        db.commit()

    except Exception as e:
        db.rollback()
        task = db.get(ImportTask, task_id)
        if task:
            task.status = "failed"
            task.error_message = str(e)
            task.updated_at = datetime.now(timezone.utc)
            db.commit()
    finally:
        db.close()


def list_import_tasks(
    db: Session,
    status: str = "",
    content_type: str = "",
    page: int = 1,
    page_size: int = 20,
):
    q = db.query(ImportTask)
    if status:
        q = q.filter(ImportTask.status == status)
    if content_type:
        q = q.filter(ImportTask.content_type == content_type)
    total = q.count()
    tasks = q.order_by(ImportTask.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return tasks, total
