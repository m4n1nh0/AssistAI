from app.infrastructure.llm.gateway import LlmGeneration
from app.infrastructure.llm.prompt import FALLBACK_ANSWER, render_user_prompt
from app.infrastructure.rag.simple_retriever import RetrievalResult


class ContextOnlyLLMGateway:
    def generate(self, question: str, contexts: list[RetrievalResult]) -> LlmGeneration:
        prompt = render_user_prompt(question, contexts)
        if not contexts:
            return LlmGeneration(
                answer=FALLBACK_ANSWER,
                safe_to_answer=False,
                prompt=prompt,
                provider="context-only",
            )

        primary = contexts[0].chunk
        title = primary.metadata.get("title", "documento da base")
        excerpt = " ".join(primary.content.split())
        return LlmGeneration(
            answer=f"Com base em {title}: {excerpt}",
            safe_to_answer=True,
            prompt=prompt,
            provider="context-only",
        )


FakeLLMGateway = ContextOnlyLLMGateway
