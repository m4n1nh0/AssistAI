from app.domain.contracts import FeedbackRequest, FeedbackResponse
from app.infrastructure.repositories.memory import InMemoryRepository


class FeedbackService:
    def __init__(self, repository: InMemoryRepository) -> None:
        self.repository = repository

    def register(self, payload: FeedbackRequest) -> FeedbackResponse:
        feedback = self.repository.add_feedback(
            message_id=payload.message_id,
            useful=payload.useful,
            comment=payload.comment,
        )
        return FeedbackResponse(
            feedback_id=feedback.id,
            message_id=feedback.message_id,
            useful=feedback.useful,
            created_at=feedback.created_at,
        )

