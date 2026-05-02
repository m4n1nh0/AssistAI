from dataclasses import dataclass

from app.domain.models import DocumentChunk


@dataclass(frozen=True, slots=True)
class QdrantConfig:
    url: str
    collection: str


class QdrantVectorStore:
    def __init__(self, config: QdrantConfig) -> None:
        self.config = config

    def upsert_chunks(self, chunks: list[DocumentChunk]) -> int:
        raise NotImplementedError("Qdrant indexing will replace the simple retriever.")

    def search(self, query: str, top_k: int = 3) -> list[DocumentChunk]:
        raise NotImplementedError("Qdrant semantic search will replace keyword search.")

