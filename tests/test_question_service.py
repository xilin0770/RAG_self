import pytest
from unittest.mock import patch, MagicMock
from app.services.qa_service import ask_sync


class TestQASync:
    @patch("app.services.qa_service.get_llm")
    @patch("app.services.qa_service.vector_search")
    @patch("app.services.qa_service.embed_query")
    def test_ask_with_context_returns_answer(self, mock_embed, mock_vs, mock_llm):
        mock_embed.return_value = [0.1] * 1024
        mock_vs.return_value = {
            "ids": [["chunk-1"]],
            "documents": [["Python is a programming language."]],
            "metadatas": [[{"course_name": "Python", "chapter_name": "Intro",
                            "source_file": "test.md"}]],
        }
        mock_llm_instance = MagicMock()
        mock_llm_instance.invoke.return_value = MagicMock(content="Python是一种编程语言")
        mock_llm.return_value = mock_llm_instance

        mock_db = MagicMock()
        result = ask_sync("What is Python?", mock_db)
        assert "Python" in result["answer"]
        assert len(result["citations"]) == 1

    @patch("app.services.qa_service.vector_search")
    @patch("app.services.qa_service.embed_query")
    def test_ask_without_context_returns_dont_know(self, mock_embed, mock_vs):
        mock_embed.return_value = [0.1] * 1024
        mock_vs.return_value = {"ids": [[]], "documents": [[]], "metadatas": [[]]}

        mock_db = MagicMock()
        result = ask_sync("What is XYZ?", mock_db)
        assert result["answer"] == "不知道"
        assert result["citations"] == []

    @patch("app.services.qa_service.get_llm")
    @patch("app.services.qa_service.vector_search")
    @patch("app.services.qa_service.embed_query")
    def test_ask_with_irrelevant_context_still_calls_llm(self, mock_embed, mock_vs, mock_llm):
        mock_embed.return_value = [0.1] * 1024
        mock_vs.return_value = {
            "ids": [["chunk-1"]],
            "documents": [["Some unrelated content about cooking."]],
            "metadatas": [[{"course_name": "", "chapter_name": "", "source_file": ""}]],
        }
        mock_llm_instance = MagicMock()
        mock_llm_instance.invoke.return_value = MagicMock(content="不知道")
        mock_llm.return_value = mock_llm_instance

        mock_db = MagicMock()
        result = ask_sync("What is machine learning?", mock_db)
        assert result["answer"] == "不知道"
