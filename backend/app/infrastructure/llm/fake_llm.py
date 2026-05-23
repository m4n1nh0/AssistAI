from app.infrastructure.rag.simple_retriever import RetrievalResult

FALLBACK_ANSWER = (
    "Nao encontrei base suficiente para responder com seguranca. "
    "Posso encaminhar este atendimento para um humano."
)

SYSTEM_PROMPT_SUMMARY = (
    "Responda apenas com informacoes presentes nos contextos recuperados. "
    "Nao use conhecimento externo. Se o contexto for insuficiente, use fallback."
)


class FakeLLMGateway:
    def generate(self, question: str, contexts: list[RetrievalResult]) -> str:
        if not contexts:
            return FALLBACK_ANSWER

        primary = contexts[0].chunk
        title = primary.metadata.get("title", "documento da base")
        excerpt = _compact_context(primary.content)
        return f"Com base na base interna ({title}): {excerpt}"


def _compact_context(content: str, max_chars: int = 700) -> str:
    excerpt = " ".join(content.split())
    if len(excerpt) <= max_chars:
        return excerpt
    return excerpt[:max_chars].rsplit(" ", 1)[0] + "."

