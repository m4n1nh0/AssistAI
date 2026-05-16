from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.application.services.assistant_service import AssistantService
from app.application.services.document_service import DocumentService
from app.application.services.feedback_service import FeedbackService
from app.application.services.metrics_service import MetricsService
from app.application.services.telegram_service import TelegramService
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.infrastructure.database.mysql import MySqlAuditStore, MySqlConfig, MySqlUnitOfWork
from app.infrastructure.knowledge.loader import load_documents
from app.infrastructure.llm.factory import build_llm_gateway
from app.infrastructure.mcp.simulated_tools import SimulatedToolRegistry
from app.infrastructure.rag.simple_retriever import SimpleRetriever
from app.infrastructure.repositories.memory import InMemoryRepository
from app.infrastructure.vector.qdrant import QdrantConfig, QdrantVectorStore


def _seed_knowledge_base(repository: InMemoryRepository, knowledge_base_path: str) -> None:
    path = Path(knowledge_base_path)
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[2] / path

    documents = load_documents(path)
    if documents:
        repository.seed_documents(documents)
        return

    repository.seed_default_documents()


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

    repository = InMemoryRepository()
    _seed_knowledge_base(repository, settings.knowledge_base_path)

    mysql_uow = MySqlUnitOfWork(
        MySqlConfig(
            url=settings.mysql_url,
            connect_timeout_seconds=settings.mysql_connect_timeout_seconds,
        )
    )
    mysql_audit_store = MySqlAuditStore(
        mysql_uow,
        enabled=settings.mysql_persistence_enabled,
    )
    vector_store = QdrantVectorStore(
        QdrantConfig(
            url=settings.qdrant_url,
            collection=settings.qdrant_collection,
        )
    )
    retriever = SimpleRetriever(repository, vector_store=vector_store)
    llm_gateway = build_llm_gateway(settings)
    tools = SimulatedToolRegistry(enabled=settings.mcp_simulated_enabled)

    app.state.repository = repository
    app.state.mysql_uow = mysql_uow
    app.state.mysql_audit_store = mysql_audit_store
    app.state.vector_store = vector_store
    app.state.document_service = DocumentService(repository, vector_store)
    app.state.assistant_service = AssistantService(
        repository=repository,
        retriever=retriever,
        llm_gateway=llm_gateway,
        tools=tools,
        settings=settings,
        audit_store=mysql_audit_store,
    )
    app.state.feedback_service = FeedbackService(repository, mysql_audit_store)
    app.state.metrics_service = MetricsService(repository)
    app.state.telegram_service = TelegramService(app.state.assistant_service)

    app.include_router(api_router, prefix=settings.api_prefix)
    return app


app = create_app()
