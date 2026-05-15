from pydantic import BaseModel, Field

from app.domain.models import Channel


class AskRequest(BaseModel):
    user_id: str = Field(default="web-user-001", min_length=1)
    channel: Channel = Channel.WEB
    message: str = Field(min_length=1, max_length=2000)


class SourceResponse(BaseModel):
    document_id: str
    title: str
    version: str
    score: float


class AskResponse(BaseModel):
    answer: str
    fallback: bool
    intent: str
    confidence: float
    sources: list[SourceResponse]
    attendance_id: str
    message_id: str
    needs_human: bool = False
    suggested_actions: list[str] = []


class FeedbackRequest(BaseModel):
    message_id: str
    useful: bool
    comment: str | None = Field(default=None, max_length=1000)


class FeedbackResponse(BaseModel):
    status: str


class DocumentCreateRequest(BaseModel):
    title: str
    category: str
    content: str
    version: str = "1.0"
    status: str = "active"
    tags: list[str] = []


class DocumentResponse(BaseModel):
    id: str
    title: str
    category: str
    version: str
    status: str
    tags: list[str]


class TelegramWebhookRequest(BaseModel):
    message: dict
