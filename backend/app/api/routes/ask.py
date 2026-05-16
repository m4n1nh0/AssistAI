from fastapi import APIRouter, Depends

from app.application.services.assistant_service import AssistantService, get_assistant_service
from app.schemas.ask import AskRequest, AskResponse

router = APIRouter()


@router.post("/ask", response_model=AskResponse)
def ask_assistant(
    payload: AskRequest,
    service: AssistantService = Depends(get_assistant_service),
) -> AskResponse:
    return service.answer(payload)
