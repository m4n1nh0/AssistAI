from __future__ import annotations

import logging

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
from app.domain.protocols import Repository
from app.infrastructure.embeddings.factory import create_embedding_service
from app.infrastructure.llm.fake_llm import FakeLLMGateway
from app.infrastructure.llm.ollama_gateway import OllamaLLMGateway
from app.infrastructure.llm.openai_gateway import OpenAILLMGateway
from app.infrastructure.mcp.simulated_tools import SimulatedToolRegistry
from app.infrastructure.rag.semantic_retriever import SemanticRetriever
from app.infrastructure.rag.simple_retriever import SimpleRetriever
from app.infrastructure.repositories.memory import InMemoryRepository
from app.infrastructure.vector.qdrant import QdrantConfig, QdrantVectorStore

logger = logging.getLogger(__name__)


def _build_llm_gateway(settings):
    provider = settings.llm_provider

    if provider == "openai":
        if not settings.llm_api_key:
            logger.warning(
                "LLM provider OpenAI sem API key, usando mock"
            )
            return FakeLLMGateway()
        logger.info(
            "Usando OpenAI LLM: model=%s", settings.llm_model
        )
        return OpenAILLMGateway(settings)

    if provider == "ollama":
        logger.info(
            "Usando Ollama LLM: model=%s", settings.llm_model
        )
        return OllamaLLMGateway(settings)

    logger.info(
        "LLM provider=%s nao reconhecido, usando FakeLLM",
        provider,
    )
    return FakeLLMGateway()


def _build_retriever(repository, settings):
    embedding_service = create_embedding_service(settings)

    qdrant_config = QdrantConfig(
        url=settings.qdrant_url,
        collection=settings.qdrant_collection,
    )

    vector_store = QdrantVectorStore(qdrant_config, embedding_service)
    try:
        _seed_qdrant(repository, vector_store)
    except Exception as exc:
        logger.warning(
            "Nao foi possible semear Qdrant: %s. "
            "Usando SimpleRetriever como fallback.",
            exc,
        )
        return SimpleRetriever(repository), None

    retriever = SemanticRetriever(
        vector_store=vector_store,
        repository=repository,
        min_score=settings.min_relevance_score,
    )
    return retriever, vector_store


def _build_repository(settings: Settings) -> Repository:
    if settings.database_persistence == "mysql":
        if not settings.mysql_url:
            logger.warning(
                "database_persistence=mysql mas ASSISTAI_MYSQL_URL nao configurado. "
                "Usando InMemoryRepository."
            )
            return InMemoryRepository()

        try:
            from app.infrastructure.database.mysql import (
                MySqlConfig,
                MySqlUnitOfWork,
            )
            from app.infrastructure.database.mysql_repository import (
                MySqlRepository,
            )

            uow = MySqlUnitOfWork(MySqlConfig(url=settings.mysql_url))
            repo = MySqlRepository(uow.session_maker)
            logger.info("Usando MySqlRepository: %s", settings.mysql_url)
            return repo
        except ImportError as exc:
            logger.warning(
                "MySQL nao disponivel (instale o group database): %s. "
                "Usando InMemoryRepository.",
                exc,
            )
            return InMemoryRepository()
        except Exception as exc:
            logger.warning(
                "Falha ao conectar MySQL: %s. Usando InMemoryRepository.", exc
            )
            return InMemoryRepository()

    logger.info(
        "Usando InMemoryRepository (database_persistence=%s)",
        settings.database_persistence,
    )
    return InMemoryRepository()


def _seed_qdrant(
    repository: InMemoryRepository,
    vector_store: QdrantVectorStore,
) -> None:
    if vector_store.collection_size() > 0:
        return

    chunks = repository.list_active_chunks()
    if chunks:
        indexed = vector_store.upsert_chunks(chunks)
        if indexed == 0:
            raise RuntimeError(
                "Falha ao semear Qdrant: 0 chunks indexados"
            )
        logger.info(
            "Qdrant semeado com %d chunks da base inicial",
            indexed,
        )


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

    repository = _build_repository(settings)
    repository.seed_default_documents()

    retriever, vector_store = _build_retriever(repository, settings)
    llm_gateway = _build_llm_gateway(settings)
    tools = SimulatedToolRegistry(enabled=settings.mcp_simulated_enabled)

    app.state.repository = repository
    app.state.document_service = DocumentService(
        repository=repository,
        vector_store=vector_store,
    )
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
