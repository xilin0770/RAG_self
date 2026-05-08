import pytest
from unittest.mock import MagicMock, patch

from app.services.document_service import list_documents, delete_document
from app.models.document import DocumentFragment


class TestListDocuments:
    def test_list_all_documents(self):
        mock_db = MagicMock()
        mock_query = mock_db.query.return_value
        mock_query.count.return_value = 5
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [
            DocumentFragment(id=1, content="test", content_type="doc_fragment",
                             course_name="Python", source_file="test.md")
        ]

        results, total = list_documents(mock_db, page=1, page_size=20)
        assert total == 5
        assert len(results) == 1
        assert results[0].content_type == "doc_fragment"

    def test_list_documents_filter_by_content_type(self):
        mock_db = MagicMock()
        mock_query = mock_db.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 2
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

        results, total = list_documents(mock_db, content_type="course_intro")
        assert total == 2

    def test_list_documents_filter_by_course(self):
        mock_db = MagicMock()
        mock_query = mock_db.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 1
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

        results, total = list_documents(mock_db, course_name="Python")
        assert total == 1

    def test_list_documents_text_search(self):
        mock_db = MagicMock()
        mock_query = mock_db.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 0
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

        results, total = list_documents(mock_db, search="hello")
        assert total == 0


class TestDeleteDocument:
    @patch("app.services.document_service.delete_by_ids")
    def test_delete_existing_document(self, mock_delete_ids):
        mock_db = MagicMock()
        fragment = DocumentFragment(id=1, chunk_id="abc-123")
        mock_db.get.return_value = fragment

        result = delete_document(mock_db, 1)
        assert result is True
        mock_db.delete.assert_called_once_with(fragment)
        mock_db.commit.assert_called_once()
        mock_delete_ids.assert_called_once_with(["abc-123"])

    def test_delete_nonexistent_document(self):
        mock_db = MagicMock()
        mock_db.get.return_value = None

        result = delete_document(mock_db, 999)
        assert result is False
        mock_db.delete.assert_not_called()
