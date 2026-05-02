from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_telegram_service
from app.application.services.telegram_service import TelegramService
from app.domain.contracts import AskResponse, TelegramWebhookRequest

router = APIRouter()
TelegramServiceDep = Annotated[TelegramService, Depends(get_telegram_service)]


@router.post("/telegram/webhook", response_model=AskResponse)
def telegram_webhook(
    payload: TelegramWebhookRequest,
    service: TelegramServiceDep,
) -> AskResponse:
    return service.handle_webhook(payload)
