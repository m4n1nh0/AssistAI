from fastapi import APIRouter, Depends

from app.application.services.telegram_service import TelegramService, get_telegram_service
from app.schemas.telegram import TelegramWebhookRequest, TelegramWebhookResponse

router = APIRouter()


@router.post("/telegram/webhook", response_model=TelegramWebhookResponse)
def receive_webhook(
    payload: TelegramWebhookRequest,
    service: TelegramService = Depends(get_telegram_service),
) -> TelegramWebhookResponse:
    return service.handle_webhook(payload)
