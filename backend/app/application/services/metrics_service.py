from collections import Counter

from app.db.models import AttendanceModel, FeedbackModel, MessageModel
from app.db.session import SessionLocal
from app.infrastructure.repositories.memory import store
from app.schemas.metrics import MetricsResponse


class MetricsService:
    def get_summary(self) -> MetricsResponse:
        try:
            with SessionLocal() as session:
                total_attendances = session.query(AttendanceModel).count()
                messages = session.query(MessageModel).all()
                feedbacks = session.query(FeedbackModel).all()

                fallback_count = sum(1 for message in messages if message.fallback)
                useful_feedbacks = [feedback for feedback in feedbacks if feedback.useful]

                return MetricsResponse(
                    total_attendances=total_attendances,
                    total_messages=len(messages),
                    fallback_rate=round(fallback_count / len(messages), 2) if messages else 0,
                    useful_feedback_rate=round(len(useful_feedbacks) / len(feedbacks), 2) if feedbacks else None,
                    top_intents=dict(Counter(message.intent for message in messages)),
                )
        except Exception:
            messages = list(store.messages.values())
            feedbacks = list(store.feedbacks.values())
            fallback_count = sum(1 for message in messages if message.fallback)
            useful_feedbacks = [feedback for feedback in feedbacks if feedback.get("useful") is True]

            return MetricsResponse(
                total_attendances=len(store.attendances),
                total_messages=len(messages),
                fallback_rate=round(fallback_count / len(messages), 2) if messages else 0,
                useful_feedback_rate=round(len(useful_feedbacks) / len(feedbacks), 2) if feedbacks else None,
                top_intents=dict(Counter(message.intent.value for message in messages)),
            )


def get_metrics_service() -> MetricsService:
    return MetricsService()
