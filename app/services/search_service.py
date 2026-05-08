from typing import List, Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.document import DocumentFragment
from app.services.embedding import embed_query
from app.services.vector_store import search as vector_search


def search_documents(
    query: str,
    db: Session,
    top_k: Optional[int] = None,
    course_name: Optional[str] = None,
    content_type: Optional[str] = None,
) -> List[dict]:
    """Semantic search for document fragments. Returns results with source info."""
    query_embedding = embed_query(query)

    conditions = []
    if course_name:
        conditions.append({"course_name": {"$eq": course_name}})
    if content_type:
        conditions.append({"content_type": {"$eq": content_type}})

    filter_meta = {"$and": conditions} if conditions else None
    results = vector_search(query_embedding, top_k=top_k, filter_meta=filter_meta)

    output = []
    if not results.get("ids") or not results["ids"][0]:
        return output

    for i, chunk_id in enumerate(results["ids"][0]):
        metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
        distance = results["distances"][0][i] if results.get("distances") else 0
        document = results["documents"][0][i] if results.get("documents") else ""
        score = 1 - distance  # cosine distance to similarity

        if score < settings.retrieval_threshold:
            continue

        output.append({
            "chunk_id": chunk_id,
            "content": document,
            "score": round(score, 4),
            "course_name": metadata.get("course_name", ""),
            "project_name": metadata.get("project_name", ""),
            "chapter_name": metadata.get("chapter_name", ""),
            "content_type": metadata.get("content_type", ""),
            "source_file": metadata.get("source_file", ""),
            "source_path": metadata.get("source_path", ""),
        })

    # Try to supplement with SQL metadata
    chunk_ids = [r["chunk_id"] for r in output]
    fragments = (
        db.query(DocumentFragment)
        .filter(DocumentFragment.chunk_id.in_(chunk_ids))
        .all()
    )
    frag_map = {f.chunk_id: f for f in fragments}
    for r in output:
        f = frag_map.get(r["chunk_id"])
        if f:
            r["course_name"] = r["course_name"] or f.course_name
            r["project_name"] = r["project_name"] or f.project_name
            r["chapter_name"] = r["chapter_name"] or f.chapter_name
            r["source_file"] = r["source_file"] or f.source_file

    return output
