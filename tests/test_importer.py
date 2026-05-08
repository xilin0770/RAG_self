import json
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from app.services.importer import run_import


class TestRunImport:
    @patch("app.services.importer.RecursiveCharacterTextSplitter")
    @patch("app.services.importer.add_chunks")
    @patch("app.services.importer.embed_texts")
    @patch("app.services.importer.parse_document")
    @patch("app.services.importer.SessionLocal")
    def test_run_import_success_flow(
        self,
        mock_session_local,
        mock_parse,
        mock_embed,
        mock_add,
        mock_splitter_class,
    ):
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        mock_task = MagicMock()
        mock_task.id = 1
        mock_task.status = "pending"
        mock_db.get.return_value = mock_task

        # Mock the splitter to return exactly 2 chunks
        mock_splitter = MagicMock()
        mock_splitter.split_text.return_value = ["chunk one", "chunk two"]
        mock_splitter_class.return_value = mock_splitter

        mock_parse.return_value = "This is a test document. With multiple sentences. Enough for chunks."
        mock_embed.return_value = [[0.1] * 1024, [0.2] * 1024]
        mock_add.return_value = ["chunk-1", "chunk-2"]

        metadata = {"content_type": "doc_fragment", "course_name": "Python"}

        run_import(1, b"test content", "test.md", metadata)

        assert mock_task.status == "completed"
        assert mock_task.completed_chunks == 2
        assert mock_task.progress == 100.0

    @patch("app.services.importer.parse_document")
    @patch("app.services.importer.SessionLocal")
    def test_run_import_parse_failure(self, mock_session_local, mock_parse):
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        mock_task = MagicMock()
        mock_task.id = 1
        mock_db.get.return_value = mock_task

        mock_parse.side_effect = ValueError("Unsupported file type: .xyz")

        run_import(1, b"bad", "bad.xyz", {})

        assert mock_task.status == "failed"
        assert "Unsupported file type" in mock_task.error_message

    @patch("app.services.importer.parse_document")
    @patch("app.services.importer.SessionLocal")
    def test_run_import_no_text_extracted(self, mock_session_local, mock_parse):
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        mock_task = MagicMock()
        mock_task.id = 1
        mock_db.get.return_value = mock_task

        mock_parse.side_effect = ValueError("No text extracted")

        run_import(1, b"   ", "empty.txt", {})

        assert mock_task.status == "failed"

    @patch("app.services.importer.add_chunks")
    @patch("app.services.importer.embed_texts")
    @patch("app.services.importer.parse_document")
    @patch("app.services.importer.SessionLocal")
    def test_run_import_metadata_flows_to_document_fragment(
        self, mock_session_local, mock_parse, mock_embed, mock_add
    ):
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        mock_task = MagicMock()
        mock_task.id = 1
        mock_db.get.return_value = mock_task

        mock_parse.return_value = "Content here. More content."
        mock_embed.return_value = [[0.1] * 1024]
        mock_add.return_value = ["chunk-x"]

        metadata = {
            "content_type": "course_intro",
            "course_name": "Math 101",
            "project_name": "Final Project",
            "chapter_name": "Calculus",
            "source_path": "/courses/math/",
        }

        run_import(1, b"test", "calculus.md", metadata)

        # Verify DocumentFragment was created with correct metadata
        fragment_call = mock_db.add.call_args_list[0][0][0]
        assert fragment_call.content_type == "course_intro"
        assert fragment_call.course_name == "Math 101"
        assert fragment_call.project_name == "Final Project"
        assert fragment_call.chapter_name == "Calculus"
        assert fragment_call.chunk_id == "chunk-x"


class TestListImportTasks:
    @patch("app.services.importer.ImportTask")
    def test_list_all(self, mock_task_model):
        from app.services.importer import list_import_tasks

        mock_db = MagicMock()
        mock_query = mock_db.query.return_value
        mock_query.count.return_value = 3
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

        tasks, total = list_import_tasks(mock_db)
        assert total == 3

    @patch("app.services.importer.ImportTask")
    def test_list_filtered_by_status(self, mock_task_model):
        from app.services.importer import list_import_tasks

        mock_db = MagicMock()
        mock_query = mock_db.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 1
        mock_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []

        tasks, total = list_import_tasks(mock_db, status="completed")
        assert total == 1
