from __future__ import annotations

import logging

import httpx

from app.infrastructure.embeddings.service import EmbeddingService

logger = logging.getLogger(__name__)


class OllamaEmbeddingService(EmbeddingService):
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "nomic-embed-text",
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model

    def embed(self, text: str) -> list[float]:
        try:
            with httpx.Client(timeout=60) as client:
                response = client.post(
                    f"{self.base_url}/api/embeddings",
                    json={"model": self.model, "prompt": text},
                )
                response.raise_for_status()
                return response.json()["embedding"]
        except httpx.HTTPError as exc:
            logger.error("Erro ao gerar embedding Ollama: %s", exc)
            raise

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(text) for text in texts]
