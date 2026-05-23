from typing import Any, Literal

from pydantic import BaseModel, Field

Channel = Literal["web", "telegram", "api"]
AnswerStatus = Literal["answered", "fallback", "error"]


class AssistantUser(BaseModel):
    id: str | None = None
    name: str | None = None


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000)
    channel: Channel
    conversation_id: str | None = None
    user: AssistantUser | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SourceResponse(BaseModel):
    document_id: str
    title: str
    chunk_id: str
    version: str
    score: float


class UsageResponse(BaseModel):
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None


class AskResponse(BaseModel):
    answer: str
    status: AnswerStatus
    conversation_id: str
    message_id: str
    sources: list[SourceResponse] = Field(default_factory=list)
    usage: UsageResponse | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    status: Literal["error"] = "error"
    error: ErrorDetail
