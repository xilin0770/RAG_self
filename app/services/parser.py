import io
from pathlib import Path

from PyPDF2 import PdfReader
from docx import Document


def parse_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    texts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            texts.append(text)
    return "\n\n".join(texts)


def parse_docx(file_bytes: bytes) -> str:
    doc = Document(io.BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def parse_markdown(file_bytes: bytes) -> str:
    return file_bytes.decode("utf-8", errors="replace")


def parse_txt(file_bytes: bytes) -> str:
    return file_bytes.decode("utf-8", errors="replace")


PARSER_MAP = {
    ".pdf": parse_pdf,
    ".docx": parse_docx,
    ".doc": parse_docx,
    ".md": parse_markdown,
    ".txt": parse_txt,
    ".markdown": parse_markdown,
}


def parse_document(file_bytes: bytes, filename: str) -> str:
    """Parse document bytes into plain text based on file extension."""
    ext = Path(filename).suffix.lower()
    parser = PARSER_MAP.get(ext)
    if not parser:
        raise ValueError(f"Unsupported file type: {ext}")
    text = parser(file_bytes)
    if not text.strip():
        raise ValueError(f"No text extracted from {filename}")
    return text
