from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from app.domain.enums import Channel, DocumentStatus, Intent


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8]}"


@dataclass(slots=True)
class User:
    id: str
    external_id: str
    channel: Channel
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(slots=True)
class Attendance:
    id: str
    user_id: str
    channel: Channel
    escalated: bool = False
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def needs_human(self) -> bool:
        return self.escalated


@dataclass(slots=True)
class Source:
    document_id: str
    title: str
    version: str
    score: float


@dataclass(slots=True)
class MessageRecord:
    id: str
    attendance_id: str = ""
    user_message: str = ""
    assistant_answer: str = ""
    fallback: bool = False
    intent: Intent | None = None
    confidence: float = 0.0
    sources: list[Source] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    role: str = ""
    content: str = ""


@dataclass(slots=True)
class KnowledgeDocument:
    id: str
    title: str
    category: str
    content: str
    version: str = "1.0"
    status: DocumentStatus | str = DocumentStatus.ACTIVE
    channel: str = "both"
    sensitivity: str = "interno"
    tags: list[str] = field(default_factory=list)
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    source: str = "manual"
    owner: str = "suporte"


@dataclass(slots=True)
class DocumentChunk:
    id: str
    document_id: str
    content: str
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class Feedback:
    id: str
    message_id: str
    useful: bool
    comment: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(slots=True)
class Handoff:
    id: str
    attendance_id: str
    reason: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(slots=True)
class AiLog:
    id: str
    message_id: str
    intent: Intent
    relevance_score: float
    fallback: bool
    source_document_ids: list[str]
    elapsed_ms: int
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(slots=True)
class ToolCall:
    id: str
    name: str
    input_payload: dict
    output_payload: dict
    success: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
