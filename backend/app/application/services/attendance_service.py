from app.db.models import AttendanceModel
from app.db.session import SessionLocal
from app.infrastructure.repositories.memory import store
from app.schemas.attendance import (
    AttendanceDetailResponse,
    AttendanceListResponse,
    AttendanceMessageResponse,
    AttendanceSummaryResponse,
)
from app.schemas.ask import SourceResponse


class AttendanceService:
    def list(self) -> AttendanceListResponse:
        try:
            with SessionLocal() as session:
                attendances = session.query(AttendanceModel).all()
                return AttendanceListResponse(
                    items=[
                        AttendanceSummaryResponse(
                            id=attendance.id,
                            user_id=attendance.user_id,
                            channel=attendance.channel,
                            total_messages=len(attendance.messages),
                            created_at=attendance.created_at,
                        )
                        for attendance in attendances
                    ]
                )
        except Exception:
            return AttendanceListResponse(
                items=[
                    AttendanceSummaryResponse(
                        id=attendance.id,
                        user_id=attendance.user_id,
                        channel=attendance.channel,
                        total_messages=len(attendance.messages),
                        created_at=attendance.created_at,
                    )
                    for attendance in store.attendances.values()
                ]
            )

    def get(self, attendance_id: str) -> AttendanceDetailResponse | None:
        try:
            with SessionLocal() as session:
                attendance = session.query(AttendanceModel).filter_by(id=attendance_id).one_or_none()
                if attendance is None:
                    return None
                return AttendanceDetailResponse(
                    id=attendance.id,
                    user_id=attendance.user_id,
                    channel=attendance.channel,
                    created_at=attendance.created_at,
                    messages=[
                        AttendanceMessageResponse(
                            id=message.id,
                            user_message=message.user_message,
                            assistant_answer=message.assistant_answer,
                            fallback=message.fallback,
                            intent=message.intent,
                            confidence=message.confidence,
                            sources=[
                                SourceResponse(
                                    document_id=source.get("document_id", ""),
                                    title=source.get("title", ""),
                                    version=source.get("version", ""),
                                    score=source.get("score", 0.0),
                                )
                                for source in (message.sources or [])
                            ],
                            created_at=message.created_at,
                        )
                        for message in attendance.messages
                    ],
                )
        except Exception:
            attendance = store.attendances.get(attendance_id)
            if attendance is None:
                return None
            return AttendanceDetailResponse(
                id=attendance.id,
                user_id=attendance.user_id,
                channel=attendance.channel,
                created_at=attendance.created_at,
                messages=[
                    AttendanceMessageResponse(
                        id=message.id,
                        user_message=message.user_message,
                        assistant_answer=message.assistant_answer,
                        fallback=message.fallback,
                        intent=message.intent,
                        confidence=message.confidence,
                        sources=[
                            SourceResponse(
                                document_id=source.document_id,
                                title=source.title,
                                version=source.version,
                                score=source.score,
                            )
                            for source in message.sources
                        ],
                        created_at=message.created_at,
                    )
                    for message in attendance.messages
                ],
            )


def get_attendance_service() -> AttendanceService:
    return AttendanceService()
