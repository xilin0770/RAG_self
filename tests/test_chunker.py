from app.services.chunker import split_text


def test_split_short_text():
    chunks = split_text("Hello world")
    assert len(chunks) >= 1
    assert "Hello world" in chunks[0]


def test_split_long_text():
    text = "This is a test sentence. " * 100
    chunks = split_text(text)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) > 0


def test_split_empty_text():
    chunks = split_text("")
    assert len(chunks) == 0
