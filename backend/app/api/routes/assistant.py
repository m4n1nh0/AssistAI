from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_assistant_service
from app.application.services.assistant_service import AssistantService
from app.domain.contracts import AskRequest as DomainAskRequest
from app.domain.enums import Channel as DomainChannel
from app.schemas.assistant import AskRequest, AskResponse, SourceResponse

router = APIRouter(tags=["assistant"])
AssistantServiceDep = Annotated[AssistantService, Depends(get_assistant_service)]

@router.post("/ask", response_model=AskResponse)
async def ask_assistant(
    payload: AskRequest,
    service: AssistantServiceDep,
) -> AskResponse:
    """
    Endpoint oficial de pergunta e resposta do assistente.
    Usado por Web, Telegram e integrações futuras.
    """

    user_id = payload.user.id if payload.user and payload.user.id else "anonymous"
    internal_payload = DomainAskRequest(
        user_id=user_id,
        channel=DomainChannel(payload.channel),
        message=payload.question,
        conversation_id=payload.conversation_id,
    )
    internal_response = service.ask(internal_payload)

    return AskResponse(
        answer=internal_response.answer,
        status="fallback" if internal_response.fallback else "answered",
        conversation_id=internal_response.attendance_id,
        message_id=internal_response.message_id,
        sources=[
            SourceResponse(
                document_id=source.document_id,
                title=source.title,
                chunk_id=source.chunk_id,
                version=source.version,
                score=source.score,
            )
            for source in internal_response.sources
        ],
        usage=None,
        metadata={
            "channel": payload.channel,
            "confidence": internal_response.confidence,
            "fallback": internal_response.fallback,
        },
    )
