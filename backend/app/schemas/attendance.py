from datetime import datetime

from pydantic import BaseModel

from app.domain.enums import Channel, Intent
from app.schemas.ask import SourceResponse


class AttendanceMessageResponse(BaseModel):
    id: str
    user_message: str
    assistant_answer: str
    fallback: bool
    intent: Intent
    confidence: float
    sources: list[SourceResponse]
    created_at: datetime


class AttendanceSummaryResponse(BaseModel):
    id: str
    user_id: str
    channel: Channel
    total_messages: int
    created_at: datetime


class AttendanceListResponse(BaseModel):
    items: list[AttendanceSummaryResponse]


class AttendanceDetailResponse(BaseModel):
    id: str
    user_id: str
    channel: Channel
    messages: list[AttendanceMessageResponse]
    created_at: datetime
