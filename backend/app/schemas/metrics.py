from pydantic import BaseModel


class MetricsResponse(BaseModel):
    total_attendances: int
    total_messages: int
    fallback_rate: float
    useful_feedback_rate: float | None
    top_intents: dict[str, int]
