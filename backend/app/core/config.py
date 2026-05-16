from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Assistente de Atendimento Inteligente"
    app_version: str = "0.1.0"
    environment: str = "local"

    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    mysql_url: str = "mysql+pymysql://assistant:assistant@localhost:3306/assistant"
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "knowledge_base"

    llm_provider: str = "stub"
    llm_api_key: str | None = None
    telegram_bot_token: str | None = None

    min_relevance_score: float = 0.35
    knowledge_base_path: str = "../docs/knowledge_base"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
