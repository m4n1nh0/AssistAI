from app.domain.contracts import (
    DocumentCreateRequest,
    DocumentResponse,
    ReindexResponse,
)
from app.infrastructure.repositories.memory import InMemoryRepository


class DocumentService:
    def __init__(self, repository: InMemoryRepository) -> None:
        self.repository = repository

    def create(self, payload: DocumentCreateRequest) -> DocumentResponse:
        return _to_response(self.repository.create_document(payload))

    def list(self) -> list[DocumentResponse]:
        return [_to_response(document) for document in self.repository.list_documents()]

    def reindex(self) -> ReindexResponse:
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

