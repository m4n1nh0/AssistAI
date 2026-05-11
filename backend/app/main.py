from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.application.services.assistant_service import AssistantService
from app.application.services.document_service import DocumentService
from app.application.services.feedback_service import FeedbackService
from app.application.services.metrics_service import MetricsService
from app.application.services.telegram_service import TelegramService
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.infrastructure.llm.fake_llm import FakeLLMGateway
from app.infrastructure.mcp.simulated_tools import SimulatedToolRegistry
from app.infrastructure.rag.simple_retriever import SimpleRetriever
from app.infrastructure.repositories.memory import InMemoryRepository
from app.infrastructure.database.mysql import MySqlConfig, MySqlUnitOfWork
from app.infrastructure.vector.qdrant import QdrantConfig, QdrantVectorStore


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.environment)

    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="POC do Assistente de Atendimento Inteligente.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Inicialização de Componentes
    if settings.use_real_database:
        # Aqui integraríamos com o MySqlUnitOfWork real
        # Por enquanto mantemos o InMemory para não quebrar a POC sem banco configurado
        repository = InMemoryRepository()
    else:
        repository = InMemoryRepository()
    
    repository.seed_default_documents()

    if settings.use_real_vector_store:
        vector_config = QdrantConfig(url=settings.qdrant_url, collection=settings.qdrant_collection)
        vector_store = QdrantVectorStore(vector_config)
        # O retriever usaria o vector_store no futuro
        retriever = SimpleRetriever(repository)
    else:
        retriever = SimpleRetriever(repository)

    if settings.llm_provider == "mock":
        llm_gateway = FakeLLMGateway()
    else:
        # Aqui integraria com OpenAI/Anthropic/etc
        llm_gateway = FakeLLMGateway()

    tools = SimulatedToolRegistry(enabled=settings.mcp_simulated_enabled)

    # Injeção de Dependências no app.state
    app.state.repository = repository
    app.state.document_service = DocumentService(repository)
    app.state.assistant_service = AssistantService(
        repository=repository,
        retriever=retriever,
        llm_gateway=llm_gateway,
        tools=tools,
        settings=settings,
    )
    app.state.feedback_service = FeedbackService(repository)
    app.state.metrics_service = MetricsService(repository)
    app.state.telegram_service = TelegramService(app.state.assistant_service)

    app.include_router(api_router, prefix=settings.api_prefix)
    return app


app = create_app()

