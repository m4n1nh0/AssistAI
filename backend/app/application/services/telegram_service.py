from app.application.services.assistant_service import AssistantService
from app.domain.enums import Channel
from app.infrastructure.telegram_client import TelegramClient
from app.schemas.ask import AskRequest
from app.schemas.telegram import TelegramWebhookRequest, TelegramWebhookResponse


class TelegramService:
    def __init__(self) -> None:
        self.assistant = AssistantService()
        self.telegram = TelegramClient()

    def handle_webhook(self, payload: TelegramWebhookRequest) -> TelegramWebhookResponse:
        response = self.assistant.answer(
            AskRequest(
                user_id=payload.message.from_user_id,
                channel=Channel.TELEGRAM,
                message=payload.message.text,
            )
        )
        self.telegram.send_message(payload.message.chat_id, response.answer)
        return TelegramWebhookResponse(ok=True, answer=response.answer)


def get_telegram_service() -> TelegramService:
    return TelegramService()
