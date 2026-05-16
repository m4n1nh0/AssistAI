from fastapi import APIRouter

from app.api.routes import assistant, attendances, documents, feedback, health, metrics, telegram

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(feedback.router, tags=["feedback"])
api_router.include_router(attendances.router, tags=["attendances"])
api_router.include_router(documents.router, tags=["documents"])
api_router.include_router(metrics.router, tags=["metrics"])
api_router.include_router(telegram.router, tags=["telegram"])
api_router.include_router(assistant.router, tags=["assistant"])

