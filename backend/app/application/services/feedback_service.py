from datetime import datetime, timezone
from app.domain.contracts import FeedbackRequest, FeedbackResponse
from app.domain.models import Feedback, new_id
from app.infrastructure.repositories.mysql import MySQLRepository


class FeedbackService:
    def __init__(self, repository: MySQLRepository) -> None:
        self.repository = repository

    def register(self, payload: FeedbackRequest) -> FeedbackResponse:
        now = datetime.now(timezone.utc)
        feedback = Feedback(
            id=new_id("fbk"),
            message_id=payload.message_id,
            useful=payload.useful,
            comment=payload.comment,
            created_at=now
        )
        self.repository.add_feedback(feedback)
        
        return FeedbackResponse(
            feedback_id=feedback.id,
            message_id=feedback.message_id,
            useful=feedback.useful,
            created_at=feedback.created_at,
        )

