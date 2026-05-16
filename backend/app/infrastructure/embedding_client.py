import hashlib
import importlib.util
import os
import re
from typing import Any, Optional

openai_spec = importlib.util.find_spec("openai")
if openai_spec is not None:
    openai_module = importlib.import_module("openai")
    OpenAI = openai_module.OpenAI
    _OPENAI_AVAILABLE = True
else:  # pragma: no cover
    OpenAI = None
    _OPENAI_AVAILABLE = False

from app.core.config import settings


class EmbeddingClient:
    def __init__(self) -> None:
        self.api_key = settings.llm_api_key or os.getenv("OPENAI_API_KEY")
        self.client: Optional[Any] = None
        self.vector_size = 1536

        if self.api_key and _OPENAI_AVAILABLE:
            self.client = OpenAI(api_key=self.api_key)

    def embed(self, text: str) -> list[float]:
        if not text:
            return []

        if self.client:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text,
            )
            return response.data[0].embedding

        return self._fallback_embedding(text)

    def _fallback_embedding(self, text: str) -> list[float]:
        normalized = re.sub(r"\s+", " ", text.strip().lower())
        vector = [0.0] * self.vector_size
        tokens = normalized.split(" ")

        for index, token in enumerate(tokens):
            digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
            value = int(digest[:8], 16) / 0xFFFFFFFF
            vector[index % self.vector_size] += value

        length = sum(value * value for value in vector) ** 0.5
        if length > 0:
            vector = [value / length for value in vector]

        return vector
