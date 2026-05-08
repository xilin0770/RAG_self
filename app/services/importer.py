from datetime import datetime, timezone

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.database import SessionLocal
from app.models.import_task import ImportTask
from app.models.document import DocumentFragment
from app.services.parser import parse_document
from app.services.embedding import embed_texts
from app.services.vector_store import add_chunks


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

        # 2. Chunk with user-specified parameters
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
