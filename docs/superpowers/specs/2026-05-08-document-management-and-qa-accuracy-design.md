# Document Management & QA Accuracy — Design Spec

**Date:** 2026-05-08
**Status:** Approved

## Overview

Enhance the education knowledge base RAG system with:
1. Import history page — complete log of all past imports
2. Document library page — browse and delete documents in the database
3. Content type standardization — 3 fixed types for imports
4. MD document processing verification
5. Q&A accuracy guard — "不知道" when no relevant context exists
6. Unit tests for all touched services

## 1. Data Model

### ImportTask — Add column

```
content_type: String(50), default=""
```

Tracks the content type of each import task for filtering on the history page, without joining to document_fragments.

### DocumentFragment — No changes

Standardize `content_type` to 3 values: `doc_fragment`, `course_intro`, `question`.

### Existing data

Untouched. The 3-type dropdown maps to existing internal content_type values; current document_fragments rows remain valid.

## 2. API Endpoints

### New

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/import/` | List all import tasks (paginated, filterable by status, content_type, date) |
| `GET` | `/documents` | List document fragments (paginated, filterable by content_type, course_name, search) |
| `DELETE` | `/documents/{id}` | Delete a document fragment + its ChromaDB chunk by chunk_id |

### Modified

| Method | Path | Change |
|--------|------|--------|
| `POST` | `/import` | content_type now mapped from 3-value dropdown (already accepted as form param) |
| `GET` | `/import/{task_id}/status` | Response includes `content_type` field |

### Response shapes

`GET /import/`:
```json
{ "tasks": [{ "task_id": 1, "file_name": "...", "status": "completed", "content_type": "doc_fragment", ... }], "total": 100 }
```

`GET /documents` query params: `page`, `page_size`, `content_type`, `course_name`, `search` (searches content + source_file).

### New service

`app/services/document_service.py`:
- `list_documents()` — paginated, filtered query against DocumentFragment
- `delete_document(id)` — deletes from SQLite (document_fragments) and ChromaDB (by chunk_id)

## 3. Frontend

### 3a. ImportView changes

Replace free-text "内容类型" input with `<el-select>`:

| Label | Internal value |
|-------|---------------|
| 知识文档 | `doc_fragment` |
| 课程 | `course_intro` |
| 题目 | `question` |

Default: `doc_fragment`.

### 3b. ImportHistory page (`/history`)

- Table: Task ID, File Name, Content Type, Status, Progress, Created At
- Filters: status, content_type, date range
- Click completed task → expand to show which document fragments it created

### 3c. DocumentLibrary page (`/documents`)

- Table: ID, Content Type, Course, Project, Chapter, Source File, Content (truncated)
- Filters: content_type dropdown, course_name input, text search
- Delete button per row with confirmation dialog

### 3d. Sidebar

Add entries in AppLayout: 导入历史 (`/history`), 文档库 (`/documents`).

## 4. Q&A Guard

Two layers:

**Layer 1 — Retrieval threshold:** Filter out results below a similarity threshold in search_service. Return empty if none pass.

**Layer 2 — Prompt guard:** System prompt instructs: "If the context does not contain information relevant to the user's question, respond exactly with: 不知道"

If search_service returns empty results, skip the LLM call and return "不知道" directly.

## 5. MD Processing

Already implemented in `parser.py` (`.md`, `.markdown` extensions). Already accepted in frontend upload. Verify end-to-end.

## 6. Unit Tests

| Test file | Coverage |
|-----------|----------|
| `tests/test_parser.py` | All 5 formats parse correctly; empty files; binary garbage |
| `tests/test_search_service.py` | Retrieval with/without filter; empty results; threshold filtering |
| `tests/test_document_service.py` | List with filters; delete (SQL + ChromaDB); delete non-existent |
| `tests/test_question_service.py` | Q&A with context; without context → "不知道"; empty retrieval → "不知道" |
| `tests/test_importer.py` | Import pipeline per content_type; metadata flow to DocumentFragment |
