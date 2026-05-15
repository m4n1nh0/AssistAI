from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.domain.enums import Channel, DocumentStatus, Intent

ASSISTANT_CONTRACT_VERSION = "assistant.ask.v1"


class RequestContext(BaseModel):
    conversation_id: str | None = Field(default=None, max_length=128)
    external_message_id: str | None = Field(default=None, max_length=128)
    locale: str = Field(default="pt-BR", min_length=2, max_length=16)
    metadata: dict[str, str] = Field(default_factory=dict)


class SourceResponse(BaseModel):
    document_id: str
    title: str
    version: str
    score: float = Field(..., ge=0, le=1)


class AskRequest(BaseModel):
    schema_version: Literal["assistant.ask.v1"] = ASSISTANT_CONTRACT_VERSION
    request_id: str | None = Field(default=None, max_length=128)
    user_id: str = Field(..., min_length=1, max_length=128)
    channel: Channel = Channel.WEB
    message: str = Field(..., min_length=1, max_length=2000)
    context: RequestContext = Field(default_factory=RequestContext)


class AskResponse(BaseModel):
    schema_version: Literal["assistant.ask.v1"] = ASSISTANT_CONTRACT_VERSION
    request_id: str | None = Field(default=None, max_length=128)
    user_id: str
    channel: Channel
    answer: str
    fallback: bool
    handoff_required: bool
    intent: Intent
    confidence: float = Field(..., ge=0, le=1)
    sources: list[SourceResponse]
    attendance_id: str
    message_id: str
    generated_at: datetime


class FeedbackRequest(BaseModel):
    message_id: str
    useful: bool
    comment: str | None = Field(default=None, max_length=1000)


class FeedbackResponse(BaseModel):
    feedback_id: str
    message_id: str
    useful: bool
    created_at: datetime


class AttendanceListItem(BaseModel):
    attendance_id: str
    user_id: str
    channel: Channel
    escalated: bool
    started_at: datetime
    message_count: int


class MessageResponse(BaseModel):
    message_id: str
    user_message: str
    assistant_answer: str
    fallback: bool
    intent: Intent
    confidence: float
    sources: list[SourceResponse]
    created_at: datetime


class AttendanceDetailResponse(BaseModel):
    attendance_id: str
    user_id: str
    channel: Channel
    escalated: bool
    started_at: datetime
    messages: list[MessageResponse]


class DocumentCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., min_length=1, max_length=128)
    channel: str = Field(default="both", max_length=32)
    version: str = Field(default="1.0", max_length=32)
    status: DocumentStatus = DocumentStatus.ACTIVE
    source: str = Field(default="manual", max_length=255)
    owner: str = Field(default="suporte", max_length=128)
    sensitivity: str = Field(default="interno", max_length=64)
    content: str = Field(..., min_length=1)
    tags: list[str] = Field(default_factory=list)


class DocumentResponse(BaseModel):
    document_id: str
    title: str
    category: str
    channel: str
    version: str
    status: DocumentStatus
    updated_at: datetime
    source: str
    owner: str
    sensitivity: str
    tags: list[str]


class ReindexResponse(BaseModel):
    indexed_documents: int
    indexed_chunks: int


class MetricSummaryResponse(BaseModel):
    total_attendances: int
    total_messages: int
    fallback_rate: float
    useful_feedback_rate: float
    escalated_attendances: int
    top_intents: dict[str, int]
    top_documents: dict[str, int]
    unanswered_questions: list[str]


class TelegramWebhookRequest(BaseModel):
    request_id: str | None = Field(default=None, max_length=128)
    user_id: str = Field(..., min_length=1, max_length=128)
    message: str = Field(..., min_length=1, max_length=2000)
    context: RequestContext = Field(default_factory=RequestContext)
