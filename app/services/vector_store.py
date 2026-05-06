from __future__ import annotations

import uuid
from typing import List, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.core.config import settings

_client: chromadb.PersistentClient | None = None
_collection: chromadb.Collection | None = None


def _get_client() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(
            path=settings.chroma_path,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
    return _client


def _get_collection() -> chromadb.Collection:
    global _collection
    if _collection is None:
        client = _get_client()
        _collection = client.get_or_create_collection(
            name="education_kb",
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def add_chunks(
    chunks: List[str],
    embeddings: List[List[float]],
    metadatas: List[dict],
) -> List[str]:
    """Add document chunks to the vector store. Returns list of chunk IDs."""
    collection = _get_collection()
    chunk_ids = [str(uuid.uuid4()) for _ in chunks]
    collection.add(
        ids=chunk_ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
    )
    return chunk_ids


def search(
    query_embedding: List[float],
    top_k: Optional[int] = None,
    filter_meta: Optional[dict] = None,
) -> dict:
    """Search for similar chunks. Returns ChromaDB results dict."""
    collection = _get_collection()
    top_k = top_k or settings.top_k
    kwargs = {
        "query_embeddings": [query_embedding],
        "n_results": top_k,
    }
    if filter_meta:
        kwargs["where"] = filter_meta
    return collection.query(**kwargs)


def delete_by_ids(chunk_ids: List[str]):
    """Delete chunks by their IDs."""
    collection = _get_collection()
    collection.delete(ids=chunk_ids)


def count() -> int:
    """Return total number of chunks in the store."""
    return _get_collection().count()
