import re
from dataclasses import dataclass

from app.domain.entities import KnowledgeDocument
from app.domain.enums import DocumentStatus
from app.rag.chunker import chunk_text


@dataclass(slots=True)
class RetrievedContext:
    document: KnowledgeDocument
    score: float
    excerpt: str
    chunk_index: int


class KeywordRetriever:
    def search(self, question: str, documents: list[KnowledgeDocument], limit: int = 3) -> list[RetrievedContext]:
        question_terms = set(self._terms(question))
        if not question_terms:
            return []

        results: list[RetrievedContext] = []
        for document in documents:
            if document.status != DocumentStatus.ACTIVE:
                continue

            chunks = chunk_text(document.content, max_words=120, overlap=20)
            for index, chunk in enumerate(chunks, start=1):
                content_terms = set(self._terms(chunk + " " + " ".join(document.tags)))
                overlap = question_terms.intersection(content_terms)
                if not overlap:
                    continue

                score = len(overlap) / max(len(question_terms), 1)
                results.append(
                    RetrievedContext(
                        document=document,
                        score=round(score, 2),
                        excerpt=chunk.strip(),
                        chunk_index=index,
                    )
                )

        return sorted(results, key=lambda item: item.score, reverse=True)[:limit]

    @staticmethod
    def _terms(text: str) -> list[str]:
        stopwords = {"como", "para", "qual", "quando", "onde", "fazer", "meu", "minha", "um", "uma", "de", "do", "da"}
        return [
            term
            for term in re.findall(r"[a-zA-ZÀ-ÿ0-9]+", text.lower())
            if len(term) > 2 and term not in stopwords
        ]
