from langchain_openai import ChatOpenAI

from app.core.config import settings


def get_llm(streaming: bool = False) -> ChatOpenAI:
    return ChatOpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_api_base,
        model=settings.llm_default_model,
        temperature=settings.llm_default_temperature,
        streaming=streaming,
    )


def get_llm_stream() -> ChatOpenAI:
    return get_llm(streaming=True)
