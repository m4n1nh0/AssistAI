from app.infrastructure.llm.prompt import FALLBACK_ANSWER, build_grounded_prompt
from app.infrastructure.rag.simple_retriever import RetrievalResult


class FakeLLMGateway:
    last_prompt: str | None = None

    def generate(self, question: str, contexts: list[RetrievalResult]) -> str:
        self.last_prompt = build_grounded_prompt(question, contexts)
        if not contexts:
            return FALLBACK_ANSWER

        primary = contexts[0].chunk
        title = primary.metadata.get("title", "documento da base")
        excerpt = " ".join(primary.content.split())
        return f"Com base em {title}: {excerpt}"

