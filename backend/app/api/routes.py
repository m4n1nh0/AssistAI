from fastapi import APIRouter

from app.api.schemas import AskRequest, AskResponse
from app.application.assistant_service import assistant_service

router = APIRouter(prefix="/api")


@router.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest) -> dict:
    return assistant_service.ask(payload.user_id, payload.channel, payload.message)
