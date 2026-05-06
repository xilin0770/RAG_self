from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings


def get_splitter() -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", "。", ".", " ", ""],
    )


def split_text(text: str) -> List[str]:
    """Split text into chunks, returns list of chunk strings."""
    splitter = get_splitter()
    chunks = splitter.split_text(text)
    return [c.strip() for c in chunks if c.strip()]
