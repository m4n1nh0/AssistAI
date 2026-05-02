from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_assistant_service
from app.application.services.assistant_service import AssistantService
from app.domain.contracts import AskRequest, AskResponse

router = APIRouter()
AssistantServiceDep = Annotated[AssistantService, Depends(get_assistant_service)]


@router.post("/ask", response_model=AskResponse)
def ask(
    payload: AskRequest,
    service: AssistantServiceDep,
) -> AskResponse:
    return service.ask(payload)
