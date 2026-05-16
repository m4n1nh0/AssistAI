from app.core.config import Settings
from app.infrastructure.llm.fake_llm import ContextOnlyLLMGateway
from app.infrastructure.llm.gateway import LlmGateway
from app.infrastructure.llm.openai_compatible import OpenAICompatibleGateway


def build_llm_gateway(settings: Settings) -> LlmGateway:
    provider = settings.llm_provider.strip().lower()
    if provider in {"mock", "fake", "context-only", "local"}:
        return ContextOnlyLLMGateway()

    if provider in {"openai", "openai-compatible"}:
        if not settings.llm_api_key:
            raise ValueError("ASSISTAI_LLM_API_KEY is required for OpenAI-compatible LLMs.")
        return OpenAICompatibleGateway(
            api_key=settings.llm_api_key,
            model=settings.llm_model,
            base_url=settings.llm_base_url,
            timeout_seconds=settings.llm_timeout_seconds,
        )

    raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
