from uuid import uuid4

from app.db.models import FeedbackModel
from app.db.session import SessionLocal
from app.infrastructure.repositories.memory import store
from app.schemas.feedback import FeedbackRequest, FeedbackResponse


class FeedbackService:
    def register(self, payload: FeedbackRequest) -> FeedbackResponse:
        feedback_id = f"fb-{uuid4()}"
        try:
            with SessionLocal() as session:
                session.add(
                    FeedbackModel(
                        id=feedback_id,
                        message_id=payload.message_id,
                        useful=payload.useful,
                        comment=payload.comment,
                    )
                )
                session.commit()
        except Exception:
            pass

        store.feedbacks[feedback_id] = payload.model_dump()
        return FeedbackResponse(
            feedback_id=feedback_id,
            message_id=payload.message_id,
            useful=payload.useful,
        )


def get_feedback_service() -> FeedbackService:
    return FeedbackService()
