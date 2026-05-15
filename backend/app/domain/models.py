from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum


class Channel(StrEnum):
    WEB = "web"
    TELEGRAM = "telegram"


class Intent(StrEnum):
    GREETING = "saudacao"
    PROCEDURE = "procedimento"
    TICKET_STATUS = "consulta_chamado"
    HUMAN = "solicitacao_humano"
    OUT_OF_SCOPE = "fora_de_escopo"


@dataclass
class Source:
    document_id: str
    title: str
    version: str
    score: float


@dataclass
class MessageRecord:
    id: str
    role: str
    content: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    sources: list[Source] = field(default_factory=list)
    fallback: bool = False
    intent: Intent | None = None


@dataclass
class Attendance:
    id: str
    user_id: str
    channel: Channel
    messages: list[MessageRecord] = field(default_factory=list)
    needs_human: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class KnowledgeDocument:
    id: str
    title: str
    category: str
    content: str
    version: str = "1.0"
    status: str = "active"
    channel: str = "both"
    sensitivity: str = "internal"
    tags: list[str] = field(default_factory=list)
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
