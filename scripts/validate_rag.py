#!/usr/bin/env python3
from app.application.services.assistant_service import AssistantService
from app.core.config import get_settings
from app.domain.contracts import AskRequest as DomainAskRequest
from app.domain.enums import Channel as DomainChannel
from app.infrastructure.llm.fake_llm import FakeLLMGateway
from app.infrastructure.mcp.simulated_tools import SimulatedToolRegistry
from app.infrastructure.rag.simple_retriever import SimpleRetriever
from app.infrastructure.repositories.memory import InMemoryRepository


def main() -> None:
    repository = InMemoryRepository()
    repository.seed_default_documents()
    retriever = SimpleRetriever(repository)
    settings = get_settings()
    llm_gateway = FakeLLMGateway()
    tools = SimulatedToolRegistry(enabled=settings.mcp_simulated_enabled)
    assistant_service = AssistantService(
        repository=repository,
        retriever=retriever,
        llm_gateway=llm_gateway,
        tools=tools,
        settings=settings,
    )

    queries = [
        "Como faço para abrir um chamado?",
        "Preciso resetar minha senha",
        "Qual o status do meu chamado CHM-12345?",
        "Quero falar com um atendente humano",
    ]

    print("=== Validação de recuperação semântica ===")
    for query in queries:
        print(f"\nConsulta: {query}")
        results = retriever.search(query)
        if not results:
            print("  Nenhum trecho relevante encontrado pelo SimpleRetriever.")
            continue
        for rank, result in enumerate(results, start=1):
            document = repository.get_document(result.chunk.document_id)
            print(
                f"  [{rank}] documento={document.title if document else 'desconhecido'}"
                f" score={result.score:.4f}"
            )
            print(f"      trecho={result.chunk.content[:120]}...")

    print("\n=== Validação do assistant_service.ask ===")
    for query in queries:
        response = assistant_service.ask(
            DomainAskRequest(
                user_id="web-user-001",
                channel=DomainChannel.WEB,
                message=query,
            )
        )
        print(f"\nPergunta: {query}")
        print(f"Resposta: {response.answer}")
        print(f"  fallback={response.fallback} confidence={response.confidence}")
        print(f"  sources={len(response.sources)}")


if __name__ == "__main__":
    main()
