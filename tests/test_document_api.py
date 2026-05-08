import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestListDocuments:
    @patch("app.api.documents.list_documents")
    def test_list_documents_defaults(self, mock_list):
        mock_list.return_value = ([], 0)
        resp = client.get("/documents")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["documents"] == []

    @patch("app.api.documents.list_documents")
    def test_list_documents_with_filters(self, mock_list):
        mock_list.return_value = ([], 0)
        resp = client.get("/documents?content_type=doc_fragment&course_name=Python&page=1&page_size=10")
        assert resp.status_code == 200
        mock_list.assert_called_once()


class TestDeleteDocument:
    @patch("app.api.documents.delete_document")
    def test_delete_success(self, mock_delete):
        mock_delete.return_value = True
        resp = client.delete("/documents/1")
        assert resp.status_code == 200
        assert resp.json() == {"deleted": True}

    @patch("app.api.documents.delete_document")
    def test_delete_not_found(self, mock_delete):
        mock_delete.return_value = False
        resp = client.delete("/documents/999")
        assert resp.status_code == 404


class TestListImportTasks:
    @patch("app.api.importer.list_import_tasks")
    def test_list_import_tasks(self, mock_list):
        mock_list.return_value = ([], 0)
        resp = client.get("/import/")
        assert resp.status_code == 200
        data = resp.json()
        assert "tasks" in data
        assert "total" in data
