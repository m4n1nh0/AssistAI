"""
Validadores e utilitários para o Contrato Oficial de Pergunta e Resposta.

Este módulo fornece funções reutilizáveis para validação, sanitização
e conformidade com o contrato em toda a aplicação.

Versão: 1.0
"""

from datetime import datetime
from typing import Optional
import re

from app.domain.contracts import (
    AskRequest,
    AskResponse,
    ErrorResponse,
    FallbackReason,
    ErrorCode,
)


# ============================================================================
# SANITIZAÇÃO DE ENTRADA
# ============================================================================


def sanitize_question(question: str) -> str:
    """
    Sanitiza uma pergunta removendo espaços extras e caracteres perigosos.
    
    Args:
        question: Pergunta a sanitizar
        
    Returns:
        Pergunta sanitizada
        
    Raises:
        ValueError: Se a pergunta estiver vazia após sanitização
    """
    # Remover espaços extras
    sanitized = question.strip()
    
    # Remover múltiplos espaços
    sanitized = re.sub(r"\s+", " ", sanitized)
    
    # Validar comprimento
    if not sanitized or len(sanitized) == 0:
        raise ValueError("Pergunta não pode ser vazia")
    
    if len(sanitized) > 1000:
        raise ValueError("Pergunta excede limite de 1000 caracteres")
    
    return sanitized


def sanitize_user_id(user_id: Optional[str]) -> Optional[str]:
    """
    Sanitiza user_id.
    
    Args:
        user_id: ID do usuário
        
    Returns:
        ID sanitizado
        
    Raises:
        ValueError: Se inválido
    """
    if not user_id:
        return None
    
    sanitized = user_id.strip()
    
    if len(sanitized) > 255:
        raise ValueError("user_id excede limite de 255 caracteres")
    
    # Permitir apenas alphanumméricos, hífens e underscores
    if not re.match(r"^[\w\-]+$", sanitized):
        raise ValueError("user_id contém caracteres inválidos")
    
    return sanitized


# ============================================================================
# VALIDAÇÃO DE CONFORMIDADE COM O CONTRATO
# ============================================================================


def validate_ask_request(request: AskRequest) -> None:
    """
    Valida que um AskRequest está em conformidade com o contrato.
    
    Args:
        request: Requisição a validar
        
    Raises:
        ValueError: Se não estiver em conformidade
    """
    # Versão
    if request.version != "1.0":
        raise ValueError(f"Versão não suportada: {request.version}")
    
    # Pergunta
    if not request.question or len(request.question) == 0:
        raise ValueError("Campo 'question' é obrigatório")
    
    if len(request.question) > 1000:
        raise ValueError("Campo 'question' excede limite de 1000 caracteres")
    
    # Canal
    if request.channel not in ["web", "telegram"]:
        raise ValueError(f"Canal não suportado: {request.channel}")
    
    # Metadata
    if not request.metadata:
        raise ValueError("Campo 'metadata' é obrigatório")
    
    if not request.metadata.timestamp:
        raise ValueError("Campo 'metadata.timestamp' é obrigatório")
    
    # Validar que timestamp é válido
    try:
        if isinstance(request.metadata.timestamp, str):
            datetime.fromisoformat(request.metadata.timestamp.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        raise ValueError("Campo 'metadata.timestamp' deve estar em formato ISO 8601")


def validate_ask_response(response: AskResponse) -> None:
    """
    Valida que uma AskResponse está em conformidade com o contrato.
    
    Args:
        response: Resposta a validar
        
    Raises:
        ValueError: Se não estiver em conformidade
    """
    # Versão
    if response.version != "1.0":
        raise ValueError(f"Versão não suportada: {response.version}")
    
    # Answer
    if not response.answer or len(response.answer) == 0:
        raise ValueError("Campo 'answer' é obrigatório")
    
    if len(response.answer) > 4000:
        raise ValueError("Campo 'answer' excede limite de 4000 caracteres")
    
    # Score
    if not isinstance(response.score, (int, float)):
        raise ValueError("Campo 'score' deve ser um número")
    
    if response.score < 0.0 or response.score > 1.0:
        raise ValueError("Campo 'score' deve estar entre 0.0 e 1.0")
    
    # Fallback
    if not isinstance(response.fallback, bool):
        raise ValueError("Campo 'fallback' deve ser booleano")
    
    # Se fallback=true, score deve ser baixo
    if response.fallback and response.score > 0.3:
        raise ValueError("Se fallback=true, score deve ser <= 0.3")
    
    # Sources
    if not isinstance(response.sources, list):
        raise ValueError("Campo 'sources' deve ser uma lista")
    
    if len(response.sources) > 5:
        raise ValueError("Campo 'sources' não pode ter mais de 5 itens")
    
    for i, source in enumerate(response.sources):
        if not source.document_id or source.score < 0.0 or source.score > 1.0:
            raise ValueError(f"Source {i} está inválida")
    
    # Metadata
    if not response.metadata:
        raise ValueError("Campo 'metadata' é obrigatório")
    
    if response.metadata.processing_time_ms < 0:
        raise ValueError("Campo 'metadata.processing_time_ms' deve ser positivo")


# ============================================================================
# BUILDERS PARA RESPOSTAS PADRÃO
# ============================================================================


def build_success_response(
    question: str,
    answer: str,
    sources: list,
    score: float,
    conversation_id: Optional[str] = None,
    processing_time_ms: int = 0,
    model_used: str = "gpt-4",
) -> AskResponse:
    """
    Constrói uma resposta de sucesso validada.
    
    Args:
        question: Pergunta original (para log)
        answer: Resposta gerada
        sources: Lista de SourceResponse
        score: Score geral
        conversation_id: ID da conversa
        processing_time_ms: Tempo de processamento
        model_used: Modelo utilizado
        
    Returns:
        AskResponse validada
    """
    response = AskResponse(
        version="1.0",
        answer=answer,
        sources=sources,
        score=score,
        fallback=score < 0.3 or len(sources) == 0,
        fallback_reason=(
            FallbackReason.LOW_SCORE
            if score < 0.3
            else (FallbackReason.NO_SOURCES if len(sources) == 0 else None)
        ),
        conversation_id=conversation_id,
        metadata={
            "processing_time_ms": processing_time_ms,
            "model_used": model_used,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
    )
    validate_ask_response(response)
    return response


def build_fallback_response(
    reason: str = FallbackReason.NO_SOURCES,
    conversation_id: Optional[str] = None,
    processing_time_ms: int = 0,
) -> AskResponse:
    """
    Constrói uma resposta de fallback padronizada.
    
    Args:
        reason: Razão do fallback
        conversation_id: ID da conversa
        processing_time_ms: Tempo de processamento
        
    Returns:
        AskResponse com fallback ativado
    """
    fallback_messages = {
        FallbackReason.LOW_SCORE: (
            "Desculpe, não encontrei informações suficientes na base de conhecimento "
            "para responder sua pergunta com segurança. Recomendo consultar o suporte humano."
        ),
        FallbackReason.NO_SOURCES: (
            "Desculpe, não encontrei informações na base de conhecimento sobre este tópico. "
            "Por favor, entre em contato com o suporte humano."
        ),
        FallbackReason.INTENT_OUT_OF_SCOPE: (
            "Desculpe, sua pergunta está fora do escopo do assistente. "
            "Para perguntas sobre outros tópicos, favor contatar o suporte."
        ),
        FallbackReason.ERROR: (
            "Desculpe, ocorreu um erro ao processar sua pergunta. "
            "Por favor, tente novamente mais tarde."
        ),
    }
    
    answer = fallback_messages.get(
        reason,
        "Desculpe, não consigo responder sua pergunta no momento.",
    )
    
    response = AskResponse(
        version="1.0",
        answer=answer,
        sources=[],
        score=0.0,
        fallback=True,
        fallback_reason=reason,
        conversation_id=conversation_id,
        metadata={
            "processing_time_ms": processing_time_ms,
            "model_used": "fallback",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
    )
    validate_ask_response(response)
    return response


def build_error_response(
    code: str = ErrorCode.INTERNAL_ERROR,
    message: str = "Erro interno do servidor",
    details: Optional[dict] = None,
) -> dict:
    """
    Constrói uma resposta de erro padronizada.
    
    Args:
        code: Código do erro
        message: Mensagem descritiva
        details: Detalhes opcionais
        
    Returns:
        Dicionário com estrutura de erro
    """
    return {
        "version": "1.0",
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
        },
    }


# ============================================================================
# MAPEAMENTO ENTRE CANAIS
# ============================================================================


def map_telegram_to_ask_request(
    update: dict, user_id: str, conversation_id: Optional[str] = None
) -> AskRequest:
    """
    Mapeia um update do Telegram para AskRequest.
    
    Args:
        update: Update do Telegram
        user_id: ID do usuário
        conversation_id: ID da conversa (opcional)
        
    Returns:
        AskRequest validada
    """
    message = update.get("message", {})
    text = message.get("text", "")
    message_id = str(message.get("message_id", ""))
    
    if not text:
        raise ValueError("Mensagem do Telegram está vazia")
    
    request = AskRequest(
        version="1.0",
        question=text,
        user_id=user_id,
        channel="telegram",
        conversation_id=conversation_id,
        metadata={
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "message_id": message_id,
        },
    )
    validate_ask_request(request)
    return request


# ============================================================================
# AUDITORIA E LOGGING
# ============================================================================


def log_request_contract(request: AskRequest, user_ip: Optional[str] = None) -> dict:
    """
    Formata dados de requisição para auditoria.
    
    Args:
        request: AskRequest
        user_ip: IP do usuário (se disponível)
        
    Returns:
        Dicionário com dados de auditoria
    """
    return {
        "version": request.version,
        "channel": request.channel,
        "user_id": request.user_id,
        "question_length": len(request.question),
        "conversation_id": request.conversation_id,
        "ip_address": user_ip or request.metadata.ip_address,
        "timestamp": request.metadata.timestamp,
    }


def log_response_contract(response: AskResponse) -> dict:
    """
    Formata dados de resposta para auditoria.
    
    Args:
        response: AskResponse
        
    Returns:
        Dicionário com dados de auditoria
    """
    return {
        "version": response.version,
        "score": response.score,
        "fallback": response.fallback,
        "fallback_reason": response.fallback_reason,
        "sources_count": len(response.sources),
        "processing_time_ms": response.metadata.processing_time_ms,
        "model_used": response.metadata.model_used,
        "timestamp": response.metadata.timestamp,
    }
