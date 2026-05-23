import hashlib
import math
import re
import unicodedata
from dataclasses import dataclass
from typing import Any
from uuid import NAMESPACE_URL, uuid5

import httpx

from app.domain.models import DocumentChunk
from app.infrastructure.rag.simple_retriever import RetrievalResult

VECTOR_SIZE = 256


@dataclass(frozen=True, slots=True)
class QdrantConfig:
    url: str
    collection: str


class QdrantRetriever:
    def __init__(self, config: QdrantConfig, repository: Any) -> None:
        self.config = config
        self.repository = repository
        self.base_url = config.url.rstrip("/")
        self._client = httpx.Client(timeout=10.0)
        self.synchronize()

    def synchronize(self) -> int:
        self._ensure_collection()
        chunks = self.repository.list_active_chunks()
        if not chunks:
            return 0
        points = [
            {
                "id": str(uuid5(NAMESPACE_URL, chunk.id)),
                "vector": _embed(_chunk_embedding_text(chunk)),
                "payload": {
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "content": chunk.content,
                    "metadata": chunk.metadata,
                },
            }
            for chunk in chunks
        ]
        response = self._client.put(
            f"{self.base_url}/collections/{self.config.collection}/points",
            params={"wait": "true"},
            json={"points": points},
        )
        response.raise_for_status()
        return len(points)

    def search(self, query: str, top_k: int = 3) -> list[RetrievalResult]:
        vector = _embed(query)
        response = self._client.post(
            f"{self.base_url}/collections/{self.config.collection}/points/query",
            json={"query": vector, "limit": top_k, "with_payload": True},
        )
        if response.status_code == 404:
            response = self._client.post(
                f"{self.base_url}/collections/{self.config.collection}/points/search",
                json={"vector": vector, "limit": top_k, "with_payload": True},
            )
        response.raise_for_status()
        result = response.json().get("result", {})
        points = result.get("points", result) if isinstance(result, dict) else result
        return [
            RetrievalResult(
                chunk=DocumentChunk(
                    id=point["payload"]["chunk_id"],
                    document_id=point["payload"]["document_id"],
                    content=point["payload"]["content"],
                    metadata=point["payload"]["metadata"],
                ),
                score=round(float(point["score"]), 4),
            )
            for point in points
        ]

    def _ensure_collection(self) -> None:
        response = self._client.get(
            f"{self.base_url}/collections/{self.config.collection}",
        )
        if response.status_code == 200:
            return
        if response.status_code != 404:
            response.raise_for_status()
        response = self._client.put(
            f"{self.base_url}/collections/{self.config.collection}",
            json={"vectors": {"size": VECTOR_SIZE, "distance": "Cosine"}},
        )
        response.raise_for_status()


def _embed(text: str) -> list[float]:
    vector = [0.0] * VECTOR_SIZE
    for token in _tokens(text):
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:2], byteorder="big") % VECTOR_SIZE
        direction = 1.0 if digest[2] % 2 == 0 else -1.0
        vector[index] += direction
    norm = math.sqrt(sum(value * value for value in vector))
    return [value / norm for value in vector] if norm else vector


def _chunk_embedding_text(chunk: DocumentChunk) -> str:
    return " ".join(
        [
            chunk.content,
            chunk.metadata.get("title", ""),
            chunk.metadata.get("category", ""),
        ]
    )


def _tokens(text: str) -> list[str]:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    return re.findall(r"[a-z0-9]{3,}", ascii_text)
