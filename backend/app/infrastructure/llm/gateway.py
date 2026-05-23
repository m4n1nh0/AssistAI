from typing import Protocol

import httpx

from app.core.config import Settings
from app.infrastructure.llm.prompt import build_grounded_prompt
from app.infrastructure.rag.simple_retriever import RetrievalResult


class LLMGateway(Protocol):
    def generate(self, question: str, contexts: list[RetrievalResult]) -> str: ...


class OpenAICompatibleLLMGateway:
    def __init__(self, settings: Settings) -> None:
        if not settings.llm_api_key:
            raise ValueError("ASSISTAI_LLM_API_KEY deve ser configurada para o provedor LLM.")
        self.api_key = settings.llm_api_key
        self.base_url = settings.llm_base_url.rstrip("/")
        self.model = settings.llm_model

    def generate(self, question: str, contexts: list[RetrievalResult]) -> str:
        prompt = build_grounded_prompt(question, contexts)
        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0,
            },
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()


def build_llm_gateway(settings: Settings) -> LLMGateway:
    if settings.llm_provider.lower() in {"openai", "openai-compatible"}:
        return OpenAICompatibleLLMGateway(settings)

    from app.infrastructure.llm.fake_llm import FakeLLMGateway

    return FakeLLMGateway()
