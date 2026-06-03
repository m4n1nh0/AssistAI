import hashlib
import math
from dataclasses import dataclass
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from app.domain.models import DocumentChunk
from app.infrastructure.rag.simple_retriever import RetrievalResult, SimpleRetriever
from app.infrastructure.repositories.memory import InMemoryRepository


@dataclass(frozen=True, slots=True)
class QdrantConfig:
    url: str
    collection: str
    vector_size: int = 128


def embed_text(text: str, size: int = 128) -> list[float]:
    vector = [0.0] * size
    for raw_token in text.lower().split():
        token = "".join(char for char in raw_token if char.isalnum())
        if not token:
            continue
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % size
        vector[index] += 1.0

    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [round(value / norm, 6) for value in vector]


class QdrantVectorStore:
    def __init__(self, config: QdrantConfig) -> None:
        self.config = config
        self._client: Any | None = None

    @property
    def available(self) -> bool:
        try:
            self._get_client().get_collections()
            return True
        except Exception:
            return False

    def ensure_collection(self) -> None:
        client = self._get_client()
        from qdrant_client.models import Distance, VectorParams

        existing = {collection.name for collection in client.get_collections().collections}
        if self.config.collection in existing:
            return

        client.create_collection(
            collection_name=self.config.collection,
            vectors_config=VectorParams(size=self.config.vector_size, distance=Distance.COSINE),
        )

    def upsert_chunks(self, chunks: list[DocumentChunk]) -> int:
        if not chunks:
            return 0

        self.ensure_collection()
        from qdrant_client.models import PointStruct

        points = [
            PointStruct(
                id=str(uuid5(NAMESPACE_URL, chunk.id)),
                vector=embed_text(chunk.content, self.config.vector_size),
                payload={
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "content": chunk.content,
                    **chunk.metadata,
                },
            )
            for chunk in chunks
        ]
        self._get_client().upsert(collection_name=self.config.collection, points=points)
        return len(points)

    def search(self, query: str, top_k: int = 3) -> list[tuple[DocumentChunk, float]]:
        self.ensure_collection()
        results = self._get_client().search(
            collection_name=self.config.collection,
            query_vector=embed_text(query, self.config.vector_size),
            limit=top_k,
            with_payload=True,
        )

        chunks: list[tuple[DocumentChunk, float]] = []
        for result in results:
            payload = result.payload or {}
            chunk = DocumentChunk(
                id=str(payload.get("chunk_id", result.id)),
                document_id=str(payload.get("document_id", "")),
                content=str(payload.get("content", "")),
                metadata={key: str(value) for key, value in payload.items() if key != "content"},
            )
            chunks.append((chunk, round(float(result.score), 4)))
        return chunks

    def _get_client(self) -> Any:
        if self._client is None:
            from qdrant_client import QdrantClient

            self._client = QdrantClient(url=self.config.url, timeout=0.5)
        return self._client


class HybridRetriever:
    def __init__(self, repository: InMemoryRepository, vector_store: QdrantVectorStore) -> None:
        self.repository = repository
        self.vector_store = vector_store
        self.fallback = SimpleRetriever(repository)

    def index_documents(self) -> tuple[int, int, str]:
        documents, chunks = self.repository.reindex_documents()
        try:
            indexed = self.vector_store.upsert_chunks(self.repository.list_active_chunks())
            return documents, indexed, "qdrant"
        except Exception:
            return documents, chunks, "local"

    def search(self, query: str, top_k: int = 3) -> list[RetrievalResult]:
        try:
            results = self.vector_store.search(query, top_k)
        except Exception:
            return self.fallback.search(query, top_k)

        hydrated: list[RetrievalResult] = []
        for chunk, score in results:
            local_document = self.repository.get_document(chunk.document_id)
            if local_document:
                chunk.metadata.setdefault("title", local_document.title)
                chunk.metadata.setdefault("version", local_document.version)
            hydrated.append(RetrievalResult(chunk=chunk, score=score))
        return hydrated
