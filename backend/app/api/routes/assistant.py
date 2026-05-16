from fastapi import APIRouter

from app.schemas.assistant import AskRequest, AskResponse

router = APIRouter(tags=["assistant"])

@router.post("/ask", response_model=AskResponse)
async def ask_assistant(payload: AskRequest) -> AskResponse:
    """
    Endpoint oficial de pergunta e resposta do assistente.
    Usado por Web, Telegram e integrações futuras.
    """

    # Mock inicial para validar contrato na S1-01.
    # Na S1-10 esse trecho será conectado à busca semântica/Qdrant.
    return AskResponse(
        answer=(
            "Contrato validado com sucesso." 
            "A integração com RAG será adicionada nas próximas tarefas."
        ),
        status="answered",
        conversation_id=payload.conversation_id or "conv_mock",
        message_id="msg_mock",
        sources=[],
        usage=None,
        metadata={
            "channel": payload.channel,
            "rag_enabled": False,
        },
    )