import os
from dataclasses import dataclass


def _bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_name: str = "Assistente de Atendimento Inteligente"
    environment: str = "local"
    mysql_url: str = "mysql+pymysql://assistente:assistente@localhost:3306/atendimento"
    qdrant_url: str = "http://localhost:6333"
    llm_provider: str = "mock"
    llm_api_key: str = ""
    telegram_bot_token: str = ""
    min_relevance_score: float = 0.35
    enable_mcp_simulated: bool = True


settings = Settings(
    app_name=os.getenv("APP_NAME", "Assistente de Atendimento Inteligente"),
    environment=os.getenv("ENVIRONMENT", "local"),
    mysql_url=os.getenv("MYSQL_URL", "mysql+pymysql://assistente:assistente@localhost:3306/atendimento"),
    qdrant_url=os.getenv("QDRANT_URL", "http://localhost:6333"),
    llm_provider=os.getenv("LLM_PROVIDER", "mock"),
    llm_api_key=os.getenv("LLM_API_KEY", ""),
    telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
    min_relevance_score=float(os.getenv("MIN_RELEVANCE_SCORE", "0.35")),
    enable_mcp_simulated=_bool_env("ENABLE_MCP_SIMULATED", True),
)
