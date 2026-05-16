from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.core.config import Settings
from app.domain.models import DocumentChunk
from app.infrastructure.llm.fake_llm import FakeLLMGateway
from app.infrastructure.llm.ollama_gateway import OllamaLLMGateway
from app.infrastructure.llm.openai_gateway import OpenAILLMGateway
from app.infrastructure.rag.simple_retriever import RetrievalResult


def _fake_chunk(content: str = "Conteudo do documento.", title: str = "Teste") -> DocumentChunk:
    return DocumentChunk(
        id="chk-test",
        document_id="doc-test",
        content=content,
        metadata={"title": title, "document_id": "doc-test"},
    )


class TestFakeLLMGateway:
    def test_generate_with_context_returns_based_on_chunk(self) -> None:
        gateway = FakeLLMGateway()
        chunk = _fake_chunk("Instrucao de reset de senha.", "Reset de Senha")
        result = RetrievalResult(chunk=chunk, score=0.95)

        answer = gateway.generate("Como resetar?", [result])

        assert "Reset de Senha" in answer
        assert "Instrucao de reset" in answer

    def test_generate_without_context_returns_fallback(self) -> None:
        gateway = FakeLLMGateway()

        answer = gateway.generate("Pergunta qualquer", [])

        assert "nao encontrei base" in answer.lower()

    def test_generate_multiple_contexts_uses_first(self) -> None:
        gateway = FakeLLMGateway()
        c1 = _fake_chunk("Primeiro doc", "Doc A")
        c2 = _fake_chunk("Segundo doc", "Doc B")
        results = [
            RetrievalResult(chunk=c1, score=0.9),
            RetrievalResult(chunk=c2, score=0.8),
        ]

        answer = gateway.generate("Pergunta", results)

        assert "Doc A" in answer

    def test_system_prompt_is_accepted_but_ignored(self) -> None:
        gateway = FakeLLMGateway()
        chunk = _fake_chunk("Conteudo", "Doc")
        result = RetrievalResult(chunk=chunk, score=0.9)

        answer = gateway.generate(
            "Pergunta", [result], system_prompt="Seja educado."
        )

        assert answer


class TestOpenAILLMGateway:
    def _make_settings(self) -> Settings:
        return Settings(
            llm_provider="openai",
            llm_api_key="sk-test",
            llm_model="gpt-4o-mini",
        )

    def test_generate_success(self) -> None:
        settings = self._make_settings()
        gateway = OpenAILLMGateway(settings)

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Resposta do assistente."))
        ]

        with patch.object(gateway.client.chat.completions, "create", return_value=mock_response):
            chunk = _fake_chunk("Conteudo do documento.", "Manual")
            result = RetrievalResult(chunk=chunk, score=0.9)

            answer = gateway.generate("Pergunta?", [result])

            assert answer == "Resposta do assistente."

    def test_generate_fallback_on_error(self) -> None:
        from openai import APIError

        settings = self._make_settings()
        gateway = OpenAILLMGateway(settings)

        with patch.object(
            gateway.client.chat.completions,
            "create",
            side_effect=APIError(
                message="API Error",
                request=MagicMock(),
                body=None,
            ),
        ):
            chunk = _fake_chunk()
            result = RetrievalResult(chunk=chunk, score=0.9)

            answer = gateway.generate("Pergunta?", [result])

            assert "nao foi possivel processar" in answer.lower()

    def test_generate_without_context(self) -> None:
        settings = self._make_settings()
        gateway = OpenAILLMGateway(settings)

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Nao sei responder."))
        ]

        with patch.object(gateway.client.chat.completions, "create", return_value=mock_response):
            answer = gateway.generate("Pergunta?", [])

            assert answer == "Nao sei responder."

    def test_generate_with_system_prompt(self) -> None:
        settings = self._make_settings()
        gateway = OpenAILLMGateway(settings)

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Resposta educada."))
        ]

        with patch.object(gateway.client.chat.completions, "create") as mock_create:
            mock_create.return_value = mock_response

            chunk = _fake_chunk()
            result = RetrievalResult(chunk=chunk, score=0.9)
            gateway.generate("Pergunta?", [result], system_prompt="Seja educado.")

            call_kwargs = mock_create.call_args.kwargs
            messages = call_kwargs["messages"]
            assert messages[0]["role"] == "system"
            assert messages[0]["content"] == "Seja educado."


class TestOllamaLLMGateway:
    def test_uses_openai_compatible_client(self) -> None:
        settings = Settings(
            llm_provider="ollama",
            llm_api_key="http://localhost:11434/v1",
            llm_model="llama3",
        )
        gateway = OllamaLLMGateway(settings)

        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message=MagicMock(content="Resposta local."))
        ]

        with patch.object(gateway.client.chat.completions, "create", return_value=mock_response):
            chunk = _fake_chunk()
            result = RetrievalResult(chunk=chunk, score=0.9)
            answer = gateway.generate("Pergunta?", [result])

            assert answer == "Resposta local."

    def test_fallback_on_error(self) -> None:
        from openai import APIError

        settings = Settings(
            llm_provider="ollama",
            llm_api_key="http://localhost:11434/v1",
            llm_model="llama3",
        )
        gateway = OllamaLLMGateway(settings)

        with patch.object(
            gateway.client.chat.completions,
            "create",
            side_effect=APIError(
                message="Connection refused",
                request=MagicMock(),
                body=None,
            ),
        ):
            answer = gateway.generate("Pergunta?", [])

            assert "nao foi possivel processar" in answer.lower()
