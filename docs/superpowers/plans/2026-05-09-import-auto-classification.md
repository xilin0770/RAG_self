# 导入自动分类提取 - 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 导入文档后并行执行 LLM 结构化提取，自动创建 Question 和 Course 记录。

**Architecture:** 在 `run_import` 中解析得到全文后，启动独立线程运行 `run_extraction`，与现有分块嵌入流程并行。`run_extraction` 调用新增的 `extractor.py` 服务，通过 LLM 分块提取结构化数据，写入 questions 和 courses 表。

**Tech Stack:** Python/FastAPI/SQLAlchemy/SQLite, ChatOpenAI (qwen-flash via siliconflow.cn), Vue 3/TypeScript/Element Plus

---

## File Structure

| 文件 | 操作 | 职责 |
|---|---|---|
| `app/models/import_task.py` | 修改 | 新增 questions_extracted, courses_extracted 列 |
| `app/services/extractor.py` | 新建 | LLM 结构化提取：分块调用 LLM，解析 JSON，合并去重 |
| `app/services/importer.py` | 修改 | 并行启动提取线程；新增 run_extraction 函数 |
| `app/api/importer.py` | 修改 | 状态 API 返回 questions_extracted, courses_extracted |
| `frontend/src/types/index.ts` | 修改 | ImportTask 接口新增字段 |
| `frontend/src/views/ImportView.vue` | 修改 | 表格显示提取结果列 |
| `tests/test_extractor.py` | 新建 | extractor 单元测试 |

---

### Task 1: ImportTask 模型新增提取统计字段

**Files:**
- Modify: `app/models/import_task.py`

- [ ] **Step 1: 添加 columns**

```python
# app/models/import_task.py
# 在 completed_chunks 之后、error_message 之前添加：

    questions_extracted = Column(Integer, default=0)
    courses_extracted = Column(Integer, default=0)
```

完整文件：

```python
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, Float, DateTime

from app.core.database import Base


class ImportTask(Base):
    __tablename__ = "import_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    file_name = Column(String(512), nullable=False)
    content_type = Column(String(50), default="", index=True)
    status = Column(String(50), nullable=False, default="pending", index=True)
    progress = Column(Float, default=0.0)
    total_chunks = Column(Integer, default=0)
    completed_chunks = Column(Integer, default=0)
    questions_extracted = Column(Integer, default=0)
    courses_extracted = Column(Integer, default=0)
    error_message = Column(Text, default="")
    metadata_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
```

- [ ] **Step 2: 验证**

```bash
cd /home/xilin/project/RAG_self && python -c "from app.models.import_task import ImportTask; print('columns:', [c.name for c in ImportTask.__table__.columns])"
```

Expected: columns 中包含 `questions_extracted` 和 `courses_extracted`

- [ ] **Step 3: Commit**

```bash
git add app/models/import_task.py
git commit -m "feat: add questions_extracted and courses_extracted columns to ImportTask"
```

---

### Task 2: 新建 LLM 结构化提取服务

**Files:**
- Create: `app/services/extractor.py`
- Create: `tests/test_extractor.py`

- [ ] **Step 1: 编写失败测试**

```python
# tests/test_extractor.py
import json
import pytest
from unittest.mock import MagicMock, patch
from app.services.extractor import extract_structured_content, EXTRACTOR_PROMPT


class TestExtractStructuredContent:
    def test_empty_text_returns_empty(self):
        result = extract_structured_content("", "test.md")
        assert result == {"questions": [], "courses": []}

    def test_no_json_in_response_returns_empty(self):
        with patch("app.services.extractor.get_llm") as mock_get_llm:
            mock_llm = MagicMock()
            mock_response = MagicMock()
            mock_response.content = "这里没有 JSON"
            mock_llm.invoke.return_value = mock_response
            mock_get_llm.return_value = mock_llm

            result = extract_structured_content("一些文本", "test.md")
            assert result == {"questions": [], "courses": []}

    def test_extracts_questions_from_llm_response(self):
        with patch("app.services.extractor.get_llm") as mock_get_llm:
            mock_llm = MagicMock()
            mock_response = MagicMock()
            mock_response.content = json.dumps({
                "questions": [
                    {
                        "content": "Python是什么？",
                        "question_type": "short_answer",
                        "options": [],
                        "answer": "一种编程语言",
                        "explanation": "Python是解释型语言"
                    }
                ],
                "courses": []
            }, ensure_ascii=False)
            mock_llm.invoke.return_value = mock_response
            mock_get_llm.return_value = mock_llm

            result = extract_structured_content("Python是一种编程语言", "test.md")
            assert len(result["questions"]) == 1
            assert result["questions"][0]["content"] == "Python是什么？"
            assert result["questions"][0]["question_type"] == "short_answer"

    def test_extracts_courses_from_llm_response(self):
        with patch("app.services.extractor.get_llm") as mock_get_llm:
            mock_llm = MagicMock()
            mock_response = MagicMock()
            mock_response.content = json.dumps({
                "questions": [],
                "courses": [
                    {
                        "name": "Python入门",
                        "description": "零基础课程",
                        "prerequisites": "无",
                        "target_audience": "初学者",
                        "learning_goals": "掌握基础语法"
                    }
                ]
            }, ensure_ascii=False)
            mock_llm.invoke.return_value = mock_response
            mock_get_llm.return_value = mock_llm

            result = extract_structured_content("课程介绍: Python入门...", "test.md")
            assert len(result["courses"]) == 1
            assert result["courses"][0]["name"] == "Python入门"

    def test_merges_duplicate_questions(self):
        with patch("app.services.extractor.get_llm") as mock_get_llm:
            mock_llm = MagicMock()
            responses = [
                json.dumps({
                    "questions": [{"content": "Q1?", "question_type": "short_answer", "options": [], "answer": "A1", "explanation": "E1"}],
                    "courses": []
                }, ensure_ascii=False),
                json.dumps({
                    "questions": [{"content": "Q1?", "question_type": "short_answer", "options": [], "answer": "A1", "explanation": "E1"}],
                    "courses": []
                }, ensure_ascii=False),
            ]
            mock_llm.invoke.side_effect = [
                MagicMock(content=r) for r in responses
            ]
            mock_get_llm.return_value = mock_llm

            # A text that will be split into 2 chunks (each > 800 chars triggers split)
            long_text = "Python是一种编程语言。" * 200  # ~3000 chars, will split into ~4 chunks
            result = extract_structured_content(long_text, "test.md")
            # duplicates should be merged
            assert len(result["questions"]) == 1

    def test_llm_error_returns_empty(self):
        with patch("app.services.extractor.get_llm") as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.invoke.side_effect = RuntimeError("API error")
            mock_get_llm.return_value = mock_llm

            result = extract_structured_content("一些文本", "test.md")
            assert result == {"questions": [], "courses": []}

    def test_malformed_json_returns_empty(self):
        with patch("app.services.extractor.get_llm") as mock_get_llm:
            mock_llm = MagicMock()
            mock_response = MagicMock()
            mock_response.content = "not valid json {{{"
            mock_llm.invoke.return_value = mock_response
            mock_get_llm.return_value = mock_llm

            result = extract_structured_content("文本", "test.md")
            assert result == {"questions": [], "courses": []}
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd /home/xilin/project/RAG_self && python -m pytest tests/test_extractor.py -v
```

Expected: FAIL (module not found)

- [ ] **Step 3: 实现 extractor 服务**

```python
# app/services/extractor.py
import json
import re
from typing import Any

from app.services.llm import get_llm

EXTRACTOR_PROMPT = """你是一个教育内容结构化提取助手。请从以下文本中提取所有题目和课程信息。

注意：
1. 如果文本包含题目（选择题、判断题、填空题、简答题等），提取每道题的完整信息
2. 如果文本包含课程介绍信息，提取课程元数据
3. question_type 必须是以下之一：single_choice, multi_choice, true_false, fill_blank, short_answer
4. 选项仅对 single_choice 和 multi_choice 有效，其他题型 options 为空数组
5. 如果文本中不包含某类内容，对应数组为空
6. 只返回 JSON，不要附加任何解释

文本内容：
{text}

请按以下 JSON 格式输出（只输出 JSON）：
{{"questions": [{{"content": "...", "question_type": "...", "options": [...], "answer": "...", "explanation": "..."}}], "courses": [{{"name": "...", "description": "...", "prerequisites": "...", "target_audience": "...", "learning_goals": "..."}}]}}"""


def _split_text(text: str, max_chars: int = 3000) -> list[str]:
    if len(text) <= max_chars:
        return [text]

    chunks = []
    paragraphs = text.split("\n\n")
    current = ""
    for para in paragraphs:
        if len(current) + len(para) < max_chars:
            current += para + "\n\n"
        else:
            if current.strip():
                chunks.append(current.strip())
            current = para + "\n\n"
    if current.strip():
        chunks.append(current.strip())
    return chunks or [text]


def _parse_llm_response(raw: str) -> dict:
    raw = raw.strip()
    # Try to extract JSON from markdown code blocks
    m = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", raw, re.DOTALL)
    if m:
        raw = m.group(1)
    try:
        data = json.loads(raw)
        if isinstance(data, dict) and ("questions" in data or "courses" in data):
            return {
                "questions": data.get("questions", []),
                "courses": data.get("courses", []),
            }
    except json.JSONDecodeError:
        pass
    return {}


def _extract_one_chunk(text: str) -> dict:
    llm = get_llm()
    prompt = EXTRACTOR_PROMPT.format(text=text)
    try:
        response = llm.invoke([
            {"role": "user", "content": prompt},
        ])
        return _parse_llm_response(response.content)
    except Exception:
        return {}


def _merge_results(all_results: list[dict]) -> dict:
    """Merge results from multiple chunks, deduplicating questions by content."""
    seen_contents = set()
    merged_questions = []
    merged_courses = {}
    for r in all_results:
        for q in r.get("questions", []):
            c = q.get("content", "").strip()
            if c and c not in seen_contents:
                seen_contents.add(c)
                merged_questions.append(q)
        for c in r.get("courses", []):
            name = c.get("name", "").strip()
            if name and name not in merged_courses:
                merged_courses[name] = c
    return {
        "questions": merged_questions,
        "courses": list(merged_courses.values()),
    }


def extract_structured_content(text: str, filename: str = "") -> dict:
    """从文档全文中提取结构化题目和课程信息。"""
    if not text.strip():
        return {"questions": [], "courses": []}

    chunks = _split_text(text)
    all_results = [_extract_one_chunk(c) for c in chunks]
    return _merge_results(all_results)
```

- [ ] **Step 4: 运行测试确认通过**

```bash
cd /home/xilin/project/RAG_self && python -m pytest tests/test_extractor.py -v
```

Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add app/services/extractor.py tests/test_extractor.py
git commit -m "feat: add LLM structured extraction service for questions and courses"
```

---

### Task 3: 修改 importer 服务，并行提取

**Files:**
- Modify: `app/services/importer.py`

- [ ] **Step 1: 更新 importer 测试（先写失败测试）**

在 `tests/test_importer.py` 中追加新测试：

```python
    @patch("app.services.importer.run_extraction")
    @patch("app.services.importer.RecursiveCharacterTextSplitter")
    @patch("app.services.importer.add_chunks")
    @patch("app.services.importer.embed_texts")
    @patch("app.services.importer.parse_document")
    @patch("app.services.importer.SessionLocal")
    def test_run_import_spawns_extraction_for_question_type(
        self,
        mock_session_local,
        mock_parse,
        mock_embed,
        mock_add,
        mock_splitter_class,
        mock_run_extraction,
    ):
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        mock_task = MagicMock()
        mock_task.id = 1
        mock_task.status = "pending"
        mock_db.get.return_value = mock_task

        mock_splitter = MagicMock()
        mock_splitter.split_text.return_value = ["chunk"]
        mock_splitter_class.return_value = mock_splitter

        mock_parse.return_value = "What is Python? A programming language."
        mock_embed.return_value = [[0.1] * 1024]
        mock_add.return_value = ["chunk-1"]

        metadata = {"content_type": "question", "course_name": "Python"}
        run_import(1, b"test", "test.md", metadata)

        mock_run_extraction.assert_called_once_with(1, "What is Python? A programming language.", "test.md", metadata)

    @patch("app.services.importer.run_extraction")
    @patch("app.services.importer.RecursiveCharacterTextSplitter")
    @patch("app.services.importer.add_chunks")
    @patch("app.services.importer.embed_texts")
    @patch("app.services.importer.parse_document")
    @patch("app.services.importer.SessionLocal")
    def test_run_import_skips_extraction_for_doc_fragment(
        self,
        mock_session_local,
        mock_parse,
        mock_embed,
        mock_add,
        mock_splitter_class,
        mock_run_extraction,
    ):
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        mock_task = MagicMock()
        mock_task.id = 1
        mock_task.status = "pending"
        mock_db.get.return_value = mock_task

        mock_splitter = MagicMock()
        mock_splitter.split_text.return_value = ["chunk"]
        mock_splitter_class.return_value = mock_splitter

        mock_parse.return_value = "Some document text."
        mock_embed.return_value = [[0.1] * 1024]
        mock_add.return_value = ["chunk-1"]

        metadata = {"content_type": "doc_fragment", "course_name": "Python"}
        run_import(1, b"test", "test.md", metadata)

        mock_run_extraction.assert_not_called()
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd /home/xilin/project/RAG_self && python -m pytest tests/test_importer.py::TestRunImport::test_run_import_spawns_extraction_for_question_type tests/test_importer.py::TestRunImport::test_run_import_skips_extraction_for_doc_fragment -v
```

Expected: FAIL (run_extraction not called / not defined)

- [ ] **Step 3: 修改 `run_import` 并新增 `run_extraction`**

```python
# app/services/importer.py
import threading
from datetime import datetime, timezone

from langchain_text_splitters import RecursiveCharacterTextSplitter

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.import_task import ImportTask
from app.models.document import DocumentFragment
from app.services.parser import parse_document
from app.services.embedding import embed_texts
from app.services.vector_store import add_chunks
from app.services.extractor import extract_structured_content
from app.services.question_service import create_question
from app.services.course_service import create_course


def run_extraction(
    task_id: int,
    text: str,
    filename: str,
    metadata: dict,
):
    """Run LLM structured extraction and persist results."""
    db = SessionLocal()
    try:
        result = extract_structured_content(text, filename)

        questions_count = 0
        courses_count = 0
        course_name = metadata.get("course_name", "")

        for q in result.get("questions", []):
            try:
                create_question(
                    db=db,
                    content=q.get("content", ""),
                    question_type=q.get("question_type", "short_answer"),
                    options=q.get("options", []),
                    answer=q.get("answer", ""),
                    explanation=q.get("explanation", ""),
                    course_name=course_name,
                    source_file=filename,
                )
                questions_count += 1
            except Exception:
                pass

        for c in result.get("courses", []):
            try:
                create_course(
                    db=db,
                    name=c.get("name", ""),
                    description=c.get("description", ""),
                    prerequisites=c.get("prerequisites", ""),
                    target_audience=c.get("target_audience", ""),
                    learning_goals=c.get("learning_goals", ""),
                )
                courses_count += 1
            except Exception:
                pass

        task = db.get(ImportTask, task_id)
        if task:
            task.questions_extracted = questions_count
            task.courses_extracted = courses_count
            task.updated_at = datetime.now(timezone.utc)
            db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


def run_import(
    task_id: int,
    file_bytes: bytes,
    filename: str,
    metadata: dict,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
):
    """Run the full import pipeline and update task status."""
    db = SessionLocal()
    try:
        task = db.get(ImportTask, task_id)
        if not task:
            return

        task.status = "processing"
        task.updated_at = datetime.now(timezone.utc)
        db.commit()

        # 1. Parse
        text = parse_document(file_bytes, filename)

        # 2. Start extraction in parallel for non-doc_fragment types
        content_type = metadata.get("content_type", "")
        if content_type in ("question", "course_intro"):
            t = threading.Thread(
                target=run_extraction,
                args=(task_id, text, filename, metadata),
                daemon=True,
            )
            t.start()

        # 3. Chunk with user-specified parameters
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "。", ".", " ", ""],
        )
        chunks = splitter.split_text(text)
        chunks = [c.strip() for c in chunks if c.strip()]
        if not chunks:
            raise ValueError("No text chunks produced")

        task.total_chunks = len(chunks)
        db.commit()

        # 4. Embed
        embeddings = embed_texts(chunks)

        # 5. Store in vector DB
        chunk_metadatas = [
            {
                "content_type": metadata.get("content_type", ""),
                "course_name": metadata.get("course_name", ""),
                "project_name": metadata.get("project_name", ""),
                "chapter_name": metadata.get("chapter_name", ""),
                "source_file": filename,
                "source_path": metadata.get("source_path", ""),
            }
            for _ in chunks
        ]
        chunk_ids = add_chunks(chunks, embeddings, chunk_metadatas)

        # 6. Write metadata to SQL
        for i, chunk in enumerate(chunks):
            fragment = DocumentFragment(
                content=chunk,
                content_type=metadata.get("content_type", ""),
                course_name=metadata.get("course_name", ""),
                project_name=metadata.get("project_name", ""),
                chapter_name=metadata.get("chapter_name", ""),
                source_file=filename,
                source_path=metadata.get("source_path", ""),
                chunk_id=chunk_ids[i],
            )
            db.add(fragment)

        # 7. Complete
        task.status = "completed"
        task.completed_chunks = len(chunks)
        task.progress = 100.0
        task.updated_at = datetime.now(timezone.utc)
        db.commit()

    except Exception as e:
        db.rollback()
        task = db.get(ImportTask, task_id)
        if task:
            task.status = "failed"
            task.error_message = str(e)
            task.updated_at = datetime.now(timezone.utc)
            db.commit()
    finally:
        db.close()
```

注意：list_import_tasks 函数保持不变。

- [ ] **Step 4: 运行全部 importer 测试**

```bash
cd /home/xilin/project/RAG_self && python -m pytest tests/test_importer.py -v
```

Expected: all tests pass (existing + 2 new)

- [ ] **Step 5: Commit**

```bash
git add app/services/importer.py tests/test_importer.py
git commit -m "feat: run LLM extraction in parallel during import for question/course types"
```

---

### Task 4: 修改 Import API 返回提取统计

**Files:**
- Modify: `app/api/importer.py`

- [ ] **Step 1: 修改状态查询 API 和列表 API**

在 `get_import_status` 返回中添加 `questions_extracted` 和 `courses_extracted`：

```python
# app/api/importer.py
# 修改 get_import_status 的 return 语句：

@router.get("/{task_id}/status")
async def get_import_status(task_id: int, db: Session = Depends(get_db)):
    task = db.get(ImportTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "task_id": task.id,
        "file_name": task.file_name,
        "content_type": task.content_type,
        "status": task.status,
        "progress": task.progress,
        "total_chunks": task.total_chunks,
        "completed_chunks": task.completed_chunks,
        "questions_extracted": task.questions_extracted,
        "courses_extracted": task.courses_extracted,
        "error_message": task.error_message,
        "created_at": task.created_at.isoformat() if task.created_at else "",
        "updated_at": task.updated_at.isoformat() if task.updated_at else "",
    }
```

同样修改列表 API：

```python
# app/api/importer.py
# 修改 api_list_import_tasks 的 return 语句中的 tasks 列表：

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
                "questions_extracted": t.questions_extracted,
                "courses_extracted": t.courses_extracted,
                "error_message": t.error_message,
                "created_at": t.created_at.isoformat() if t.created_at else "",
                "updated_at": t.updated_at.isoformat() if t.updated_at else "",
            }
            for t in tasks
        ],
    }
```

- [ ] **Step 2: 快速验证**

```bash
cd /home/xilin/project/RAG_self && python -c "from app.api.importer import router; print('router OK')"
```

Expected: `router OK`

- [ ] **Step 3: Commit**

```bash
git add app/api/importer.py
git commit -m "feat: return extraction stats in import task status API"
```

---

### Task 5: 前端类型定义更新

**Files:**
- Modify: `frontend/src/types/index.ts`

- [ ] **Step 1: 添加字段**

在 `ImportTask` 接口中添加：

```typescript
// frontend/src/types/index.ts
// 在 ImportTask 接口的 completed_chunks 之后添加：
  questions_extracted?: number
  courses_extracted?: number
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/types/index.ts
git commit -m "feat: add extraction stat fields to ImportTask type"
```

---

### Task 6: 前端 ImportView 显示提取结果

**Files:**
- Modify: `frontend/src/views/ImportView.vue`

- [ ] **Step 1: 在表格中新增"提取结果"列**

在 `<el-table>` 的 `<el-table-column prop="completed_chunks" />` 之后、"操作"列之前添加：

```html
        <el-table-column label="提取结果" width="160">
          <template #default="{ row }">
            <template v-if="row.status === 'completed'">
              <span v-if="(row.questions_extracted || 0) + (row.courses_extracted || 0) > 0">
                <span v-if="row.questions_extracted">题目 {{ row.questions_extracted }} 道</span>
                <span v-if="row.questions_extracted && row.courses_extracted">，</span>
                <span v-if="row.courses_extracted">课程 {{ row.courses_extracted }} 门</span>
              </span>
              <span v-else style="color: #909399">-</span>
            </template>
            <template v-else>
              <span style="color: #909399">-</span>
            </template>
          </template>
        </el-table-column>
```

- [ ] **Step 2: 构建验证**

```bash
cd /home/xilin/project/RAG_self/frontend && npm run build
```

Expected: build succeeds

- [ ] **Step 3: Commit**

```bash
git add frontend/src/views/ImportView.vue
git commit -m "feat: show extraction results column in import task table"
```

---

### Task 7: 数据库迁移

**Files:**
- Modify: `app/core/database.py` (如果现有迁移模式用 ALTER TABLE)

- [ ] **Step 1: 检查现有数据库**

```bash
cd /home/xilin/project/RAG_self && sqlite3 data/education_kb.sqlite ".schema import_tasks"
```

- [ ] **Step 2: 添加 columns（如果数据库已存在）**

如果 `import_tasks` 表已经存在但没有新列，数据库启动时的 `init_db()` 会自动处理（SQLite 的 `CREATE TABLE IF NOT EXISTS` 不会修改已有表，需要手动 ALTER TABLE）。

在 `app/core/database.py` 的 `init_db()` 末尾追加：

```python
# app/core/database.py
# 在现有 ALTER TABLE migrations 之后添加：
    for col in ["questions_extracted", "courses_extracted"]:
        try:
            engine.execute(
                __import__("sqlalchemy").text(
                    f"ALTER TABLE import_tasks ADD COLUMN {col} INTEGER DEFAULT 0"
                )
            )
        except Exception:
            pass
```

实际上，检查现有模式：

```python
# 查看 database.py 当前的 init_db 实现
```

- [ ] **Step 3: Commit**

```bash
git add app/core/database.py
git commit -m "fix: add migration for new import_tasks columns"
```

---

### Task 8: 端到端验证

- [ ] **Step 1: 启动后端**

```bash
cd /home/xilin/project/RAG_self && python -m app.main &
sleep 3
```

- [ ] **Step 2: 启动前端 dev server**

```bash
cd /home/xilin/project/RAG_self/frontend && npm run dev &
sleep 3
```

- [ ] **Step 3: 后端健康检查**

```bash
curl -s http://127.0.0.1:8000/docs | head -5
```

- [ ] **Step 4: 测试导入 API（带 question 类型）**

创建一个测试 MD 文件：

```bash
echo '## 题目1
Python中用于定义函数的关键字是？
A. func
B. def
C. function
D. define
答案：B
解析：Python使用def关键字定义函数。

## 题目2
Python中的列表(list)是可变数据类型。（判断正误）
答案：正确
解析：列表创建后可以增删改元素，属于可变数据类型。' > /tmp/test_questions.md

# 上传 (需在服务器运行后执行)
curl -X POST http://127.0.0.1:8000/import \
  -F "files=@/tmp/test_questions.md" \
  -F "content_type=question" \
  -F "course_name=Python入门"
```

- [ ] **Step 5: 查看题库**

```bash
curl -s http://127.0.0.1:8000/questions | python -m json.tool
```

Expected: 返回提取到的题目

- [ ] **Step 6: 清理**

```bash
kill %1 %2 2>/dev/null
rm /tmp/test_questions.md
```
