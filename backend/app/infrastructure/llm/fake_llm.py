from app.domain.protocols import LLMGateway
from app.infrastructure.rag.simple_retriever import RetrievalResult


class FakeLLMGateway(LLMGateway):
    def generate(
        self,
        question: str,
        contexts: list[RetrievalResult],
        system_prompt: str | None = None,
    ) -> str:
        if not contexts:
            return (
                "Nao encontrei base suficiente para responder com seguranca. "
                "Posso encaminhar este atendimento para um humano."
            )

        primary = contexts[0].chunk
        title = primary.metadata.get("title", "documento da base")
        excerpt = " ".join(primary.content.split())
        return f"Com base em {title}: {excerpt}"
