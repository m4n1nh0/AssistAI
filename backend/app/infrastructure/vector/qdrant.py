from dataclasses import dataclass
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from app.domain.models import DocumentChunk
from app.infrastructure.rag.simple_retriever import RetrievalResult

@dataclass(frozen=True, slots=True)
class QdrantConfig:
    url: str
    collection: str


class QdrantVectorStore:
    def __init__(self, config: QdrantConfig) -> None:
        self.config = config
        self.client = QdrantClient(url=config.url)
        
        if not self.client.collection_exists(config.collection):
            pass

    def upsert_chunks(self, chunks: list[DocumentChunk]) -> int:
        if not chunks:
            return 0
        
        documents = [chunk.content for chunk in chunks]
        metadata = [{"chunk_id": chunk.id, "document_id": chunk.document_id, **chunk.metadata} for chunk in chunks]
        ids = [chunk.id for chunk in chunks]
        
        self.client.add(
            collection_name=self.config.collection,
            documents=documents,
            metadata=metadata,
            ids=ids
        )
        return len(chunks)

    def search(self, query: str, top_k: int = 3) -> list[RetrievalResult]:
        results = self.client.query(
            collection_name=self.config.collection,
            query_text=query,
            limit=top_k
        )
        
        return [
            RetrievalResult(
                chunk=DocumentChunk(
                    id=res.id,
                    document_id=res.metadata.get("document_id", ""),
                    content=res.document,
                    metadata=res.metadata,
                ),
                score=res.score
            )
            for res in results
        ]
