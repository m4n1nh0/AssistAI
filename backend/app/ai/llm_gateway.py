from app.ai.retriever import RetrievedContext


class MockLLMGateway:
    def generate_answer(self, question: str, contexts: list[RetrievedContext]) -> str:
        if not contexts:
            return "Nao encontrei base suficiente para responder com seguranca. Posso encaminhar para um atendente humano."

        best = contexts[0].document
        return (
            f"Com base em {best.title}, {best.content} "
            "Se precisar, posso ajudar a transformar isso em um chamado para atendimento humano."
        )


llm_gateway = MockLLMGateway()
