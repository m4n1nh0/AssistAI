from dataclasses import asdict
from uuid import uuid4

from app.core.config import settings
from app.domain.entities import KnowledgeDocument
from app.infrastructure.qdrant_client import QdrantGateway
from app.infrastructure.repositories.memory import store
from app.rag.chunker import chunk_text
from app.rag.loader import load_markdown_documents
from app.schemas.document import DocumentCreateRequest, DocumentListResponse, DocumentResponse, ReindexResponse


class DocumentService:
    def __init__(self) -> None:
        self._qdrant = None

    def _get_qdrant(self) -> QdrantGateway:
        if self._qdrant is None:
            self._qdrant = QdrantGateway()
        return self._qdrant

    def list(self) -> DocumentListResponse:
        self._ensure_seed_documents()
        return DocumentListResponse(items=[self._to_response(document) for document in store.documents.values()])

    def create(self, payload: DocumentCreateRequest) -> DocumentResponse:
        document = KnowledgeDocument(id=f"doc-{uuid4()}", **payload.model_dump())
        store.documents[document.id] = document
        return self._to_response(document)

    def reindex(self) -> ReindexResponse:
        self._ensure_seed_documents()
        documents = list(store.documents.values())
        indexed_chunks = self._get_qdrant().index_documents(documents)
        return ReindexResponse(indexed_documents=len(documents), indexed_chunks=indexed_chunks)

    def reindex_document(self, document_id: str) -> ReindexResponse:
        self._ensure_seed_documents()
        document = store.documents.get(document_id)
        if not document:
            return ReindexResponse(indexed_documents=0, indexed_chunks=0)

        indexed_chunks = self._get_qdrant().index_documents([document])
        return ReindexResponse(indexed_documents=1, indexed_chunks=indexed_chunks)

    def get_chunks(self, document_id: str | None = None, max_words: int = 120, overlap: int = 20) -> list[dict]:
        self._ensure_seed_documents()

        if document_id:
            document = store.documents.get(document_id)
            if not document:
                return []
            documents = [document]
        else:
            documents = list(store.documents.values())

        chunks: list[dict] = []
        for document in documents:
            for index, chunk in enumerate(chunk_text(document.content, max_words=max_words, overlap=overlap), start=1):
                start_word = (index - 1) * (max_words - overlap) + 1
                end_word = start_word + len(chunk.split()) - 1
                chunks.append(
                    {
                        "document_id": document.id,
                        "chunk_id": f"{document.id}-{index}",
                        "title": document.title,
                        "category": document.category,
                        "version": document.version,
                        "content": chunk,
                        "source": document.source,
                        "start_word": start_word,
                        "end_word": end_word,
                    }
                )
        return chunks

    def _ensure_seed_documents(self) -> None:
        if store.documents:
            return
        for document in load_markdown_documents(settings.knowledge_base_path):
            store.documents[document.id] = document

    @staticmethod
    def _to_response(document: KnowledgeDocument) -> DocumentResponse:
        return DocumentResponse(
            id=document.id,
            title=document.title,
            category=document.category,
            content=document.content,
            channel=document.channel,
            version=document.version,
            status=document.status,
            source=document.source,
            owner=document.owner,
            sensitivity=document.sensitivity,
            tags=document.tags,
            updated_at=document.updated_at,
        )


def get_document_service() -> DocumentService:
    return DocumentService()
