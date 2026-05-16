from __future__ import annotations

import logging
from collections.abc import Generator

from openai import APIError, APITimeoutError, RateLimitError

from app.core.config import Settings
from app.domain.protocols import LLMGateway
from app.infrastructure.rag.simple_retriever import RetrievalResult

logger = logging.getLogger(__name__)


class OllamaLLMGateway(LLMGateway):
    def __init__(self, settings: Settings) -> None:
        self.model = settings.llm_model
        self.temperature = settings.llm_temperature
        self.max_tokens = settings.llm_max_tokens
        self.timeout = settings.llm_timeout_seconds

        base_url = settings.llm_api_key or "http://localhost:11434/v1"

        from openai import OpenAI as OpenAICompat

        self.client = OpenAICompat(
            api_key="ollama",
            base_url=base_url,
            timeout=self.timeout,
            max_retries=2,
        )

    def generate(
        self,
        question: str,
        contexts: list[RetrievalResult],
        system_prompt: str | None = None,
    ) -> str:
        messages = self._build_messages(question, contexts, system_prompt)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            return response.choices[0].message.content or ""

        except RateLimitError:
            logger.warning("Rate limit atingido no Ollama")
            return self._fallback_message()
        except APITimeoutError:
            logger.warning("Timeout no Ollama")
            return self._fallback_message()
        except APIError as exc:
            logger.error("Erro na API Ollama: %s", exc)
            return self._fallback_message()

    def generate_stream(
        self,
        question: str,
        contexts: list[RetrievalResult],
        system_prompt: str | None = None,
    ) -> Generator[str, None, None]:
        messages = self._build_messages(question, contexts, system_prompt)

        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True,
            )
            for chunk in stream:
                content = chunk.choices[0].delta.content or ""
                if content:
                    yield content

        except (RateLimitError, APITimeoutError, APIError) as exc:
            logger.warning("Erro no stream Ollama: %s", exc)
            yield self._fallback_message()

    def _build_messages(
        self,
        question: str,
        contexts: list[RetrievalResult],
        system_prompt: str | None,
    ) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        context_block = self._format_contexts(contexts)
        if context_block:
            user_content = f"{context_block}\n\nPergunta: {question}"
        else:
            user_content = question

        messages.append({"role": "user", "content": user_content})
        return messages

    def _format_contexts(self, contexts: list[RetrievalResult]) -> str:
        if not contexts:
            return ""

        parts: list[str] = []
        for i, ctx in enumerate(contexts, start=1):
            title = ctx.chunk.metadata.get("title", "documento")
            parts.append(f"[{i}] ({title}) {ctx.chunk.content}")

        return "Contexto:\n" + "\n\n".join(parts)

    def _fallback_message(self) -> str:
        return (
            "Nao foi possivel processar sua pergunta no momento. "
            "Tente novamente mais tarde ou solicite atendimento humano."
        )
