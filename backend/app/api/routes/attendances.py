from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_repository
from app.domain.contracts import (
    AttendanceDetailResponse,
    AttendanceListItem,
    MessageResponse,
    SourceResponse,
)
from app.infrastructure.repositories.memory import InMemoryRepository

router = APIRouter()
RepositoryDep = Annotated[InMemoryRepository, Depends(get_repository)]


@router.get("/attendances", response_model=list[AttendanceListItem])
def list_attendances(
    repository: RepositoryDep,
) -> list[AttendanceListItem]:
    message_counts = repository.count_messages_by_attendance()
    return [
        AttendanceListItem(
            attendance_id=attendance.id,
            user_id=attendance.user_id,
            channel=attendance.channel,
            escalated=attendance.escalated,
            started_at=attendance.started_at,
            message_count=message_counts.get(attendance.id, 0),
        )
        for attendance in repository.list_attendances()
    ]


@router.get("/attendances/{attendance_id}", response_model=AttendanceDetailResponse)
def get_attendance(
    attendance_id: str,
    repository: RepositoryDep,
) -> AttendanceDetailResponse:
    attendance = repository.get_attendance(attendance_id)
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Atendimento nao encontrado.",
        )

    messages = repository.list_messages_by_attendance(attendance.id)
    return AttendanceDetailResponse(
        attendance_id=attendance.id,
        user_id=attendance.user_id,
        channel=attendance.channel,
        escalated=attendance.escalated,
        started_at=attendance.started_at,
        messages=[
            MessageResponse(
                message_id=message.id,
                user_message=message.user_message,
                assistant_answer=message.assistant_answer,
                fallback=message.fallback,
                intent=message.intent,
                confidence=message.confidence,
                sources=[
                    SourceResponse(
                        document_id=source.document_id,
                        chunk_id=source.chunk_id,
                        title=source.title,
                        version=source.version,
                        score=source.score,
                    )
                    for source in message.sources
                ],
                created_at=message.created_at,
            )
            for message in messages
        ],
    )
