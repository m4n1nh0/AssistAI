class LLMClient:
    """Gateway inicial para LLM.

    A implementação real deve conectar o provedor definido por variável de ambiente.
    Para a fundação técnica, o stub mantém o fluxo demonstrável e testável.
    """

    def generate_answer(self, question: str, context: str) -> str:
        if not context.strip():
            return ""
        return (
            "Com base na base de conhecimento recuperada: "
            f"{context.strip()[:500]}"
        )
