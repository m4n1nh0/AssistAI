from app.domain.contracts import FeedbackRequest, FeedbackResponse
from app.infrastructure.database.mysql import MySqlAuditStore
from app.infrastructure.repositories.memory import InMemoryRepository


class FeedbackService:
    def __init__(
        self,
        repository: InMemoryRepository,
        audit_store: MySqlAuditStore | None = None,
    ) -> None:
        self.repository = repository
        self.audit_store = audit_store

    def register(self, payload: FeedbackRequest) -> FeedbackResponse:
        feedback = self.repository.add_feedback(
            message_id=payload.message_id,
            useful=payload.useful,
            comment=payload.comment,
        )
        if self.audit_store:
            self.audit_store.persist_feedback(feedback)
        return FeedbackResponse(
            feedback_id=feedback.id,
            message_id=feedback.message_id,
            useful=feedback.useful,
            created_at=feedback.created_at,
        )
