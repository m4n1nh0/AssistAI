"""
Testes de Contrato para o Assistente Inteligente.

Este módulo contém testes que validam a conformidade com o contrato oficial
de Pergunta e Resposta entre Web, Telegram, API e Motor de IA.

Execução:
    pytest backend/tests/test_contract.py -v
"""

import pytest
from datetime import datetime
from app.domain.contracts import (
    AskRequest,
    AskResponse,
    RequestMetadata,
    SourceResponse,
    ResponseMetadata,
    FeedbackRequest,
    ErrorResponse,
)
from app.domain.enums import Channel
from app.infrastructure.validation import (
    sanitize_question,
    validate_ask_request,
    validate_ask_response,
    build_fallback_response,
    build_success_response,
    map_telegram_to_ask_request,
)


# ============================================================================
# TESTES DE REQUEST
# ============================================================================


class TestAskRequestContract:
    """Testes de conformidade do AskRequest com o contrato."""

    def test_valid_request_minimal(self):
        """Deve aceitar request mínimo válido."""
        request = AskRequest(
            version="1.0",
            question="Teste?",
            channel=Channel.WEB,
            metadata=RequestMetadata(timestamp=datetime.utcnow()),
        )
        validate_ask_request(request)
        assert request.version == "1.0"

    def test_valid_request_complete(self):
        """Deve aceitar request completo."""
        request = AskRequest(
            version="1.0",
            question="Como reiniciar o servidor?",
            user_id="user123",
            channel=Channel.TELEGRAM,
            session_id="sess456",
            conversation_id="conv789",
            metadata=RequestMetadata(
                timestamp=datetime.utcnow(),
                user_agent="Mozilla/5.0...",
                ip_address="192.168.1.1",
                message_id="msg123",
            ),
        )
        validate_ask_request(request)

    def test_question_required(self):
        """Campo 'question' deve ser obrigatório."""
        with pytest.raises(Exception):
            AskRequest(
                version="1.0",
                question="",  # Vazio
                channel=Channel.WEB,
                metadata=RequestMetadata(timestamp=datetime.utcnow()),
            )

    def test_question_max_length(self):
        """Campo 'question' tem limite de 1000 caracteres."""
        with pytest.raises(Exception):
            AskRequest(
                version="1.0",
                question="x" * 1001,  # Excede limite
                channel=Channel.WEB,
                metadata=RequestMetadata(timestamp=datetime.utcnow()),
            )

    def test_question_whitespace_only(self):
        """Campo 'question' não pode ser apenas espaços."""
        with pytest.raises(Exception):
            question_only_spaces = AskRequest(
                version="1.0",
                question="   ",
                channel=Channel.WEB,
                metadata=RequestMetadata(timestamp=datetime.utcnow()),
            )

    def test_channel_required(self):
        """Campo 'channel' deve ser obrigatório."""
        with pytest.raises(Exception):
            AskRequest(
                version="1.0",
                question="Teste",
                channel=None,  # type: ignore
                metadata=RequestMetadata(timestamp=datetime.utcnow()),
            )

    def test_channel_valid_values(self):
        """Campo 'channel' aceita apenas 'web' ou 'telegram'."""
        # Válido: web
        request = AskRequest(
            version="1.0",
            question="Teste",
            channel=Channel.WEB,
            metadata=RequestMetadata(timestamp=datetime.utcnow()),
        )
        assert request.channel == Channel.WEB

        # Válido: telegram
        request = AskRequest(
            version="1.0",
            question="Teste",
            channel=Channel.TELEGRAM,
            metadata=RequestMetadata(timestamp=datetime.utcnow()),
        )
        assert request.channel == Channel.TELEGRAM

    def test_metadata_required(self):
        """Campo 'metadata' deve ser obrigatório."""
        with pytest.raises(Exception):
            AskRequest(
                version="1.0",
                question="Teste",
                channel=Channel.WEB,
                metadata=None,  # type: ignore
            )

    def test_timestamp_required(self):
        """Campo 'metadata.timestamp' deve ser obrigatório."""
        with pytest.raises(Exception):
            RequestMetadata(timestamp=None)  # type: ignore

    def test_question_trimmed(self):
        """Pergunta deve ser trimmed automaticamente."""
        request = AskRequest(
            version="1.0",
            question="  Teste com espaços  ",
            channel=Channel.WEB,
            metadata=RequestMetadata(timestamp=datetime.utcnow()),
        )
        assert request.question == "Teste com espaços"


# ============================================================================
# TESTES DE RESPONSE
# ============================================================================


class TestAskResponseContract:
    """Testes de conformidade do AskResponse com o contrato."""

    def test_valid_response_success(self):
        """Deve aceitar response de sucesso válido."""
        response = AskResponse(
            version="1.0",
            answer="Resposta teste",
            sources=[],
            score=0.9,
            fallback=False,
            metadata=ResponseMetadata(
                processing_time_ms=100,
                model_used="gpt-4",
                timestamp=datetime.utcnow(),
            ),
        )
        validate_ask_response(response)

    def test_valid_response_with_sources(self):
        """Deve aceitar response com fontes."""
        sources = [
            SourceResponse(
                document_id="doc001",
                title="Guia",
                content="Conteúdo",
                score=0.95,
                version="1.0",
            )
        ]
        response = AskResponse(
            version="1.0",
            answer="Resposta com fontes",
            sources=sources,
            score=0.95,
            fallback=False,
            metadata=ResponseMetadata(
                processing_time_ms=100,
                model_used="gpt-4",
                timestamp=datetime.utcnow(),
            ),
        )
        validate_ask_response(response)

    def test_valid_response_fallback(self):
        """Deve aceitar response com fallback."""
        response = AskResponse(
            version="1.0",
            answer="Não encontrei resposta.",
            sources=[],
            score=0.0,
            fallback=True,
            fallback_reason="no_sources",
            metadata=ResponseMetadata(
                processing_time_ms=50,
                model_used="fallback",
                timestamp=datetime.utcnow(),
            ),
        )
        validate_ask_response(response)

    def test_answer_required(self):
        """Campo 'answer' deve ser obrigatório."""
        with pytest.raises(Exception):
            AskResponse(
                version="1.0",
                answer="",  # Vazio
                sources=[],
                score=0.5,
                fallback=False,
                metadata=ResponseMetadata(
                    processing_time_ms=100,
                    model_used="gpt-4",
                    timestamp=datetime.utcnow(),
                ),
            )

    def test_answer_max_length(self):
        """Campo 'answer' tem limite de 4000 caracteres."""
        with pytest.raises(Exception):
            AskResponse(
                version="1.0",
                answer="x" * 4001,  # Excede limite
                sources=[],
                score=0.5,
                fallback=False,
                metadata=ResponseMetadata(
                    processing_time_ms=100,
                    model_used="gpt-4",
                    timestamp=datetime.utcnow(),
                ),
            )

    def test_score_range(self):
        """Campo 'score' deve estar entre 0.0 e 1.0."""
        # Score válido
        response = AskResponse(
            version="1.0",
            answer="Teste",
            sources=[],
            score=0.5,
            fallback=False,
            metadata=ResponseMetadata(
                processing_time_ms=100,
                model_used="gpt-4",
                timestamp=datetime.utcnow(),
            ),
        )
        validate_ask_response(response)

        # Score inválido (>1.0)
        with pytest.raises(Exception):
            AskResponse(
                version="1.0",
                answer="Teste",
                sources=[],
                score=1.5,  # Acima do máximo
                fallback=False,
                metadata=ResponseMetadata(
                    processing_time_ms=100,
                    model_used="gpt-4",
                    timestamp=datetime.utcnow(),
                ),
            )

    def test_sources_max_count(self):
        """Campo 'sources' não pode ter mais de 5 itens."""
        sources = [
            SourceResponse(
                document_id=f"doc{i:03d}",
                title=f"Doc {i}",
                content="Conteúdo",
                score=0.9,
                version="1.0",
            )
            for i in range(6)  # 6 fontes
        ]

        with pytest.raises(Exception):
            AskResponse(
                version="1.0",
                answer="Teste",
                sources=sources,
                score=0.9,
                fallback=False,
                metadata=ResponseMetadata(
                    processing_time_ms=100,
                    model_used="gpt-4",
                    timestamp=datetime.utcnow(),
                ),
            )

    def test_source_score_range(self):
        """Score de fonte deve estar entre 0.0 e 1.0."""
        with pytest.raises(Exception):
            SourceResponse(
                document_id="doc001",
                title="Doc",
                content="Conteúdo",
                score=1.5,  # Inválido
                version="1.0",
            )

    def test_fallback_with_low_score(self):
        """Fallback deve ser ativado com score < 0.3."""
        response = AskResponse(
            version="1.0",
            answer="Resposta com baixo score",
            sources=[],
            score=0.2,
            fallback=True,
            fallback_reason="low_score",
            metadata=ResponseMetadata(
                processing_time_ms=100,
                model_used="gpt-4",
                timestamp=datetime.utcnow(),
            ),
        )
        validate_ask_response(response)


# ============================================================================
# TESTES DE BUILDERS
# ============================================================================


class TestResponseBuilders:
    """Testes de builders para respostas."""

    def test_build_success_response(self):
        """Deve construir response de sucesso válida."""
        sources = [
            SourceResponse(
                document_id="doc001",
                title="Guia",
                content="Conteúdo",
                score=0.95,
                version="1.0",
            )
        ]
        response = build_success_response(
            question="Como?",
            answer="Resposta",
            sources=sources,
            score=0.9,
            processing_time_ms=100,
        )
        assert response.version == "1.0"
        assert response.fallback is False
        assert response.score == 0.9

    def test_build_fallback_response(self):
        """Deve construir response de fallback válida."""
        response = build_fallback_response(reason="no_sources")
        assert response.fallback is True
        assert response.score == 0.0
        assert len(response.sources) == 0
        assert response.fallback_reason == "no_sources"


# ============================================================================
# TESTES DE INTEGRAÇÃO (WEB + TELEGRAM)
# ============================================================================


class TestChannelIntegration:
    """Testes de integração com múltiplos canais."""

    def test_web_request_mapping(self):
        """Request da Web deve ser válido."""
        request = AskRequest(
            version="1.0",
            question="Teste web",
            user_id="web_user",
            channel=Channel.WEB,
            metadata=RequestMetadata(
                timestamp=datetime.utcnow(),
                user_agent="Mozilla/5.0...",
            ),
        )
        validate_ask_request(request)

    def test_telegram_request_mapping(self):
        """Request do Telegram deve ser válido."""
        telegram_update = {
            "message": {
                "text": "Teste telegram",
                "message_id": 123456,
            }
        }
        request = map_telegram_to_ask_request(
            telegram_update, user_id="telegram_user"
        )
        validate_ask_request(request)
        assert request.channel == Channel.TELEGRAM
        assert request.question == "Teste telegram"


# ============================================================================
# TESTES DE VALIDAÇÃO
# ============================================================================


class TestValidation:
    """Testes de funções de validação."""

    def test_sanitize_question_valid(self):
        """Deve sanitizar pergunta válida."""
        result = sanitize_question("  Teste com espaços  ")
        assert result == "Teste com espaços"

    def test_sanitize_question_empty(self):
        """Deve rejeitar pergunta vazia."""
        with pytest.raises(ValueError):
            sanitize_question("   ")

    def test_sanitize_question_too_long(self):
        """Deve rejeitar pergunta muito longa."""
        with pytest.raises(ValueError):
            sanitize_question("x" * 1001)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
