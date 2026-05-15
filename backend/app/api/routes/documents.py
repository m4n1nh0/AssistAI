from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_document_service
from app.application.services.document_service import DocumentService
from app.domain.contracts import (
    DocumentCreateRequest,
    DocumentResponse,
    ReindexResponse,
)

router = APIRouter()
DocumentServiceDep = Annotated[DocumentService, Depends(get_document_service)]


@router.get("/documents", response_model=list[DocumentResponse])
async def list_documents(
    service: DocumentServiceDep,
) -> list[DocumentResponse]:
    return service.list()


@router.post("/documents", response_model=DocumentResponse, status_code=201)
async def create_document(
    payload: DocumentCreateRequest,
    service: DocumentServiceDep,
) -> DocumentResponse:
    return service.create(payload)


@router.post("/documents/reindex", response_model=ReindexResponse)
async def reindex_documents(
    service: DocumentServiceDep,
) -> ReindexResponse:
    return service.reindex()
