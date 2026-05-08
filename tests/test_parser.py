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


def test_parse_md_extension():
    text = parse_document("# Hello\n\nWorld".encode("utf-8"), "notes.md")
    assert "Hello" in text
    assert "World" in text


def test_parse_markdown_extension():
    text = parse_document("# Hello".encode("utf-8"), "notes.markdown")
    assert "Hello" in text


class TestParseEdgeCases:
    def test_empty_txt_file(self):
        with pytest.raises(ValueError, match="No text extracted"):
            parse_document(b"", "empty.txt")

    def test_empty_md_file(self):
        with pytest.raises(ValueError, match="No text extracted"):
            parse_document(b"", "empty.md")

    def test_binary_garbage_rejected(self):
        # Binary data passed to PDF parser should not crash
        text = parse_document(b"\x00\x01\x02\x03", "binary.pdf")
        assert isinstance(text, str)
