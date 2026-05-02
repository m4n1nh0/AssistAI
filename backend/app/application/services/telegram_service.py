from app.application.services.assistant_service import AssistantService
from app.domain.contracts import AskRequest, AskResponse, TelegramWebhookRequest
from app.domain.enums import Channel


class TelegramService:
    def __init__(self, assistant_service: AssistantService) -> None:
        self.assistant_service = assistant_service

    def handle_webhook(self, payload: TelegramWebhookRequest) -> AskResponse:
        return self.assistant_service.ask(
            AskRequest(
                user_id=payload.user_id,
                channel=Channel.TELEGRAM,
                message=payload.message,
            )
        )

