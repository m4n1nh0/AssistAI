from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.bootstrap import build_container
from app.core.config import get_settings
from app.core.logging import configure_logging


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.environment)

    app = FastAPI(
        title=settings.app_name,
        version=settings.api_version,
        description="POC do Assistente de Atendimento Inteligente.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    container = build_container(settings)
    app.state.settings = settings
    app.state.repository = container.repository
    app.state.document_service = container.document_service
    app.state.assistant_service = container.assistant_service
    app.state.feedback_service = container.feedback_service
    app.state.metrics_service = container.metrics_service
    app.state.telegram_service = container.telegram_service
    app.state.mysql_uow = container.mysql_uow
    app.state.vector_store = container.vector_store
    app.state.integrations = container.integrations

    app.include_router(api_router, prefix=settings.api_prefix)
    return app


app = create_app()
