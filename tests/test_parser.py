import pytest

from app.services.parser import parse_document, parse_markdown, parse_txt


def test_parse_txt():
    text = parse_txt(b"Hello world\nThis is a test.")
    assert "Hello world" in text
    assert "This is a test" in text


def test_parse_markdown():
    text = parse_markdown("# Title\n\nContent here.".encode("utf-8"))
    assert "Title" in text
    assert "Content here" in text


def test_parse_unsupported_extension():
    with pytest.raises(ValueError, match="Unsupported file type"):
        parse_document(b"dummy", "test.xyz")


def test_parse_empty_document():
    with pytest.raises(ValueError, match="No text extracted"):
        parse_document(b"   ", "empty.txt")
