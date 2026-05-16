from pydantic import BaseModel, Field


class FeedbackRequest(BaseModel):
    message_id: str = Field(min_length=1)
    useful: bool
    comment: str | None = Field(default=None, max_length=1000)


class FeedbackResponse(BaseModel):
    feedback_id: str
    message_id: str
    useful: bool
