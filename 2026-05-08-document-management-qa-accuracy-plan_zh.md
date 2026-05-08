# 文档管理与 QA 准确性 - 实施计划

> ***适用于代理工作者：***必备子技能：使用超级能力：子代理驱动开发（推荐）或超级能力：执行计划来逐项实施本计划。步骤使用复选框（`- [ ]`）语法进行跟踪。

***目标：** 添加导入历史、文档库、内容类型标准化、MD 验证、QA 准确性防护（"不知道"）和单元测试。

***架构：** 新增 `document_service.py` 处理文档列表/删除；新增 API 路由 `/import/` （列表）、 `/documents` （列表 + 删除）；新增两个 Vue 页面（ImportHistory、DocumentLibrary）；QA 防护使用检索阈值 + 提示规则；内容类型变为三选一的下拉式。

***技术栈：** Python 3.12、FastAPI、SQLAlchemy、ChromaDB、LangChain、Vue 3 + Element Plus、pytest

----

### 任务 1：在 ImportTask 中添加 `content_type` 列

***文件:**
- 修改: `app/models/import_task.py:10-20`
- 修改: `app/services/importer.py:41-47`
- 修改: `app/api/importer.py:19,30`

- [ ] **第 1 步：在模型中添加列***

在 `app/models/import_task.py`中，在 `file_name` 列（第 12 行）之后添加:

```python
content_type = Column(String(50), default="", index=True)
```

- [ ] **第 2 步：更新导入器服务以存储内容类型***

在 `app/services/importer.py`中

```python
task = ImportTask(
    file_name=file.filename or "unknown",
    content_type=metadata.get("content_type", ""),
    status="pending",
    metadata_json=json.dumps(metadata, ensure_ascii=False),
    created_at=datetime.now(timezone.utc),
    updated_at=datetime.now(timezone.utc),
)
```

- ，更新 ImportTask 创建（大约第 41-47 行）：

[ ] **步骤 3：更新导入器 API，将 content_type 默认为 "doc_fragment "** `app/api/importer.py`在

```python
content_type: str = Form(default="doc_fragment"),
```

- 中，更改第 19 行：

```bash
cd /home/xilin/project/RAG_self && python -c "
from app.core.database import engine, Base
from app.models import import_task
Base.metadata.create_all(bind=engine)
print('Migration complete')
"
```

[ ] **步骤 4：运行迁移并验证** `Migration complete`

- 预期：FAIL -

```bash
git add app/models/import_task.py app/services/importer.py app/api/importer.py
git commit -m "feat: add content_type column to import_tasks"
```

[ ] **步骤 3：实现 document_service****

### Create

:
- [ ] **步骤 4：运行测试以验证它们是否通过*** `app/services/document_service.py`
- 预期：通过 (6 个测试)FAIL - 导入错误（新端点尚不存在） `tests/test_document_service.py`

- [ ] **第三步：创建文档 API 路由器***

创建 `tests/test_document_service.py`：

```python
import pytest
from unittest.mock import MagicMock, patch

from app.services.document_service import list_documents, delete_document
from app.models.document import DocumentFragment


class TestListDocuments:
    def test_list_all_documents(self):
        mock_db = MagicMock()
        mock_query = mock_db.query.return_value
        mock_query.count.return_value = 5
        mock_query.offset.return_value.limit.return_value.all.return_value = [
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
        mock_query.offset.return_value.limit.return_value.all.return_value = []

        results, total = list_documents(mock_db, content_type="course_intro")
        assert total == 2

    def test_list_documents_filter_by_course(self):
        mock_db = MagicMock()
        mock_query = mock_db.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 1
        mock_query.offset.return_value.limit.return_value.all.return_value = []

        results, total = list_documents(mock_db, course_name="Python")
        assert total == 1

    def test_list_documents_text_search(self):
        mock_db = MagicMock()
        mock_query = mock_db.query.return_value
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 0
        mock_query.offset.return_value.limit.return_value.all.return_value = []

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
```

- [ ] **第四步：添加列表导入任务端点和函数***

```bash
cd /home/xilin/project/RAG_self && python -m pytest tests/test_document_service.py -v
```

在 `ModuleNotFoundError: No module named 'app.services.document_service'`

- 然后，更新现有的导入行：

更改为： `app/services/document_service.py`然后在文件末尾添加：

```python
from sqlalchemy.orm import Session

from app.models.document import DocumentFragment
from app.services.vector_store import delete_by_ids


def list_documents(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    content_type: str = "",
    course_name: str = "",
    search: str = "",
):
    q = db.query(DocumentFragment)
    if content_type:
        q = q.filter(DocumentFragment.content_type == content_type)
    if course_name:
        q = q.filter(DocumentFragment.course_name == course_name)
    if search:
        pattern = f"%{search}%"
        q = q.filter(
            DocumentFragment.content.ilike(pattern)
            | DocumentFragment.source_file.ilike(pattern)
        )
    total = q.count()
    results = q.order_by(DocumentFragment.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return results, total


def delete_document(db: Session, document_id: int) -> bool:
    fragment = db.get(DocumentFragment, document_id)
    if not fragment:
        return False
    if fragment.chunk_id:
        delete_by_ids([fragment.chunk_id])
    db.delete(fragment)
    db.commit()
    return True
```

- 同时更新

```bash
cd /home/xilin/project/RAG_self && python -m pytest tests/test_document_service.py -v
```

端点响应以包含

- 。在响应 dict 中，在

```bash
git add app/services/document_service.py tests/test_document_service.py
git commit -m "feat: add document_service with list and delete operations"
```

:

### [ ]之后 **步骤 5：向导入器服务添加

函数**
- 在 `app/api/documents.py`
- 中，首先向文件顶部的 SQLAlchemy 导入添加 `app/api/importer.py:60-77`
- 。更改： `app/main.py` （如果尚未存在，则添加该行；如果缺少，则添加）

- 然后在

函数后添加： `tests/test_document_api.py`[ ] **步骤 6：在 main.py 中注册文档路由器***

```python
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
```

- 首先阅读

```bash
cd /home/xilin/project/RAG_self && python -m pytest tests/test_document_api.py -v 2>&1 | head -20
```

以找到路由器注册模式，然后添加：

- [ ] **步骤 7：运行测试以验证它们是否通过***

预期：PASS (5 tests) `app/api/documents.py`[ ] **步骤 8: Commit****

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.document_service import list_documents, delete_document

router = APIRouter(prefix="/documents", tags=["文档管理"])


@router.get("")
async def api_list_documents(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    content_type: str = Query(default=""),
    course_name: str = Query(default=""),
    search: str = Query(default=""),
    db: Session = Depends(get_db),
):
    results, total = list_documents(
        db,
        page=page,
        page_size=page_size,
        content_type=content_type,
        course_name=course_name,
        search=search,
    )
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "documents": [
            {
                "id": f.id,
                "content": f.content[:300],
                "content_type": f.content_type,
                "course_name": f.course_name,
                "project_name": f.project_name,
                "chapter_name": f.chapter_name,
                "source_file": f.source_file,
                "source_path": f.source_path,
                "chunk_id": f.chunk_id,
            }
            for f in results
        ],
    }


@router.delete("/{document_id}")
async def api_delete_document(document_id: int, db: Session = Depends(get_db)):
    ok = delete_document(db, document_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"deleted": True}
```

- ---

Task 4: Add retrieval threshold to search_service `app/api/importer.py`****Files:**

Modify: `from app.services.importer import run_import` Modify:

```python
from app.services.importer import run_import, list_import_tasks
```

(add threshold setting)

```python
@router.get("")
async def api_list_import_tasks(
    status: str = Query(default=""),
    content_type: str = Query(default=""),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    tasks, total = list_import_tasks(db, status=status, content_type=content_type, page=page, page_size=page_size)
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "tasks": [
            {
                "task_id": t.id,
                "file_name": t.file_name,
                "content_type": t.content_type,
                "status": t.status,
                "progress": t.progress,
                "total_chunks": t.total_chunks,
                "completed_chunks": t.completed_chunks,
                "error_message": t.error_message,
                "created_at": t.created_at.isoformat() if t.created_at else "",
                "updated_at": t.updated_at.isoformat() if t.updated_at else "",
            }
            for t in tasks
        ],
    }
```

Create: `get_import_status` [ ] **步骤 1：将 RETRIEVAL_THRESHOLD 添加到配置*** `content_type`Read `"file_name"`以找到模式，然后添加：

```python
"content_type": task.content_type,
```

- [ ] **步骤 2：编写失败测试*** `list_import_tasks` Create

: `app/services/importer.py`[ ] **步骤 3：运行测试以验证它们是否失败*** `Session` Expected：FAIL - 结果不为空（未应用阈值）

`from sqlalchemy.orm import Session` [ ] **步骤 4：在 search_service 中执行阈值过滤***

在 `run_import` 中，在距离计算（第 37 行）之后，添加阈值检查。将 for 循环改为：

```python
def list_import_tasks(
    db: Session,
    status: str = "",
    content_type: str = "",
    page: int = 1,
    page_size: int = 20,
):
    q = db.query(ImportTask)
    if status:
        q = q.filter(ImportTask.status == status)
    if content_type:
        q = q.filter(ImportTask.content_type == content_type)
    total = q.count()
    tasks = q.order_by(ImportTask.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return tasks, total
```

- [ ] **步骤 5：运行测试以验证它们是否通过***

预期： `app/main.py` [ ] **步骤 2：运行测试以验证当前行为***

```python
from app.api import documents
app.include_router(documents.router)
```

- 预期：

```bash
cd /home/xilin/project/RAG_self && python -m pytest tests/test_document_api.py -v
```

FAILS - 返回 "根据现有知识库无法回答该问题 "而非 "不知道"

- [ ] **步骤 3：更新 QA_SYSTEM_PROMPT****

```bash
git add app/api/documents.py app/api/importer.py app/services/importer.py app/main.py tests/test_document_api.py
git commit -m "feat: add document list/delete and import history list API endpoints"
```

In

###  中的提示（第 11-20 行）：

[ ] **步骤 4：更新 ask_sync****
- In `app/services/search_service.py:10-49`
-  中的空结果响应，更改第 67 行： `app/core/config.py` [ ] **步骤 5：更新 ask_stream****
- In `tests/test_search_service.py`

-  中的空结果响应，更改第 117 行：

[ ] **步骤 6：运行测试以验证它们是否通过** `app/core/config.py` Expected：

```python
retrieval_threshold: float = 0.3
```

- [ ] **步骤 2：运行所有解析器测试***

预期：PASS (all tests, including new ones) `tests/test_search_service.py`[ ] **步骤 3: Commit****

```python
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
```

- ---

```bash
cd /home/xilin/project/RAG_self && python -m pytest tests/test_search_service.py::TestSearchDocuments::test_search_filters_by_threshold -v
```

Task 7: Importer service tests

- ****Files:**

Create: `app/services/search_service.py`[ ] **步骤 1: Write importer tests****

```python
from app.core.config import settings

    for i, chunk_id in enumerate(results["ids"][0]):
        metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
        distance = results["distances"][0][i] if results.get("distances") else 0
        document = results["documents"][0][i] if results.get("documents") else ""
        score = 1 - distance  # cosine distance to similarity

        if score < settings.retrieval_threshold:
            continue

        output.append({
            ...
```

- Create

```bash
cd /home/xilin/project/RAG_self && python -m pytest tests/test_search_service.py -v
```

:

- [ ] **步骤 2: Run importer tests****

```bash
git add app/services/search_service.py app/core/config.py tests/test_search_service.py
git commit -m "feat: add retrieval similarity threshold to filter low-quality results"
```

Expected：

### [ ] **步骤 2：在导入 API 模块中添加 listImportTasks***


- ，在现有函数后添加： `app/services/qa_service.py:11-21,66-68,116-119`
- 同时更新 `tests/test_question_service.py`

- 的

返回类型： `tests/test_question_service.py`-无需更改代码，只是接口现在包含

```python
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
```

- 。

```bash
cd /home/xilin/project/RAG_self && python -m pytest tests/test_question_service.py -v 2>&1 | head -30
```

[ ] **步骤 3：创建文档 API 模块*** `test_ask_without_context_returns_dont_know` 创建

- ：

[ ] **步骤 4：验证 TypeScript 的编译*** `app/services/qa_service.py`预期：

```python
QA_SYSTEM_PROMPT = """你是一个教育知识库助手。请根据以下知识库片段回答用户的问题。

要求：
1. 只根据提供的片段内容回答，不要编造信息
2. 如果片段中没有相关信息，请只回复"不知道"
3. 回答时引用相关片段编号，如 [1]、[2]
4. 回答尽量简洁、准确、结构化

知识库片段：
{context}"""
```

- 使用：

[ ] **步骤 2：验证 TypeScript 的编译** `app/services/qa_service.py`预期：No errors.

```python
        return {"answer": "不知道", "citations": []}
```

- [ ] **步骤 3: Commit****

--- `app/services/qa_service.py`Task 10: Frontend - ImportHistory page

```python
            yield _to_sse_data("不知道")
```

- ****Files:**

```bash
cd /home/xilin/project/RAG_self && python -m pytest tests/test_question_service.py -v
```

Create:

- [ ] **步骤 1: Create ImportHistoryView****

```bash
git add app/services/qa_service.py tests/test_question_service.py
git commit -m "feat: update QA guard to respond '不知道' when no relevant context"
```

Create

### :

[ ] **步骤 2: Verify TypeScript compiles****
- Expected：无错误。 `tests/test_parser.py`

- [ ] **步骤 2：添加侧边栏菜单项***

在 `tests/test_parser.py`中，在 "内容导入 "菜单项（第 18 行）后添加：

```python
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
        # Binary data should be parsed but likely produce garbage text;
        # parser should not crash
        text = parse_document(b"\x00\x01\x02\x03", "binary.pdf")
        assert isinstance(text, str)
```

- 添加

```bash
cd /home/xilin/project/RAG_self && python -m pytest tests/test_parser.py -v
```

并

- 到第 78 行的图标导入：

```bash
git add tests/test_parser.py
git commit -m "test: extend parser tests with md/markdown verification and edge cases"
```

[ ] **步骤 3：验证 TypeScript 的编译***

### 预期：没有错误：

(验证阈值是否设置）
- [ ] **步骤 1：验证设置中是否存在 RETRIEVAL_THRESHOLD** `tests/test_importer.py`

- 预期：

（或配置值） `tests/test_importer.py`[ ] **步骤 2：运行所有后端测试**

```python
import json
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from app.services.importer import run_import


class TestRunImport:
    @patch("app.services.importer.add_chunks")
    @patch("app.services.importer.embed_texts")
    @patch("app.services.importer.parse_document")
    @patch("app.services.importer.SessionLocal")
    def test_run_import_success_flow(self, mock_session_local, mock_parse, mock_embed, mock_add):
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        mock_task = MagicMock()
        mock_task.id = 1
        mock_task.status = "pending"
        mock_db.get.return_value = mock_task

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
    def test_run_import_metadata_flows_to_document_fragment(self, mock_session_local, mock_parse, mock_embed, mock_add):
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
```

- 预期：所有测试通过：

```bash
cd /home/xilin/project/RAG_self && python -m pytest tests/test_importer.py -v
```

[ ] **步骤 3：启动后端并验证新端点的响应***

- 预期：200、200、404（未找到文档）

```bash
git add tests/test_importer.py
git commit -m "test: add importer service unit tests"
```

[ ] **步骤 4：提交**。

### undefined

undefined
- undefined `frontend/src/types/index.ts`
- undefined `frontend/src/api/documents.ts`
- undefined `frontend/src/api/import.ts`

- undefined

undefined `frontend/src/types/index.ts`undefined `ImportTask`undefined

```typescript
export interface ImportTask {
  task_id: number
  file_name: string
  content_type: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  total_chunks: number
  completed_chunks: number
  error_message?: string
  created_at: string
  updated_at: string
}
```

undefined

```typescript
export interface DocumentFragment {
  id: number
  content: string
  content_type: string
  course_name: string
  project_name: string
  chapter_name: string
  source_file: string
  source_path: string
  chunk_id: string
}

export interface DocumentListResponse {
  total: number
  page: number
  page_size: number
  documents: DocumentFragment[]
}

export interface ImportTaskListResponse {
  total: number
  page: number
  page_size: number
  tasks: ImportTask[]
}
```

- undefined

undefined `frontend/src/api/import.ts`undefined

```typescript
import type { ImportTaskListResponse } from '@/types'

export async function listImportTasks(params: {
  status?: string
  content_type?: string
  page?: number
  page_size?: number
} = {}): Promise<ImportTaskListResponse> {
  const { data } = await client.get<ImportTaskListResponse>('/import/', { params })
  return data
}
```

undefined `ImportTask` undefined `getImportStatus` undefined `content_type`undefined

- undefined

undefined `frontend/src/api/documents.ts`undefined

```typescript
import client from './client'
import type { DocumentListResponse } from '@/types'

export async function listDocuments(params: {
  page?: number
  page_size?: number
  content_type?: string
  course_name?: string
  search?: string
} = {}): Promise<DocumentListResponse> {
  const { data } = await client.get<DocumentListResponse>('/documents', { params })
  return data
}

export async function deleteDocument(id: number): Promise<void> {
  await client.delete(`/documents/${id}`)
}
```

- undefined

```bash
cd /home/xilin/project/RAG_self/frontend && npx vue-tsc --noEmit 2>&1 | head -20
```

undefined

- undefined

```bash
git add frontend/src/types/index.ts frontend/src/api/import.ts frontend/src/api/documents.ts
git commit -m "feat: add frontend types and API modules for documents and import history"
```

undefined

### undefined

undefined
- undefined `frontend/src/views/ImportView.vue:34-38`

- undefined

undefined `frontend/src/views/ImportView.vue`undefined

```html
            <el-form-item label="内容类型">
              <el-input v-model="metadata.content_type" placeholder="doc_fragment" />
            </el-form-item>
```

undefined

```html
            <el-form-item label="内容类型">
              <el-select v-model="metadata.content_type" style="width: 200px">
                <el-option label="知识文档" value="doc_fragment" />
                <el-option label="课程" value="course_intro" />
                <el-option label="题目" value="question" />
              </el-select>
            </el-form-item>
```

- undefined

```bash
cd /home/xilin/project/RAG_self/frontend && npx vue-tsc --noEmit 2>&1 | head -20
```

undefined

- undefined

```bash
git add frontend/src/views/ImportView.vue
git commit -m "feat: replace content_type text input with 3-option dropdown"
```

undefined

### undefined

undefined
- undefined `frontend/src/views/ImportHistoryView.vue`

- undefined

undefined `frontend/src/views/ImportHistoryView.vue`undefined

```vue
<template>
  <div class="import-history-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>导入历史</span>
          <el-button @click="refresh">刷新</el-button>
        </div>
      </template>

      <el-row :gutter="12" style="margin-bottom: 12px">
        <el-col :span="6">
          <el-select v-model="filters.status" placeholder="状态筛选" clearable @change="refresh">
            <el-option label="等待中" value="pending" />
            <el-option label="处理中" value="processing" />
            <el-option label="已完成" value="completed" />
            <el-option label="失败" value="failed" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-select v-model="filters.content_type" placeholder="类型筛选" clearable @change="refresh">
            <el-option label="知识文档" value="doc_fragment" />
            <el-option label="课程" value="course_intro" />
            <el-option label="题目" value="question" />
          </el-select>
        </el-col>
      </el-row>

      <el-table :data="tasks" stripe v-loading="loading">
        <el-table-column prop="task_id" label="任务ID" width="80" />
        <el-table-column prop="file_name" label="文件名" min-width="180" />
        <el-table-column label="内容类型" width="100">
          <template #default="{ row }">{{ contentTypeLabel(row.content_type) }}</template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170" />
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button size="small" @click="toggleExpand(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        style="margin-top: 12px; justify-content: flex-end"
        layout="total, prev, pager, next"
        :total="total"
        :page-size="pageSize"
        v-model:current-page="page"
        @current-change="refresh"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { listImportTasks } from '@/api/import'
import type { ImportTask } from '@/types'

const tasks = ref<ImportTask[]>([])
const loading = ref(false)
const total = ref(0)
const page = ref(1)
const pageSize = 20

const filters = reactive({
  status: '',
  content_type: '',
})

async function refresh() {
  loading.value = true
  try {
    const data = await listImportTasks({
      status: filters.status || undefined,
      content_type: filters.content_type || undefined,
      page: page.value,
      page_size: pageSize,
    })
    tasks.value = data.tasks
    total.value = data.total
  } catch {
    // handled by interceptor
  } finally {
    loading.value = false
  }
}

function toggleExpand(_row: ImportTask) {
  // Navigate to document library filtered by source file
}

function statusTagType(status: string) {
  const map: Record<string, string> = {
    pending: 'info', processing: 'warning', completed: 'success', failed: 'danger',
  }
  return map[status] || 'info'
}

function statusLabel(status: string) {
  const map: Record<string, string> = {
    pending: '等待中', processing: '处理中', completed: '已完成', failed: '失败',
  }
  return map[status] || status
}

function contentTypeLabel(type: string) {
  const map: Record<string, string> = {
    doc_fragment: '知识文档', course_intro: '课程', question: '题目',
  }
  return map[type] || type
}

onMounted(refresh)
</script>
```

- undefined

```bash
cd /home/xilin/project/RAG_self/frontend && npx vue-tsc --noEmit 2>&1 | head -20
```

undefined

- undefined

```bash
git add frontend/src/views/ImportHistoryView.vue
git commit -m "feat: add ImportHistory page with status and type filters"
```

undefined

### undefined

undefined
- undefined `frontend/src/views/DocumentLibraryView.vue`

- undefined

undefined `frontend/src/views/DocumentLibraryView.vue`undefined

```vue
<template>
  <div class="document-library-view">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>文档库</span>
          <el-button @click="refresh">刷新</el-button>
        </div>
      </template>

      <el-row :gutter="12" style="margin-bottom: 12px">
        <el-col :span="6">
          <el-select v-model="filters.content_type" placeholder="类型筛选" clearable @change="refresh">
            <el-option label="知识文档" value="doc_fragment" />
            <el-option label="课程" value="course_intro" />
            <el-option label="题目" value="question" />
          </el-select>
        </el-col>
        <el-col :span="6">
          <el-input v-model="filters.course_name" placeholder="课程名" clearable @clear="refresh" @keyup.enter="refresh" />
        </el-col>
        <el-col :span="6">
          <el-input v-model="filters.search" placeholder="搜索内容" clearable @clear="refresh" @keyup.enter="refresh" />
        </el-col>
      </el-row>

      <el-table :data="documents" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column label="类型" width="100">
          <template #default="{ row }">{{ contentTypeLabel(row.content_type) }}</template>
        </el-table-column>
        <el-table-column prop="course_name" label="课程" width="120" />
        <el-table-column prop="project_name" label="项目" width="120" />
        <el-table-column prop="chapter_name" label="章节" width="120" />
        <el-table-column prop="source_file" label="来源文件" width="180" />
        <el-table-column label="内容预览" min-width="200">
          <template #default="{ row }">{{ row.content?.substring(0, 100) }}{{ row.content?.length > 100 ? '...' : '' }}</template>
        </el-table-column>
        <el-table-column label="操作" width="80">
          <template #default="{ row }">
            <el-popconfirm title="删除该文档？同时会移除向量嵌入。" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button type="danger" size="small">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        style="margin-top: 12px; justify-content: flex-end"
        layout="total, prev, pager, next"
        :total="total"
        :page-size="pageSize"
        v-model:current-page="page"
        @current-change="refresh"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { listDocuments, deleteDocument } from '@/api/documents'
import type { DocumentFragment } from '@/types'

const documents = ref<DocumentFragment[]>([])
const loading = ref(false)
const total = ref(0)
const page = ref(1)
const pageSize = 20

const filters = reactive({
  content_type: '',
  course_name: '',
  search: '',
})

async function refresh() {
  loading.value = true
  try {
    const data = await listDocuments({
      page: page.value,
      page_size: pageSize,
      content_type: filters.content_type || undefined,
      course_name: filters.course_name || undefined,
      search: filters.search || undefined,
    })
    documents.value = data.documents
    total.value = data.total
  } catch {
    // handled by interceptor
  } finally {
    loading.value = false
  }
}

async function handleDelete(id: number) {
  try {
    await deleteDocument(id)
    ElMessage.success('文档已删除')
    await refresh()
  } catch {
    // handled by interceptor
  }
}

function contentTypeLabel(type: string) {
  const map: Record<string, string> = {
    doc_fragment: '知识文档', course_intro: '课程', question: '题目',
  }
  return map[type] || type
}

onMounted(refresh)
</script>
```

- undefined

```bash
cd /home/xilin/project/RAG_self/frontend && npx vue-tsc --noEmit 2>&1 | head -20
```

undefined

- undefined

```bash
git add frontend/src/views/DocumentLibraryView.vue
git commit -m "feat: add DocumentLibrary page with filters and delete"
```

undefined

### undefined

undefined
- undefined `frontend/src/router/index.ts:11-52`
- undefined `frontend/src/components/AppLayout.vue:16-39`

- undefined

undefined `frontend/src/router/index.ts`undefined `]` undefined

```typescript
        {
          path: 'history',
          name: 'history',
          component: () => import('@/views/ImportHistoryView.vue'),
          meta: { title: '导入历史' },
        },
        {
          path: 'documents',
          name: 'documents',
          component: () => import('@/views/DocumentLibraryView.vue'),
          meta: { title: '文档库' },
        },
```

- undefined

undefined `frontend/src/components/AppLayout.vue`undefined

```html
        <el-menu-item index="/history">
          <el-icon><Clock /></el-icon>
          <span>导入历史</span>
        </el-menu-item>
        <el-menu-item index="/documents">
          <el-icon><Document /></el-icon>
          <span>文档库</span>
        </el-menu-item>
```

undefined `Clock` undefined `Document` undefined

```typescript
import {
  Upload, Reading, EditPen, Search, ChatDotSquare, List, Expand, Fold, Clock, Document,
} from '@element-plus/icons-vue'
```

- undefined

```bash
cd /home/xilin/project/RAG_self/frontend && npx vue-tsc --noEmit
```

undefined

- undefined

```bash
git add frontend/src/router/index.ts frontend/src/components/AppLayout.vue
git commit -m "feat: add history and documents routes and sidebar entries"
```

undefined

### undefined

undefined
- undefined `app/core/config.py` undefined

- undefined

```bash
cd /home/xilin/project/RAG_self && python -c "from app.core.config import settings; print(settings.retrieval_threshold)"
```

undefined `0.3` undefined

- undefined

```bash
cd /home/xilin/project/RAG_self && python -m pytest tests/ -v
```

undefined

- undefined

```bash
cd /home/xilin/project/RAG_self && python -c "
from fastapi.testclient import TestClient
from app.main import app
c = TestClient(app)
r1 = c.get('/import/')
print('GET /import/:', r1.status_code, r1.json())
r2 = c.get('/documents')
print('GET /documents:', r2.status_code, r2.json())
r3 = c.delete('/documents/99999')
print('DELETE /documents/99999:', r3.status_code, r3.json())
"
```

undefined

- undefined

```bash
git add app/core/config.py
git commit -m "chore: verify retrieval_threshold config and integration"
```
