from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_feedback_service
from app.application.services.feedback_service import FeedbackService
from app.domain.contracts import FeedbackRequest, FeedbackResponse

router = APIRouter()
FeedbackServiceDep = Annotated[FeedbackService, Depends(get_feedback_service)]


@router.post("/feedback", response_model=FeedbackResponse)
async def register_feedback(
    payload: FeedbackRequest,
    service: FeedbackServiceDep,
) -> FeedbackResponse:
    try:
        return service.register(payload)
    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mensagem nao encontrada.",
        ) from exc
