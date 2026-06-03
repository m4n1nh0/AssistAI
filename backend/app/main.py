from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import ask, health
from app.application.services.assistant_service import AssistantService
from app.core.config import get_settings
from app.infrastructure.llm.fake_llm import FakeLLMGateway
from app.infrastructure.mcp.simulated_tools import SimulatedToolRegistry
from app.infrastructure.repositories.memory import InMemoryRepository
from app.infrastructure.vector.qdrant import HybridRetriever, QdrantConfig, QdrantVectorStore


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    repository = InMemoryRepository()
    repository.seed_default_documents()

    vector_store = QdrantVectorStore(
        QdrantConfig(url=settings.qdrant_url, collection=settings.qdrant_collection)
    )
    retriever = HybridRetriever(repository, vector_store)
    retriever.index_documents()

    assistant_service = AssistantService(
        repository=repository,
        retriever=retriever,
        llm_gateway=FakeLLMGateway(),
        tools=SimulatedToolRegistry(),
        settings=settings,
    )

    app.state.settings = settings
    app.state.repository = repository
    app.state.vector_store = vector_store
    app.state.retriever = retriever
    app.state.assistant_service = assistant_service

    for router in (health.router, ask.router):
        app.include_router(router)
        app.include_router(router, prefix="/api")
    return app


app = create_app()
