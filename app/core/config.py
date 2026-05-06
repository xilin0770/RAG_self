from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # LLM (OpenAI compatible)
    openai_api_key: str = ""
    openai_api_base: str = "https://api.siliconflow.cn/v1"
    llm_default_model: str = "qwen-flash"
    llm_default_temperature: float = 0.1
    vl_model: str = "Qwen/Qwen3.5-27B"
    kg_model: str = "qwen-flash"

    # BGE Embedding
    bge_m3_path: str = ""
    bge_m3: str = "BAAI/bge-m3"
    bge_device: str = "cpu"
    bge_fp16: bool = False

    # BGE Reranker
    bge_reranker_large: str = ""
    bge_reranker_device: str = "cpu"
    bge_reranker_fp16: bool = False

    # ModelScope
    modelscope_offline: int = 1
    modelscope_cache: str = ""

    # Embedding
    embedding_dim: int = 1024

    # Paths
    db_path: str = "data/education_kb.sqlite"
    chroma_path: str = "data/chroma_db"

    # Chunking
    chunk_size: int = 500
    chunk_overlap: int = 50

    # Retrieval
    top_k: int = 5

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    @property
    def database_url(self) -> str:
        return f"sqlite:///{self.db_path}"


settings = Settings()
