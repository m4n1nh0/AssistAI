from fastapi import Request

from app.application.services.assistant_service import AssistantService
from app.application.services.document_service import DocumentService
from app.application.services.feedback_service import FeedbackService
from app.application.services.metrics_service import MetricsService
from app.application.services.telegram_service import TelegramService
from app.domain.protocols import Repository


def get_repository(request: Request) -> Repository:
    return request.app.state.repository


def get_assistant_service(request: Request) -> AssistantService:
    return request.app.state.assistant_service


def get_document_service(request: Request) -> DocumentService:
    return request.app.state.document_service


def get_feedback_service(request: Request) -> FeedbackService:
    return request.app.state.feedback_service


def get_metrics_service(request: Request) -> MetricsService:
    return request.app.state.metrics_service


def get_telegram_service(request: Request) -> TelegramService:
    return request.app.state.telegram_service

