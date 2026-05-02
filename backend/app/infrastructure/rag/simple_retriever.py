import re
import unicodedata
from dataclasses import dataclass

from app.domain.models import DocumentChunk
from app.infrastructure.repositories.memory import InMemoryRepository

STOPWORDS = {
    "a",
    "ao",
    "aos",
    "as",
    "como",
    "da",
    "das",
    "de",
    "do",
    "dos",
    "e",
    "em",
    "eu",
    "me",
    "na",
    "nas",
    "no",
    "nos",
    "o",
    "os",
    "para",
    "por",
    "que",
    "um",
    "uma",
}


@dataclass(slots=True)
class RetrievalResult:
    chunk: DocumentChunk
    score: float


class SimpleRetriever:
    def __init__(self, repository: InMemoryRepository) -> None:
        self.repository = repository

    def search(self, query: str, top_k: int = 3) -> list[RetrievalResult]:
        query_tokens = _tokenize(query)
        if not query_tokens:
            return []

        results: list[RetrievalResult] = []
        for chunk in self.repository.list_active_chunks():
            document = self.repository.get_document(chunk.document_id)
            document_text = " ".join(
                [
                    chunk.content,
                    document.title if document else "",
                    " ".join(document.tags) if document else "",
                ]
            )
            chunk_tokens = _tokenize(document_text)
            overlap = query_tokens.intersection(chunk_tokens)
            if not overlap:
                continue

            coverage = len(overlap) / len(query_tokens)
            density = len(overlap) / max(len(chunk_tokens), 1)
            score = min(1.0, coverage * 0.85 + density * 0.15)
            results.append(RetrievalResult(chunk=chunk, score=round(score, 4)))

        return sorted(results, key=lambda item: item.score, reverse=True)[:top_k]


def _tokenize(text: str) -> set[str]:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    tokens = re.findall(r"[a-z0-9]+", ascii_text)
    return {token for token in tokens if token not in STOPWORDS and len(token) > 2}

