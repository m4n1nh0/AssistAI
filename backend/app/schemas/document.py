from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.enums import DocumentStatus


class DocumentCreateRequest(BaseModel):
    title: str = Field(min_length=1)
    category: str = Field(min_length=1)
    content: str = Field(min_length=1)
    channel: str = "both"
    version: str = "1.0"
    status: DocumentStatus = DocumentStatus.ACTIVE
    source: str = "manual"
    owner: str = "suporte"
    sensitivity: str = "interno"
    tags: list[str] = Field(default_factory=list)


class DocumentResponse(DocumentCreateRequest):
    id: str
    updated_at: datetime


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]


class ReindexResponse(BaseModel):
    indexed_documents: int
    indexed_chunks: int


class DocumentChunkResponse(BaseModel):
    document_id: str
    chunk_id: str
    title: str | None = None
    category: str | None = None
    version: str | None = None
    content: str
    source: str | None = None
    start_word: int
    end_word: int
