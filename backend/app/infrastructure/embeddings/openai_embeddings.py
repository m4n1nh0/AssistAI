from __future__ import annotations

import logging

import openai

from app.infrastructure.embeddings.service import EmbeddingService

logger = logging.getLogger(__name__)


class OpenAIEmbeddingService(EmbeddingService):
    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-3-small",
        timeout: int = 60,
    ) -> None:
        self.model = model
        self.client = openai.OpenAI(
            api_key=api_key,
            timeout=timeout,
            max_retries=2,
        )

    def embed(self, text: str) -> list[float]:
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text,
            )
            return response.data[0].embedding
        except openai.APIError as exc:
            logger.error("Erro ao gerar embedding OpenAI: %s", exc)
            raise

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts,
            )
            ordered = sorted(response.data, key=lambda item: item.index)
            return [item.embedding for item in ordered]
        except openai.APIError as exc:
            logger.error("Erro ao gerar embeddings batch OpenAI: %s", exc)
            raise
