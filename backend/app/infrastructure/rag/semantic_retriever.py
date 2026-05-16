from __future__ import annotations

import logging

from app.domain.models import RetrievalResult
from app.domain.protocols import Repository, Retriever
from app.infrastructure.vector.qdrant import QdrantVectorStore

logger = logging.getLogger(__name__)


class SemanticRetriever(Retriever):
    def __init__(
        self,
        vector_store: QdrantVectorStore,
        repository: Repository,
        min_score: float = 0.15,
    ) -> None:
        self.vector_store = vector_store
        self.repository = repository
        self.min_score = min_score

    def search(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        qdrant_results = self.vector_store.search(query, top_k=top_k)

        results: list[RetrievalResult] = []
        for qr in qdrant_results:
            if qr.score < self.min_score:
                continue

            doc = self.repository.get_document(qr.chunk.document_id)
            if doc and doc.status.value != "active":
                continue
            if not doc:
                continue

            results.append(
                RetrievalResult(chunk=qr.chunk, score=qr.score)
            )

        results.sort(key=lambda item: item.score, reverse=True)
        logger.info(
            "Busca semantica: %d resultados (top_k=%d, min_score=%.2f)",
            len(results),
            top_k,
            self.min_score,
        )
        return results
