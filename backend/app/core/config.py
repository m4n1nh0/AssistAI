from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AssistAI"
    environment: str = "local"
    api_prefix: str = ""

    mysql_url: str = "mysql+pymysql://assistai:assistai@localhost:3306/assistai"

    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "assistai_knowledge"

    llm_provider: str = "mock"
    llm_api_key: str | None = None
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.3
    llm_max_tokens: int = 1024
    llm_timeout_seconds: int = 60

    embedding_provider: str | None = None
    embedding_api_key: str | None = None
    embedding_model: str = "text-embedding-3-small"

    telegram_bot_token: str | None = None

    min_relevance_score: float = 0.15
    max_message_chars: int = 2000
    mcp_simulated_enabled: bool = True
    rag_top_k: int = 5
    database_persistence: str = "memory"

    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="ASSISTAI_",
        env_nested_delimiter="__",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
