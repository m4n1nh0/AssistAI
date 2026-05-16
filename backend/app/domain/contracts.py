from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import Channel, DocumentStatus, Intent


class SourceResponse(BaseModel):
    document_id: str = Field(..., description="Identificador do documento usado como fonte.")
    title: str = Field(..., description="Titulo do documento usado como fonte.")
    version: str = Field(..., description="Versao do documento usada na resposta.")
    score: float = Field(..., ge=0.0, le=1.0, description="Score de relevancia da fonte.")


class AskRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "user_id": "web-user-001",
                    "channel": "web",
                    "message": "Como abrir chamado no suporte?",
                }
            ]
        }
    )

    user_id: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Identificador externo do usuario no canal de origem.",
    )
    channel: Channel = Field(
        ...,
        description="Canal que originou a pergunta.",
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Pergunta enviada pelo usuario em linguagem natural.",
    )


class AskResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "answer": "Para abrir um chamado, acesse o portal de suporte interno...",
                    "fallback": False,
                    "intent": "procedimento",
                    "confidence": 0.87,
                    "sources": [
                        {
                            "document_id": "doc-001",
                            "title": "Procedimento de abertura de chamado",
                            "version": "1.0",
                            "score": 0.91,
                        }
                    ],
                    "attendance_id": "att-123",
                    "message_id": "msg-456",
                }
            ]
        }
    )

    answer: str = Field(..., description="Resposta final exibida ao usuario.")
    fallback: bool = Field(..., description="Indica se a resposta foi fallback controlado.")
    intent: Intent = Field(..., description="Intencao detectada pelo assistente.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confianca da resposta.")
    sources: list[SourceResponse] = Field(
        ...,
        description="Fontes usadas para fundamentar a resposta.",
    )
    attendance_id: str = Field(..., description="Identificador do atendimento.")
    message_id: str = Field(
        ...,
        description="Identificador da mensagem para historico e feedback.",
    )


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
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "user_id": "telegram-123456",
                    "message": "Como abrir chamado no suporte?",
                }
            ]
        }
    )

    user_id: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Identificador externo do usuario no Telegram.",
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Mensagem recebida do usuario no Telegram.",
    )
