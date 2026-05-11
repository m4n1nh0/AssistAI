from dataclasses import dataclass
try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models as rest
except ImportError:
    QdrantClient = None

from app.domain.models import DocumentChunk


@dataclass(frozen=True, slots=True)
class QdrantConfig:
    url: str
    collection: str


class QdrantVectorStore:
    def __init__(self, config: QdrantConfig) -> None:
        self.config = config
        self.client = QdrantClient(url=config.url) if QdrantClient else None

    def upsert_chunks(self, chunks: list[DocumentChunk]) -> int:
        if not self.client:
            raise RuntimeError("QdrantClient not installed or not configured.")
        # Lógica real de indexação viria aqui
        return len(chunks)

    def search(self, query: str, top_k: int = 3) -> list[DocumentChunk]:
        if not self.client:
            raise RuntimeError("QdrantClient not installed or not configured.")
        # Lógica real de busca viria aqui
        return []

