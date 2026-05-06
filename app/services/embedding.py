from __future__ import annotations

from typing import List

from sentence_transformers import SentenceTransformer

from app.core.config import settings

_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        model_path = settings.bge_m3_path or settings.bge_m3
        _model = SentenceTransformer(
            model_path,
            device=settings.bge_device,
        )
    return _model


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for a list of texts."""
    model = _get_model()
    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return embeddings.tolist()


def embed_query(text: str) -> List[float]:
    """Generate embedding for a single query text."""
    model = _get_model()
    embedding = model.encode(
        text,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return embedding.tolist()
