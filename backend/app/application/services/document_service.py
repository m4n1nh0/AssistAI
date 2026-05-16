from __future__ import annotations

import logging

from app.domain.contracts import (
    DocumentCreateRequest,
    DocumentResponse,
    ReindexResponse,
)
from app.domain.protocols import Repository
from app.infrastructure.vector.qdrant import QdrantVectorStore

logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(
        self,
        repository: Repository,
        vector_store: QdrantVectorStore | None = None,
    ) -> None:
        self.repository = repository
        self.vector_store = vector_store

    def create(self, payload: DocumentCreateRequest) -> DocumentResponse:
        document = self.repository.create_document(payload)

        if self.vector_store:
            chunks = [
                chunk
                for chunk in self.repository.list_active_chunks()
                if chunk.document_id == document.id
            ]
            if chunks:
                indexed = self.vector_store.upsert_chunks(chunks)
                logger.info(
                    "Documento %s indexado no Qdrant: %d chunks",
                    document.id,
                    indexed,
                )

        return _to_response(document)

    def list(self) -> list[DocumentResponse]:
        return [_to_response(doc) for doc in self.repository.list_documents()]

    def reindex(self) -> ReindexResponse:
        doc_count, chunk_count = self.repository.reindex_documents()

        if self.vector_store:
            chunks = self.repository.list_active_chunks()
            self.vector_store.upsert_chunks(chunks)
            logger.info(
                "Reindexacao Qdrant completa: %d chunks",
                len(chunks),
            )

        return ReindexResponse(
            indexed_documents=doc_count,
            indexed_chunks=chunk_count,
        )


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
