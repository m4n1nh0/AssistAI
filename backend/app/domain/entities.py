from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.domain.enums import Channel, DocumentStatus, Intent


@dataclass(slots=True)
class Source:
    document_id: str
    title: str
    version: str
    score: float


@dataclass(slots=True)
class Message:
    id: str
    attendance_id: str
    user_message: str
    assistant_answer: str
    fallback: bool
    intent: Intent
    confidence: float
    sources: list[Source] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(slots=True)
class Attendance:
    id: str
    user_id: str
    channel: Channel
    messages: list[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(slots=True)
class KnowledgeDocument:
    id: str
    title: str
    category: str
    channel: str
    version: str
    status: DocumentStatus
    source: str
    owner: str
    sensitivity: str
    content: str
    tags: list[str] = field(default_factory=list)
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
