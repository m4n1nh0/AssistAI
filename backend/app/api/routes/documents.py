from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.application.services.document_service import DocumentService, get_document_service
from app.infrastructure.qdrant_client import QdrantUnavailableError
from app.schemas.document import (
    DocumentChunkResponse,
    DocumentCreateRequest,
    DocumentListResponse,
    DocumentResponse,
    ReindexResponse,
)

router = APIRouter()


@router.get("/documents", response_model=DocumentListResponse)
def list_documents(
    service: DocumentService = Depends(get_document_service),
) -> DocumentListResponse:
    return service.list()


@router.post("/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(
    payload: DocumentCreateRequest,
    service: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    return service.create(payload)


@router.post("/documents/reindex", response_model=ReindexResponse)
def reindex_documents(
    service: DocumentService = Depends(get_document_service),
) -> ReindexResponse:
    try:
        return service.reindex()
    except QdrantUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))


@router.post("/documents/{document_id}/reindex", response_model=ReindexResponse)
def reindex_document(
    document_id: str,
    service: DocumentService = Depends(get_document_service),
) -> ReindexResponse:
    try:
        response = service.reindex_document(document_id)
    except QdrantUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))

    if response.indexed_documents == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento não encontrado")
    return response


@router.get("/documents/chunks", response_model=list[DocumentChunkResponse])
def list_document_chunks(
    service: DocumentService = Depends(get_document_service),
    max_words: int = Query(120, gt=0),
    overlap: int = Query(20, ge=0, lt=120),
) -> list[DocumentChunkResponse]:
    return service.get_chunks(max_words=max_words, overlap=overlap)


@router.get("/documents/{document_id}/chunks", response_model=list[DocumentChunkResponse])
def get_document_chunks(
    document_id: str,
    service: DocumentService = Depends(get_document_service),
    max_words: int = Query(120, gt=0),
    overlap: int = Query(20, ge=0, lt=120),
) -> list[DocumentChunkResponse]:
    chunks = service.get_chunks(document_id=document_id, max_words=max_words, overlap=overlap)
    if not chunks:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento não encontrado")
    return chunks
