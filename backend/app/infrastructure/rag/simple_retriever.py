from dataclasses import dataclass

from app.domain.models import DocumentChunk
from app.infrastructure.repositories.memory import InMemoryRepository
from app.infrastructure.vector.embeddings import (
    HashEmbeddingGenerator,
    cosine_similarity,
    tokenize,
)
from app.infrastructure.vector.qdrant import QdrantUnavailable, QdrantVectorStore


@dataclass(slots=True)
class RetrievalResult:
    chunk: DocumentChunk
    score: float


class SimpleRetriever:
    def __init__(
        self,
        repository: InMemoryRepository,
        vector_store: QdrantVectorStore | None = None,
        embedding_generator: HashEmbeddingGenerator | None = None,
    ) -> None:
        self.repository = repository
        self.vector_store = vector_store
        self.embedding_generator = embedding_generator or HashEmbeddingGenerator()

    def search(self, query: str, top_k: int = 3) -> list[RetrievalResult]:
        query_tokens = _tokenize(query)
        if not query_tokens:
            return []

        qdrant_results = self._search_qdrant(query, query_tokens, top_k)
        if qdrant_results:
            return qdrant_results

        query_embedding = self.embedding_generator.embed(query)
        results: list[RetrievalResult] = []
        for chunk in self.repository.list_active_chunks():
            document_text = self._document_text(chunk)
            chunk_tokens = _tokenize(document_text)
            overlap = query_tokens.intersection(chunk_tokens)
            if not overlap:
                continue

            coverage = len(overlap) / len(query_tokens)
            density = len(overlap) / max(len(chunk_tokens), 1)
            lexical_score = min(1.0, coverage * 0.85 + density * 0.15)
            vector = chunk.embedding or self.embedding_generator.embed(document_text)
            vector_score = cosine_similarity(query_embedding, vector)
            score = min(1.0, lexical_score * 0.45 + vector_score * 0.55)
            results.append(RetrievalResult(chunk=chunk, score=round(score, 4)))

        return sorted(results, key=lambda item: item.score, reverse=True)[:top_k]

    def _search_qdrant(
        self,
        query: str,
        query_tokens: set[str],
        top_k: int,
    ) -> list[RetrievalResult]:
        if not self.vector_store or not self.vector_store.indexed:
            return []

        try:
            vector_results = self.vector_store.search(query, top_k)
        except QdrantUnavailable:
            return []

        results: list[RetrievalResult] = []
        for result in vector_results:
            chunk = self.repository.get_chunk(result.chunk_id)
            if not chunk:
                continue
            overlap = query_tokens.intersection(_tokenize(self._document_text(chunk)))
            if not overlap:
                continue
            results.append(RetrievalResult(chunk=chunk, score=result.score))
        return results

    def _document_text(self, chunk: DocumentChunk) -> str:
        document = self.repository.get_document(chunk.document_id)
        return " ".join(
            [
                chunk.content,
                document.title if document else "",
                " ".join(document.tags) if document else "",
            ]
        )


def _tokenize(text: str) -> set[str]:
    return tokenize(text)
