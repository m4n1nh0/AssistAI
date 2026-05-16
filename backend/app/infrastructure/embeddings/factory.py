from __future__ import annotations

import logging

from app.core.config import Settings
from app.infrastructure.embeddings.ollama_embeddings import OllamaEmbeddingService
from app.infrastructure.embeddings.openai_embeddings import OpenAIEmbeddingService
from app.infrastructure.embeddings.service import EmbeddingService

logger = logging.getLogger(__name__)


def create_embedding_service(settings: Settings) -> EmbeddingService:
    provider = settings.embedding_provider or settings.llm_provider

    if provider == "openai":
        api_key = settings.embedding_api_key or settings.llm_api_key
        if not api_key:
            logger.warning(
                "Embedding provider OpenAI sem API key, "
                "usando mock (embedding vazio)"
            )
            return _MockEmbeddingService()
        logger.info(
            "Usando OpenAI embeddings: model=%s", settings.embedding_model
        )
        return OpenAIEmbeddingService(
            api_key=api_key,
            model=settings.embedding_model,
            timeout=settings.llm_timeout_seconds,
        )

    if provider == "ollama":
        base_url = settings.llm_api_key or "http://localhost:11434"
        logger.info(
            "Usando Ollama embeddings: model=%s url=%s",
            settings.embedding_model,
            base_url,
        )
        return OllamaEmbeddingService(
            base_url=base_url,
            model=settings.embedding_model,
        )

    logger.info(
        "Nenhum embedding provider configurado (provider=%s), "
        "usando mock",
        provider,
    )
    return _MockEmbeddingService()


class _MockEmbeddingService(EmbeddingService):
    def embed(self, text: str) -> list[float]:
        return [0.0] * 384

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [[0.0] * 384 for _ in texts]
