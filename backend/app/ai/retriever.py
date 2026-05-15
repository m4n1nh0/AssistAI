import re
from dataclasses import dataclass

from app.ai.knowledge_base import SEED_DOCUMENTS
from app.domain.models import KnowledgeDocument, Source


@dataclass
class RetrievedContext:
    document: KnowledgeDocument
    score: float


def _tokens(text: str) -> set[str]:
    return {token for token in re.findall(r"[a-zA-ZÀ-ÿ0-9-]+", text.lower()) if len(token) > 2}


class SimpleRetriever:
    def __init__(self) -> None:
        self.documents: list[KnowledgeDocument] = list(SEED_DOCUMENTS)

    def add_document(self, document: KnowledgeDocument) -> None:
        self.documents.append(document)

    def search(self, query: str, limit: int = 3) -> list[RetrievedContext]:
        query_tokens = _tokens(query)
        results: list[RetrievedContext] = []

        for document in self.documents:
            if document.status != "active":
                continue
            document_tokens = _tokens(" ".join([document.title, document.category, document.content, *document.tags]))
            if not query_tokens or not document_tokens:
                score = 0.0
            else:
                score = len(query_tokens & document_tokens) / len(query_tokens)
            results.append(RetrievedContext(document=document, score=round(score, 2)))

        return sorted(results, key=lambda item: item.score, reverse=True)[:limit]

    @staticmethod
    def to_sources(contexts: list[RetrievedContext]) -> list[Source]:
        return [
            Source(
                document_id=context.document.id,
                title=context.document.title,
                version=context.document.version,
                score=context.score,
            )
            for context in contexts
        ]


retriever = SimpleRetriever()
