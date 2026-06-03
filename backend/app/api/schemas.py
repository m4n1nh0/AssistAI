from pydantic import BaseModel, Field

from app.domain.enums import Channel


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
