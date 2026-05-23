import warnings
from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.application.services.assistant_service import AssistantService
from app.application.services.document_service import DocumentService
from app.application.services.feedback_service import FeedbackService
from app.application.services.metrics_service import MetricsService
from app.application.services.telegram_service import TelegramService
from app.infrastructure.database.database import get_db
from app.infrastructure.repositories.mysql import MySQLRepository


def get_repository(db: Session = Depends(get_db)) -> MySQLRepository:
    return MySQLRepository(db)


def get_assistant_service(request: Request, repo: MySQLRepository = Depends(get_repository)) -> AssistantService:
    # We still get LLM and Retriever from app.state for performance, 
    # but the repository (which needs db connection) is scoped to the request.
    return AssistantService(
        repository=repo,
        retriever=request.app.state.retriever,
        llm_gateway=request.app.state.llm_gateway,
        tools=request.app.state.tools,
        settings=request.app.state.settings,
    )


def get_document_service(repo: MySQLRepository = Depends(get_repository)) -> DocumentService:
    return DocumentService(repo)


def get_feedback_service(repo: MySQLRepository = Depends(get_repository)) -> FeedbackService:
    return FeedbackService(repo)


def get_metrics_service(repo: MySQLRepository = Depends(get_repository)) -> MetricsService:
    return MetricsService(repo)


def get_telegram_service(assistant_service: AssistantService = Depends(get_assistant_service)) -> TelegramService:
    return TelegramService(assistant_service)


