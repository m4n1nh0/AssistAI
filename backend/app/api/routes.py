from fastapi import APIRouter, HTTPException

from app.api.schemas import (
    AskRequest,
    AskResponse,
    DocumentCreateRequest,
    DocumentResponse,
    FeedbackRequest,
    FeedbackResponse,
    TelegramWebhookRequest,
)
from app.application.assistant_service import assistant_service
from app.domain.models import Channel
from app.infrastructure.repositories import repository

router = APIRouter(prefix="/api")


@router.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest) -> dict:
    return assistant_service.ask(payload.user_id, payload.channel, payload.message)


@router.post("/chat", response_model=AskResponse)
def chat_alias(payload: AskRequest) -> dict:
    return assistant_service.ask(payload.user_id, payload.channel, payload.message)


@router.post("/feedback", response_model=FeedbackResponse)
def feedback(payload: FeedbackRequest) -> dict[str, str]:
    repository.add_feedback(payload.message_id, payload.useful, payload.comment)
    return {"status": "saved"}


@router.get("/attendances")
def list_attendances() -> list[dict]:
    return [
        {
            "id": attendance.id,
            "user_id": attendance.user_id,
            "channel": attendance.channel,
            "needs_human": attendance.needs_human,
            "message_count": len(attendance.messages),
            "created_at": attendance.created_at,
        }
        for attendance in repository.list_attendances()
    ]


@router.get("/attendances/{attendance_id}")
def get_attendance(attendance_id: str) -> dict:
    attendance = repository.get_attendance(attendance_id)
    if not attendance:
        raise HTTPException(status_code=404, detail="Atendimento nao encontrado.")

    return {
        "id": attendance.id,
        "user_id": attendance.user_id,
        "channel": attendance.channel,
        "needs_human": attendance.needs_human,
        "messages": attendance.messages,
    }


@router.get("/documents", response_model=list[DocumentResponse])
def list_documents() -> list[dict]:
    documents = repository.list_documents()
    return [
        {
            "id": document.id,
            "title": document.title,
            "category": document.category,
            "version": document.version,
            "status": document.status,
            "tags": document.tags,
        }
        for document in documents
    ]


@router.post("/documents", response_model=DocumentResponse)
def create_document(payload: DocumentCreateRequest) -> dict:
    document = assistant_service.create_document(payload.model_dump())
    return {
        "id": document.id,
        "title": document.title,
        "category": document.category,
        "version": document.version,
        "status": document.status,
        "tags": document.tags,
    }


@router.post("/documents/reindex")
def reindex_documents() -> dict[str, str]:
    return {"status": "reindexed", "mode": "in-memory"}


@router.post("/telegram/webhook")
def telegram_webhook(payload: TelegramWebhookRequest) -> dict:
    message = payload.message.get("text", "")
    user_id = str(payload.message.get("from", {}).get("id", "telegram-user"))
    response = assistant_service.ask(user_id=user_id, channel=Channel.TELEGRAM, message=message)
    return {"method": "sendMessage", "text": response["answer"]}
