from pydantic import BaseModel, Field

from app.domain.enums import Channel, Intent


class AskRequest(BaseModel):
    user_id: str = Field(min_length=1, examples=["web-user-001"])
    channel: Channel = Field(default=Channel.WEB)
    message: str = Field(min_length=1, max_length=2000, examples=["Como faço para abrir um chamado?"])


class SourceResponse(BaseModel):
    document_id: str
    title: str
    version: str
    score: float


class AskResponse(BaseModel):
    answer: str
    fallback: bool
    intent: Intent
    confidence: float
    sources: list[SourceResponse]
    attendance_id: str
    message_id: str
