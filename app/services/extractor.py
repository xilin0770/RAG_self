import json
import logging
import re
from typing import Any, Dict, List

from app.services.llm import get_llm

logger = logging.getLogger(__name__)

EXTRACTOR_PROMPT = """你是一个教育内容结构化提取助手。请从以下文本中提取所有题目和课程信息，以 JSON 格式返回。

对于每个题目，提取以下字段：
- content: 题目的完整内容
- question_type: 题目类型，必须是以下之一：single_choice（单选题）、multi_choice（多选题）、true_false（判断题）、fill_blank（填空题）、short_answer（简答题）
- options: 选项列表（如果是选择题），否则为空数组
- answer: 正确答案
- explanation: 题目解析或解答说明（如果有），否则为空字符串

对于每个课程，提取以下字段：
- name: 课程名称
- description: 课程描述
- prerequisites: 先修要求或前置知识
- target_audience: 目标受众
- learning_goals: 学习目标

请严格按照以下 JSON 格式输出，不要包含任何其他内容：

```json
{
  "questions": [
    {
      "content": "...",
      "question_type": "...",
      "options": ["...", "..."],
      "answer": "...",
      "explanation": "..."
    }
  ],
  "courses": [
    {
      "name": "...",
      "description": "...",
      "prerequisites": "...",
      "target_audience": "...",
      "learning_goals": "..."
    }
  ]
}
```

如果没有找到题目或课程，对应数组返回空。

以下是需要提取的文本：

{text}"""


def _split_text(text: str, max_chars: int = 3000) -> List[str]:
    """Split text into chunks at paragraph boundaries, each <= max_chars."""
    paragraphs = text.split("\n\n")
    chunks: List[str] = []
    current_chunk: List[str] = []
    current_len = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        para_len = len(para)

        # If adding this paragraph would exceed max_chars and we already
        # have content in current_chunk, finalize the current chunk
        if current_len + para_len > max_chars and current_chunk:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = []
            current_len = 0

        # If a single paragraph exceeds max_chars, force-split it
        if para_len > max_chars:
            # Finalize any pending chunk first
            if current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = []
                current_len = 0
            # Split the long paragraph at sentence-like boundaries
            sub_chunks = _split_long_paragraph(para, max_chars)
            chunks.extend(sub_chunks)
            continue

        current_chunk.append(para)
        current_len += para_len

    # Don't forget the last chunk
    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks


def _split_long_paragraph(text: str, max_chars: int) -> List[str]:
    """Split a single long paragraph into smaller chunks at sentence boundaries."""
    # Try to split at sentence endings
    sentences = re.split(r"(?<=[。.！!？?；;])\s*", text)
    chunks: List[str] = []
    current: List[str] = []
    current_len = 0

    for sentence in sentences:
        if not sentence.strip():
            continue
        sent_len = len(sentence)

        # If a single sentence exceeds max_chars, force-split it
        if sent_len > max_chars:
            if current:
                chunks.append("".join(current))
                current = []
                current_len = 0
            for i in range(0, sent_len, max_chars):
                chunks.append(sentence[i : i + max_chars])
            continue

        if current_len + sent_len > max_chars and current:
            chunks.append("".join(current))
            current = []
            current_len = 0
        current.append(sentence)
        current_len += sent_len

    if current:
        chunks.append("".join(current))

    return chunks


def _parse_llm_response(raw: str) -> Dict[str, Any]:
    """Extract JSON from LLM response text.

    Handles markdown code blocks (```json ... ```) and bare JSON.
    Returns a dict with 'questions' and 'courses' keys, or {} on failure.
    """
    if not raw or not raw.strip():
        return {}

    text = raw.strip()

    # Try to extract JSON from markdown code block: ```json ... ```
    json_pattern = r"```(?:json)?\s*\n?(.*?)```"
    matches = re.findall(json_pattern, text, re.DOTALL)

    candidates = matches if matches else [text]

    for candidate in candidates:
        candidate = candidate.strip()
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                # Normalise: ensure expected keys exist
                result: Dict[str, Any] = {
                    "questions": parsed.get("questions", []),
                    "courses": parsed.get("courses", []),
                }
                return result
        except (json.JSONDecodeError, TypeError):
            continue

    # Try to find a JSON object anywhere in the text as a last resort
    brace_pattern = r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}"
    brace_matches = re.findall(brace_pattern, text, re.DOTALL)
    for match in brace_matches:
        try:
            parsed = json.loads(match)
            if isinstance(parsed, dict) and (
                "questions" in parsed or "courses" in parsed
            ):
                return {
                    "questions": parsed.get("questions", []),
                    "courses": parsed.get("courses", []),
                }
        except (json.JSONDecodeError, TypeError):
            continue

    logger.warning("Failed to parse JSON from LLM response: %s...", raw[:200])
    return {}


def _extract_one_chunk(text: str) -> Dict[str, Any]:
    """Call LLM with EXTRACTOR_PROMPT and parse the response.

    Returns a dict with 'questions' and 'courses', or {} on error.
    """
    try:
        llm = get_llm()
        prompt = EXTRACTOR_PROMPT.format(text=text)
        response = llm.invoke([{"role": "user", "content": prompt}])
        return _parse_llm_response(response.content)
    except Exception as e:
        logger.warning("LLM extraction failed for chunk: %s", e)
        return {}


def _merge_results(all_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge extraction results from multiple chunks, deduplicating.

    Questions are deduplicated by their 'content' field.
    Courses are deduplicated by their 'name' field.
    """
    seen_questions: set = set()
    seen_courses: set = set()
    merged_questions: List[Dict[str, Any]] = []
    merged_courses: List[Dict[str, Any]] = []

    for result in all_results:
        if not result:
            continue

        for q in result.get("questions", []):
            content = q.get("content", "")
            if content and content not in seen_questions:
                seen_questions.add(content)
                merged_questions.append(q)

        for c in result.get("courses", []):
            name = c.get("name", "")
            if name and name not in seen_courses:
                seen_courses.add(name)
                merged_courses.append(c)

    return {
        "questions": merged_questions,
        "courses": merged_courses,
    }


def extract_structured_content(
    text: str, filename: str = ""
) -> Dict[str, Any]:
    """Extract structured questions and courses from document text.

    Splits long text into chunks, extracts from each via LLM, then merges
    results with deduplication.

    Args:
        text: The document text to extract from.
        filename: Optional filename for logging context.

    Returns:
        Dict with 'questions' and 'courses' lists.
    """
    if not text or not text.strip():
        return {"questions": [], "courses": []}

    try:
        chunks = _split_text(text)

        all_results: List[Dict[str, Any]] = []
        for chunk in chunks:
            result = _extract_one_chunk(chunk)
            all_results.append(result)

        return _merge_results(all_results)
    except Exception as e:
        logger.warning(
            "extract_structured_content failed for '%s': %s", filename, e
        )
        return {"questions": [], "courses": []}
