"""
Contrato oficial de Pergunta e Resposta do Assistente Inteligente.

Este módulo define os modelos Pydantic que padronizam a comunicação
entre Web, Telegram, API e Motor de IA, garantindo validação automática
e consistência entre todas as equipes.

Versão do Contrato: 1.0
Data: 2024-01-01
"""

from datetime import datetime
from typing import Optional
import uuid

from pydantic import BaseModel, Field, validator

from app.domain.enums import Channel, DocumentStatus, Intent

# ============================================================================
# CONSTANTES
# ============================================================================

CONTRACT_VERSION = "1.0"


# ============================================================================
# ENTRADA (REQUEST)
# ============================================================================


class RequestMetadata(BaseModel):
    """Metadados obrigatórios e opcionais da requisição."""

    timestamp: datetime = Field(
        ..., description="Timestamp da requisição em ISO 8601"
    )
    user_agent: Optional[str] = Field(
        default=None, max_length=255, description="User agent do cliente"
    )
    ip_address: Optional[str] = Field(
        default=None, max_length=45, description="Endereço IP do cliente"
    )
    message_id: Optional[str] = Field(
        default=None, max_length=255, description="ID da mensagem (Telegram)"
    )


class AskRequest(BaseModel):
    """
    Requisição padrão de pergunta do usuário.
    
    Contrato versão 1.0 - Usada por Web, Telegram e API direta.
    """

    version: str = Field(
        default=CONTRACT_VERSION, description="Versão do contrato (deve ser '1.0')"
    )
    question: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="A pergunta do usuário",
    )
    user_id: Optional[str] = Field(
        default=None, max_length=255, description="ID único do usuário"
    )
    channel: Channel = Field(
        ..., description="Canal de origem: 'web' ou 'telegram'"
    )
    session_id: Optional[str] = Field(
        default=None, max_length=255, description="ID da sessão de conversa"
    )
    conversation_id: Optional[str] = Field(
        default=None, max_length=255, description="ID da conversa para multi-turno"
    )
    request_id: Optional[str] = Field(
        default_factory=lambda: str(uuid.uuid4()),
        max_length=255,
        description="ID único do request para rastreamento"
    )
    metadata: RequestMetadata = Field(
        ..., description="Metadados obrigatórios e opcionais da requisição"
    )

    @validator("question")
    def question_stripped(cls, v):
        """Garante que a pergunta é trimada."""
        return v.strip() if v else v

    @validator("question")
    def question_not_empty_after_strip(cls, v):
        """Rejeita perguntas vazias após trim."""
        if not v or not v.strip():
            raise ValueError("question não pode ser vazio após trim")
        return v

    @validator("version")
    def validate_version(cls, v):
        """Valida versão do contrato."""
        if v != CONTRACT_VERSION:
            raise ValueError(f"Versão não suportada: {v}. Esperado: {CONTRACT_VERSION}")
        return v


# ============================================================================
# SAÍDA (RESPONSE)
# ============================================================================


class SourceResponse(BaseModel):
    """Fonte de informação utilizada na resposta."""

    document_id: str = Field(..., description="ID do documento fonte")
    title: str = Field(..., description="Título do documento")
    content: str = Field(..., description="Trecho relevante do documento")
    score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Score de relevância (0.0 a 1.0)",
    )
    version: str = Field(..., description="Versão do documento")


class ResponseMetadata(BaseModel):
    """Metadados da resposta."""

    processing_time_ms: int = Field(
        ..., ge=0, description="Tempo de processamento em milissegundos"
    )
    model_used: str = Field(
        ..., description="Modelo utilizado (ex: 'gpt-4', 'fallback')"
    )
    timestamp: datetime = Field(..., description="Timestamp da resposta")


class AskResponse(BaseModel):
    """
    Resposta padrão da pergunta do usuário.
    
    Contrato versão 1.0 - Retornada para Web, Telegram e API direta.
    """

    version: str = Field(
        default=CONTRACT_VERSION, description="Versão do contrato"
    )
    answer: str = Field(
        ..., min_length=1, max_length=4000, description="Resposta gerada pelo assistente"
    )
    sources: list[SourceResponse] = Field(
        default_factory=list,
        max_items=5,
        description="Lista de fontes utilizadas (máximo 5)",
    )
    score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Score geral da resposta (0.0 a 1.0)",
    )
    fallback: bool = Field(
        ..., description="Indica se foi usado fallback"
    )
    fallback_reason: Optional[str] = Field(
        default=None,
        description="Razão do fallback (ex: 'low_score', 'no_sources', 'error')",
    )
    conversation_id: Optional[str] = Field(
        default=None, description="ID da conversa para continuidade"
    )
    request_id: Optional[str] = Field(
        default=None, description="ID do request original (para rastreamento)"
    )
    attendance_id: Optional[str] = Field(
        default=None, description="ID do atendimento registrado"
    )
    message_id: Optional[str] = Field(
        default=None, description="ID da mensagem registrada para feedback e histórico"
    )
    metadata: ResponseMetadata = Field(
        ..., description="Metadados da resposta"
    )

    @validator("version")
    def validate_version(cls, v):
        """Valida versão do contrato."""
        if v != CONTRACT_VERSION:
            raise ValueError(f"Versão não suportada: {v}. Esperado: {CONTRACT_VERSION}")
        return v


class ErrorDetail(BaseModel):
    """Detalhes de um erro."""

    field: Optional[str] = Field(default=None, description="Campo que gerou o erro")
    message: Optional[str] = Field(default=None, description="Mensagem de erro")


class ErrorResponse(BaseModel):
    """Resposta de erro padronizada."""

    version: str = Field(default=CONTRACT_VERSION, description="Versão do contrato")
    error: dict = Field(
        ...,
        description="Objeto de erro com 'code', 'message' e 'details' opcionais",
    )

    class Config:
        """Config para permitir estrutura flexível de erro."""

        extra = "allow"


# ============================================================================
# FEEDBACK
# ============================================================================


class FeedbackRequest(BaseModel):
    """Requisição de feedback sobre uma resposta."""

    message_id: str = Field(..., description="ID da mensagem para avaliação")
    useful: bool = Field(..., description="Indica se a resposta foi útil")
    comment: Optional[str] = Field(
        default=None, max_length=1000, description="Comentário opcional do usuário"
    )


class FeedbackResponse(BaseModel):
    """Resposta confirmando recebimento de feedback."""

    feedback_id: str = Field(..., description="ID do feedback registrado")
    message_id: str = Field(..., description="ID da mensagem avaliada")
    useful: bool = Field(..., description="Valor de utilidade registrado")
    created_at: datetime = Field(..., description="Data/hora de criação")


class TelegramWebhookRequest(BaseModel):
    """Requisição simplificada de webhook Telegram para o assistente."""

    user_id: str = Field(
        ..., min_length=1, max_length=255, description="ID do usuário no Telegram"
    )
    message: str = Field(
        ..., min_length=1, max_length=2000, description="Texto da mensagem recebida"
    )
    message_id: Optional[str] = Field(
        default=None,
        max_length=255,
        description="ID da mensagem do Telegram",
    )


# ============================================================================
# HISTÓRICO DE MENSAGENS
# ============================================================================


class MessageResponse(BaseModel):
    """Registro de uma mensagem no histórico de conversa."""

    message_id: str = Field(..., description="ID único da mensagem")
    user_message: str = Field(..., description="Pergunta do usuário")
    assistant_answer: str = Field(..., description="Resposta do assistente")
    fallback: bool = Field(..., description="Se usou fallback")
    intent: Intent = Field(..., description="Intenção identificada")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confiança da identificação")
    sources: list[SourceResponse] = Field(..., description="Fontes utilizadas")
    created_at: datetime = Field(..., description="Data/hora de criação")


# ============================================================================
# ATENDIMENTO (ATTENDANCE)
# ============================================================================


class AttendanceListItem(BaseModel):
    """Item da lista de atendimentos."""

    attendance_id: str = Field(..., description="ID único do atendimento")
    user_id: str = Field(..., description="ID do usuário")
    channel: Channel = Field(..., description="Canal de origem")
    escalated: bool = Field(..., description="Indica se foi escalonado")
    started_at: datetime = Field(..., description="Data/hora de início")
    message_count: int = Field(..., ge=0, description="Quantidade de mensagens")


class AttendanceDetailResponse(BaseModel):
    """Detalhes completos de um atendimento com histórico."""

    attendance_id: str = Field(..., description="ID único do atendimento")
    user_id: str = Field(..., description="ID do usuário")
    channel: Channel = Field(..., description="Canal de origem")
    escalated: bool = Field(..., description="Indica se foi escalonado")
    started_at: datetime = Field(..., description="Data/hora de início")
    messages: list[MessageResponse] = Field(..., description="Lista de mensagens da conversa")


# ============================================================================
# DOCUMENTOS
# ============================================================================


class DocumentSummary(BaseModel):
    """Sumário de um documento na base de conhecimento."""

    document_id: str = Field(..., description="ID único do documento")
    title: str = Field(..., description="Título do documento")
    version: str = Field(..., description="Versão atual do documento")
    status: DocumentStatus = Field(..., description="Status (ativo/inativo)")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")


class DocumentCreateRequest(BaseModel):
    """Requisição para criar novo documento."""

    title: str = Field(..., min_length=1, max_length=255, description="Título do documento")
    category: str = Field(..., min_length=1, max_length=128, description="Categoria")
    channel: str = Field(default="both", max_length=32, description="Canal (web, telegram, both)")
    version: str = Field(default="1.0", max_length=32, description="Versão do documento")
    status: DocumentStatus = Field(default=DocumentStatus.ACTIVE, description="Status inicial")
    source: str = Field(default="manual", max_length=255, description="Fonte do documento")
    owner: str = Field(default="suporte", max_length=128, description="Proprietário")
    sensitivity: str = Field(default="interno", max_length=64, description="Nível de sensibilidade")
    content: str = Field(..., min_length=1, description="Conteúdo do documento")
    tags: list[str] = Field(default_factory=list, description="Tags para categorização")


class DocumentResponse(BaseModel):
    """Resposta ao criar/listar documento."""

    document_id: str = Field(..., description="ID único do documento")
    title: str = Field(..., description="Título do documento")
    category: str = Field(..., description="Categoria")
    channel: str = Field(..., description="Canal alvo do documento")
    version: str = Field(..., description="Versão")
    status: DocumentStatus = Field(..., description="Status")
    updated_at: datetime = Field(..., description="Data de atualização")
    source: str = Field(..., description="Fonte do documento")
    owner: str = Field(..., description="Responsável pelo documento")
    sensitivity: str = Field(..., description="Nível de sensibilidade")
    tags: list[str] = Field(default_factory=list, description="Tags para categorização")


class ReindexResponse(BaseModel):
    """Resumo da reindexação manual da base de conhecimento."""

    indexed_documents: int = Field(..., ge=0, description="Total de documentos reindexados")
    indexed_chunks: int = Field(..., ge=0, description="Total de chunks gerados")


# ============================================================================
# PAGINAÇÃO
# ============================================================================


class PaginationMeta(BaseModel):
    """Metadados de paginação."""

    total: int = Field(..., ge=0, description="Total de itens")
    page: int = Field(..., ge=1, description="Página atual (1-indexed)")
    page_size: int = Field(..., ge=1, description="Itens por página")
    has_more: bool = Field(..., description="Se há mais páginas")


class PaginatedResponse(BaseModel):
    """Resposta paginada genérica."""

    items: list = Field(..., description="Itens da página")
    meta: PaginationMeta = Field(..., description="Metadados de paginação")


# ============================================================================
# MÉTRICAS
# ============================================================================


class MetricSummary(BaseModel):
    """Sumário de métricas do assistente."""

    total_attendances: int = Field(..., ge=0, description="Total de atendimentos")
    total_messages: int = Field(..., ge=0, description="Total de mensagens")
    fallback_rate: float = Field(..., ge=0.0, le=1.0, description="Taxa de fallback (0-1)")
    useful_feedback_rate: float = Field(..., ge=0.0, le=1.0, description="Taxa de feedback útil (0-1)")
    escalated_attendances: int = Field(..., ge=0, description="Atendimentos escalonados")
    top_intents: dict = Field(default_factory=dict, description="Intenções mais frequentes")
    top_documents: dict = Field(default_factory=dict, description="Documentos mais usados")
    unanswered_questions: list[str] = Field(default_factory=list, description="Perguntas sem resposta")


# ============================================================================
# ENUMS/TIPOS AUXILIARES
# ============================================================================


class FallbackReason(str):
    """Razões possíveis de ativação do fallback."""

    LOW_SCORE = "low_score"
    NO_SOURCES = "no_sources"
    ERROR = "error"
    INTENT_OUT_OF_SCOPE = "intent_out_of_scope"
    SERVICE_UNAVAILABLE = "service_unavailable"


class ErrorCode(str):
    """Códigos de erro padronizados."""

    INVALID_REQUEST = "INVALID_REQUEST"
    QUESTION_TOO_LONG = "QUESTION_TOO_LONG"
    UNSUPPORTED_CHANNEL = "UNSUPPORTED_CHANNEL"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

