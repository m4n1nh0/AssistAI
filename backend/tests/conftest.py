from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.application.services.assistant_service import AssistantService
from app.core.config import Settings
from app.domain.protocols import LLMGateway, Retriever
from app.infrastructure.mcp.simulated_tools import SimulatedToolRegistry
from app.infrastructure.rag.simple_retriever import RetrievalResult
from app.infrastructure.repositories.memory import InMemoryRepository


class FakeTestLLM(LLMGateway):
    def generate(
        self,
        question: str,
        contexts: list[RetrievalResult],
        system_prompt: str | None = None,
    ) -> str:
        if not contexts:
            return "Nao encontrei base suficiente."
        title = contexts[0].chunk.metadata.get("title", "doc")
        return f"Resposta baseada em {title}."


class KeywordTestRetriever(Retriever):
    def __init__(self, repository: InMemoryRepository) -> None:
        self.repository = repository

    def search(self, query: str, top_k: int = 3) -> list[RetrievalResult]:
        from app.infrastructure.rag.simple_retriever import SimpleRetriever

        return SimpleRetriever(self.repository).search(query, top_k=top_k)


@pytest.fixture
def settings() -> Settings:
    return Settings()


@pytest.fixture
def repository() -> InMemoryRepository:
    repo = InMemoryRepository()
    repo.seed_default_documents()
    return repo


@pytest.fixture
def retriever(repository: InMemoryRepository) -> Retriever:
    return KeywordTestRetriever(repository)


@pytest.fixture
def llm_gateway() -> LLMGateway:
    return FakeTestLLM()


@pytest.fixture
def tools() -> SimulatedToolRegistry:
    return SimulatedToolRegistry(enabled=True)


@pytest.fixture
def assistant_service(
    repository: InMemoryRepository,
    retriever: Retriever,
    llm_gateway: LLMGateway,
    tools: SimulatedToolRegistry,
    settings: Settings,
) -> AssistantService:
    return AssistantService(
        repository=repository,
        retriever=retriever,
        llm_gateway=llm_gateway,
        tools=tools,
        settings=settings,
    )


@pytest.fixture
def test_client() -> Generator[TestClient, None, None]:
    from app.main import create_app

    app = create_app()
    with TestClient(app) as client:
        yield client
