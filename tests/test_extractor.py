import json
import pytest
from unittest.mock import MagicMock, patch

from app.services.extractor import (
    _parse_llm_response,
    _merge_results,
    extract_structured_content,
)


class TestParseLLMResponse:
    def test_no_json_in_response_returns_empty(self):
        """LLM returns text without JSON -> empty dict."""
        result = _parse_llm_response("This is just some text, no JSON at all.")
        assert result == {}

    def test_malformed_json_returns_empty(self):
        """Invalid JSON -> empty dict."""
        result = _parse_llm_response('{"questions": [broken json here}')
        assert result == {}

    def test_extracts_questions_from_bare_json(self):
        """Valid question JSON (bare) is parsed correctly."""
        raw = json.dumps({
            "questions": [
                {
                    "content": "What is 2+2?",
                    "question_type": "single_choice",
                    "options": ["1", "2", "3", "4"],
                    "answer": "4",
                    "explanation": "Basic arithmetic",
                }
            ],
            "courses": [],
        })
        result = _parse_llm_response(raw)
        assert len(result["questions"]) == 1
        assert result["questions"][0]["content"] == "What is 2+2?"
        assert result["questions"][0]["question_type"] == "single_choice"

    def test_extracts_courses_from_bare_json(self):
        """Valid course JSON (bare) is parsed correctly."""
        raw = json.dumps({
            "questions": [],
            "courses": [
                {
                    "name": "Python 101",
                    "description": "Intro to Python",
                    "prerequisites": "None",
                    "target_audience": "Beginners",
                    "learning_goals": "Learn Python",
                }
            ],
        })
        result = _parse_llm_response(raw)
        assert len(result["courses"]) == 1
        assert result["courses"][0]["name"] == "Python 101"
        assert result["courses"][0]["description"] == "Intro to Python"

    def test_extracts_from_markdown_code_block(self):
        """JSON wrapped in ```json ... ``` is parsed correctly."""
        raw = (
            '```json\n'
            + json.dumps({
                "questions": [
                    {
                        "content": "Explain OOP",
                        "question_type": "short_answer",
                        "options": [],
                        "answer": "Object-Oriented Programming",
                        "explanation": "...",
                    }
                ],
                "courses": [],
            })
            + '\n```'
        )
        result = _parse_llm_response(raw)
        assert len(result["questions"]) == 1
        assert result["questions"][0]["content"] == "Explain OOP"

    def test_extracts_from_markdown_code_block_no_lang(self):
        """JSON wrapped in ``` ... ``` (no language specifier) is parsed."""
        raw = (
            '```\n'
            + json.dumps({
                "questions": [],
                "courses": [
                    {
                        "name": "Math",
                        "description": "Mathematics",
                        "prerequisites": "",
                        "target_audience": "",
                        "learning_goals": "",
                    }
                ],
            })
            + '\n```'
        )
        result = _parse_llm_response(raw)
        assert len(result["courses"]) == 1
        assert result["courses"][0]["name"] == "Math"

    def test_extracts_both_questions_and_courses(self):
        """Response containing both questions and courses is parsed."""
        raw = json.dumps({
            "questions": [
                {
                    "content": "Q1",
                    "question_type": "true_false",
                    "options": ["True", "False"],
                    "answer": "True",
                    "explanation": "Because",
                }
            ],
            "courses": [
                {
                    "name": "Course 1",
                    "description": "Desc",
                    "prerequisites": "",
                    "target_audience": "",
                    "learning_goals": "",
                }
            ],
        })
        result = _parse_llm_response(raw)
        assert len(result["questions"]) == 1
        assert len(result["courses"]) == 1

    def test_extra_text_around_json_block(self):
        """Surrounding text around JSON code block is tolerated."""
        raw = (
            'Here is the result:\n\n'
            '```json\n'
            + json.dumps({
                "questions": [],
                "courses": [
                    {
                        "name": "Test",
                        "description": "T",
                        "prerequisites": "",
                        "target_audience": "",
                        "learning_goals": "",
                    }
                ],
            })
            + '\n```\n\nHope this helps!'
        )
        result = _parse_llm_response(raw)
        assert len(result["courses"]) == 1
        assert result["courses"][0]["name"] == "Test"


class TestMergeResults:
    def test_merges_duplicate_questions(self):
        """Same question content in multiple chunks -> deduplicated."""
        results = [
            {
                "questions": [
                    {
                        "content": "What is Python?",
                        "question_type": "short_answer",
                        "options": [],
                        "answer": "A language",
                        "explanation": "...",
                    }
                ],
                "courses": [],
            },
            {
                "questions": [
                    {
                        "content": "What is Python?",
                        "question_type": "short_answer",
                        "options": [],
                        "answer": "A language",
                        "explanation": "...",
                    }
                ],
                "courses": [],
            },
        ]
        merged = _merge_results(results)
        assert len(merged["questions"]) == 1

    def test_merges_duplicate_courses(self):
        """Same course name in multiple chunks -> deduplicated."""
        results = [
            {
                "questions": [],
                "courses": [
                    {
                        "name": "Python 101",
                        "description": "Intro",
                        "prerequisites": "",
                        "target_audience": "",
                        "learning_goals": "",
                    }
                ],
            },
            {
                "questions": [],
                "courses": [
                    {
                        "name": "Python 101",
                        "description": "Another desc",
                        "prerequisites": "",
                        "target_audience": "",
                        "learning_goals": "",
                    }
                ],
            },
        ]
        merged = _merge_results(results)
        assert len(merged["courses"]) == 1

    def test_keeps_unique_questions(self):
        """Different questions are both kept."""
        results = [
            {
                "questions": [
                    {
                        "content": "Q1",
                        "question_type": "short_answer",
                        "options": [],
                        "answer": "A1",
                        "explanation": "",
                    }
                ],
                "courses": [],
            },
            {
                "questions": [
                    {
                        "content": "Q2",
                        "question_type": "short_answer",
                        "options": [],
                        "answer": "A2",
                        "explanation": "",
                    }
                ],
                "courses": [],
            },
        ]
        merged = _merge_results(results)
        assert len(merged["questions"]) == 2

    def test_empty_results(self):
        """Empty list returns empty dict structure."""
        merged = _merge_results([])
        assert merged == {"questions": [], "courses": []}


class TestExtractStructuredContent:
    def test_empty_text_returns_empty(self):
        """Empty string returns empty dict."""
        result = extract_structured_content("")
        assert result == {"questions": [], "courses": []}

    def test_whitespace_only_returns_empty(self):
        """Whitespace-only text returns empty dict."""
        result = extract_structured_content("   \n\n  \n  ")
        assert result == {"questions": [], "courses": []}

    @patch("app.services.extractor._extract_one_chunk")
    def test_llm_error_returns_empty(self, mock_extract):
        """LLM raises exception -> empty result."""
        mock_extract.side_effect = Exception("LLM timeout")
        result = extract_structured_content("Some text content here.")
        assert result == {"questions": [], "courses": []}

    @patch("app.services.extractor._extract_one_chunk")
    def test_single_chunk_extraction(self, mock_extract):
        """Short text in one chunk is extracted and returned."""
        mock_extract.return_value = {
            "questions": [
                {
                    "content": "What is Python?",
                    "question_type": "short_answer",
                    "options": [],
                    "answer": "A language",
                    "explanation": "...",
                }
            ],
            "courses": [],
        }
        result = extract_structured_content("What is Python?")
        assert len(result["questions"]) == 1
        assert result["questions"][0]["content"] == "What is Python?"

    @patch("app.services.extractor._extract_one_chunk")
    def test_merges_across_chunks(self, mock_extract):
        """When text is split into multiple chunks, results are merged."""
        # Return the same question for each chunk call; merge should deduplicate
        mock_extract.return_value = {
            "questions": [
                {
                    "content": "What is Python?",
                    "question_type": "short_answer",
                    "options": [],
                    "answer": "A language",
                    "explanation": "...",
                }
            ],
            "courses": [],
        }
        # Build text long enough to split into multiple chunks (> 3000 chars
        # with paragraph breaks)
        paragraph = "Lorem ipsum dolor sit amet. " * 50
        long_text = "\n\n".join([paragraph] * 5)
        result = extract_structured_content(long_text)
        assert len(result["questions"]) == 1
