import pytest
from unittest.mock import MagicMock, patch
from app.services.search_service import search_documents


class TestSearchDocuments:
    @patch("app.services.search_service.vector_search")
    @patch("app.services.search_service.embed_query")
    def test_search_returns_results(self, mock_embed, mock_vs):
        mock_embed.return_value = [0.1] * 1024
        mock_vs.return_value = {
            "ids": [["chunk-1", "chunk-2"]],
            "documents": [["doc A", "doc B"]],
            "metadatas": [[
                {"course_name": "Python", "content_type": "doc_fragment",
                 "project_name": "", "chapter_name": "", "source_file": "test.md", "source_path": ""},
                {"course_name": "Python", "content_type": "doc_fragment",
                 "project_name": "", "chapter_name": "", "source_file": "test2.md", "source_path": ""},
            ]],
            "distances": [[0.2, 0.4]],
        }
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = []

        results = search_documents("test query", mock_db)
        assert len(results) >= 1

    @patch("app.services.search_service.vector_search")
    @patch("app.services.search_service.embed_query")
    def test_search_filters_by_threshold(self, mock_embed, mock_vs):
        mock_embed.return_value = [0.1] * 1024
        mock_vs.return_value = {
            "ids": [["chunk-1"]],
            "documents": [["far away doc"]],
            "metadatas": [[{"course_name": "", "content_type": "", "project_name": "",
                            "chapter_name": "", "source_file": "", "source_path": ""}]],
            "distances": [[0.95]],
        }
        mock_db = MagicMock()

        results = search_documents("test query", mock_db)
        # similarity = 1 - 0.95 = 0.05, below threshold of 0.3
        assert results == []

    @patch("app.services.search_service.vector_search")
    @patch("app.services.search_service.embed_query")
    def test_search_empty_results(self, mock_embed, mock_vs):
        mock_embed.return_value = [0.1] * 1024
        mock_vs.return_value = {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}
        mock_db = MagicMock()

        results = search_documents("test query", mock_db)
        assert results == []

    @patch("app.services.search_service.vector_search")
    @patch("app.services.search_service.embed_query")
    def test_search_with_content_type_filter(self, mock_embed, mock_vs):
        mock_embed.return_value = [0.1] * 1024
        mock_vs.return_value = {
            "ids": [["chunk-1"]],
            "documents": [["doc A"]],
            "metadatas": [[{"course_name": "", "content_type": "course_intro",
                            "project_name": "", "chapter_name": "", "source_file": "", "source_path": ""}]],
            "distances": [[0.2]],
        }
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = []

        results = search_documents("test", mock_db, content_type="course_intro")
        assert len(results) == 1
