from app.domain.contracts import (
    DocumentCreateRequest,
    DocumentResponse,
    ReindexResponse,
)
from app.infrastructure.repositories.memory import InMemoryRepository
from app.infrastructure.vector.qdrant import HybridRetriever


class DocumentService:
    def __init__(self, repository: InMemoryRepository, retriever: HybridRetriever | None = None) -> None:
        self.repository = repository
        self.retriever = retriever

    def create(self, payload: DocumentCreateRequest) -> DocumentResponse:
        document = self.repository.create_document(payload)
        if self.retriever:
            self.retriever.index_documents()
        return _to_response(document)

    def list(self) -> list[DocumentResponse]:
        return [_to_response(document) for document in self.repository.list_documents()]

    def reindex(self) -> ReindexResponse:
        if self.retriever:
            documents, chunks, _mode = self.retriever.index_documents()
        else:
            documents, chunks = self.repository.reindex_documents()
        return ReindexResponse(indexed_documents=documents, indexed_chunks=chunks)


def _to_response(document) -> DocumentResponse:
    return DocumentResponse(
        document_id=document.id,
        title=document.title,
        category=document.category,
        channel=document.channel,
        version=document.version,
        status=document.status,
        updated_at=document.updated_at,
        source=document.source,
        owner=document.owner,
        sensitivity=document.sensitivity,
        tags=document.tags,
    )

