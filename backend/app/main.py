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
from app.infrastructure.llm.langgraph_llm import LangChainLLMGateway
from app.infrastructure.mcp.simulated_tools import SimulatedToolRegistry
from app.infrastructure.vector.qdrant import QdrantConfig, QdrantVectorStore

from app.infrastructure.database.database import engine
from app.infrastructure.database.models import Base

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

    # Initialize SQL database tables
    Base.metadata.create_all(bind=engine)

    config = QdrantConfig(url=settings.qdrant_url, collection=settings.qdrant_collection)
    retriever = QdrantVectorStore(config)
    
    llm_gateway = LangChainLLMGateway(
        provider=settings.llm_provider,
        model_name=settings.llm_model,
        api_key=settings.llm_api_key,
    )
    tools = SimulatedToolRegistry(enabled=settings.mcp_simulated_enabled)

    # Mount stateless singletons strictly in app state
    app.state.settings = settings
    app.state.retriever = retriever
    app.state.llm_gateway = llm_gateway
    app.state.tools = tools

    app.include_router(api_router, prefix=settings.api_prefix)
    return app


app = create_app()

