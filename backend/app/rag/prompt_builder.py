def build_context_prompt(question: str, contexts: list[str]) -> str:
    context_block = "\n\n".join(contexts)
    return (
        "Responda em português do Brasil usando somente o contexto abaixo.\n"
        "Se o contexto não for suficiente, informe que não há base suficiente.\n\n"
        f"Contexto:\n{context_block}\n\n"
        f"Pergunta: {question}"
    )
