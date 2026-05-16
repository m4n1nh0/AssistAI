from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from app.domain.enums import Channel, DocumentStatus, Intent


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:12]}"


def utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass(slots=True)
class Source:
    document_id: str
    title: str
    version: str
    score: float


@dataclass(slots=True)
class User:
    id: str
    external_id: str
    channel: Channel
    created_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class Attendance:
    id: str
    user_id: str
    channel: Channel
    started_at: datetime = field(default_factory=utc_now)
    escalated: bool = False


@dataclass(slots=True)
class MessageRecord:
    id: str
    attendance_id: str
    user_message: str
    assistant_answer: str
    fallback: bool
    intent: Intent
    confidence: float
    sources: list[Source]
    created_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class Feedback:
    id: str
    message_id: str
    useful: bool
    comment: str | None = None
    created_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class KnowledgeDocument:
    id: str
    title: str
    category: str
    channel: str
    version: str
    status: DocumentStatus
    updated_at: datetime
    source: str
    owner: str
    sensitivity: str
    content: str
    tags: list[str]


@dataclass(slots=True)
class DocumentChunk:
    id: str
    document_id: str
    content: str
    metadata: dict[str, str]
    embedding: list[float] = field(default_factory=list)
    indexed_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class AiLog:
    id: str
    message_id: str
    intent: Intent
    relevance_score: float
    fallback: bool
    source_document_ids: list[str]
    elapsed_ms: int
    created_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class Handoff:
    id: str
    attendance_id: str
    reason: str
    created_at: datetime = field(default_factory=utc_now)


@dataclass(slots=True)
class ToolCall:
    id: str
    message_id: str
    tool_name: str
    input_payload: dict[str, str]
    output_payload: dict[str, str]
    success: bool
    created_at: datetime = field(default_factory=utc_now)
