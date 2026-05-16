from pydantic import BaseModel


class TelegramMessage(BaseModel):
    chat_id: str
    from_user_id: str
    text: str


class TelegramWebhookRequest(BaseModel):
    message: TelegramMessage


class TelegramWebhookResponse(BaseModel):
    ok: bool
    answer: str
