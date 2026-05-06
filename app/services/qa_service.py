import json
from typing import AsyncIterator, List

from sqlalchemy.orm import Session

from app.services.embedding import embed_query
from app.services.vector_store import search as vector_search
from app.services.llm import get_llm, get_llm_stream
from app.core.config import settings

QA_SYSTEM_PROMPT = """你是一个教育知识库助手。请根据以下知识库片段回答用户的问题。

要求：
1. 只根据提供的片段内容回答，不要编造信息
2. 如果片段中没有相关信息，请诚实地说"根据现有知识库无法回答该问题"
3. 回答时引用相关片段编号，如 [1]、[2]
4. 回答尽量简洁、准确、结构化

知识库片段：
{context}"""


def _to_sse_data(payload: str) -> str:
    """Format text as a valid SSE event, preserving multiline content."""
    lines = str(payload).splitlines() or [""]
    return "".join(f"data: {line}\n" for line in lines) + "\n"


def _friendly_llm_error(exc: Exception) -> str:
    msg = str(exc)
    if "Model does not exist" in msg or "code': 20012" in msg or '"code": 20012' in msg:
        return (
            "LLM 模型不存在或不可用，请检查 .env 的 LLM_DEFAULT_MODEL。"
            "可先尝试 Qwen/Qwen3.5-27B 或 deepseek-ai/DeepSeek-V3.2。"
        )
    return f"LLM 调用失败: {msg}"


def build_context(results: List[dict]) -> str:
    parts = []
    for i, r in enumerate(results, 1):
        source = f"课程:{r.get('course_name', '')} | 章节:{r.get('chapter_name', '')} | 来源:{r.get('source_file', '')}"
        parts.append(f"[{i}] {r['content']}\n   （来源：{source}）")
    return "\n\n".join(parts)


def ask_sync(query: str, db: Session) -> dict:
    """Single-turn RAG Q&A. Returns answer + citations."""
    # Retrieve
    query_embedding = embed_query(query)
    results = vector_search(query_embedding, top_k=settings.top_k)

    docs = []
    if results.get("ids") and results["ids"][0]:
        for i, chunk_id in enumerate(results["ids"][0]):
            metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
            document = results["documents"][0][i] if results.get("documents") else ""
            docs.append({
                "chunk_id": chunk_id,
                "content": document,
                "course_name": metadata.get("course_name", ""),
                "chapter_name": metadata.get("chapter_name", ""),
                "source_file": metadata.get("source_file", ""),
            })

    if not docs:
        return {"answer": "根据现有知识库无法回答该问题", "citations": []}

    # Generate
    context = build_context(docs)
    prompt = QA_SYSTEM_PROMPT.format(context=context)

    llm = get_llm()
    try:
        response = llm.invoke([
            {"role": "system", "content": prompt},
            {"role": "user", "content": query},
        ])
    except Exception as exc:
        raise RuntimeError(_friendly_llm_error(exc)) from exc

    return {
        "answer": response.content,
        "citations": [
            {
                "index": i + 1,
                "content": d["content"][:200],
                "course_name": d["course_name"],
                "chapter_name": d["chapter_name"],
                "source_file": d["source_file"],
            }
            for i, d in enumerate(docs)
        ],
    }


async def ask_stream(query: str) -> AsyncIterator[str]:
    """Streaming RAG Q&A. Yields SSE chunks."""
    try:
        # Retrieve
        query_embedding = embed_query(query)
        results = vector_search(query_embedding, top_k=settings.top_k)

        docs = []
        if results.get("ids") and results["ids"][0]:
            for i, chunk_id in enumerate(results["ids"][0]):
                metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
                document = results["documents"][0][i] if results.get("documents") else ""
                docs.append({
                    "content": document,
                    "course_name": metadata.get("course_name", ""),
                    "chapter_name": metadata.get("chapter_name", ""),
                    "source_file": metadata.get("source_file", ""),
                })

        if not docs:
            yield _to_sse_data("根据现有知识库无法回答该问题")
            yield _to_sse_data("[DONE]")
            return

        context = build_context(docs)
        prompt = QA_SYSTEM_PROMPT.format(context=context)

        llm = get_llm_stream()
        async for chunk in llm.astream([
            {"role": "system", "content": prompt},
            {"role": "user", "content": query},
        ]):
            if chunk.content:
                yield _to_sse_data(chunk.content)

        # Send citations at end
        citations = [
            {
                "index": i + 1,
                "content": d["content"][:200],
                "course_name": d["course_name"],
                "chapter_name": d["chapter_name"],
                "source_file": d["source_file"],
            }
            for i, d in enumerate(docs)
        ]
        yield _to_sse_data(f"[CITATIONS]{json.dumps(citations, ensure_ascii=False)}")
        yield _to_sse_data("[DONE]")
    except Exception as exc:
        yield _to_sse_data(f"[ERROR]{_friendly_llm_error(exc)}")
        yield _to_sse_data("[DONE]")
