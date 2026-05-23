import re
from time import perf_counter

from app.core.config import Settings
from app.domain.contracts import AskRequest, AskResponse, SourceResponse
from app.domain.enums import Intent
from app.domain.models import AiLog, MessageRecord, Source, new_id
from app.infrastructure.llm.gateway import LLMGateway
from app.infrastructure.llm.prompt import FALLBACK_ANSWER
from app.infrastructure.mcp.simulated_tools import SimulatedToolRegistry
from app.infrastructure.rag.simple_retriever import RetrievalResult, SimpleRetriever
from app.infrastructure.repositories.memory import InMemoryRepository


class AssistantService:
    def __init__(
        self,
        repository: InMemoryRepository,
        retriever: SimpleRetriever,
        llm_gateway: LLMGateway,
        tools: SimulatedToolRegistry,
        settings: Settings,
    ) -> None:
        self.repository = repository
        self.retriever = retriever
        self.llm_gateway = llm_gateway
        self.tools = tools
        self.settings = settings

    def ask(self, request: AskRequest) -> AskResponse:
        started = perf_counter()
        message = _sanitize(request.message, max_chars=self.settings.max_message_chars)
        intent = _classify_intent(message)

        user = self.repository.find_or_create_user(request.user_id, request.channel)
        attendance = self.repository.find_or_create_attendance(
            user.id,
            request.channel,
            request.conversation_id,
        )

        contexts = self.retriever.search(message)
        contexts = [
            context
            for context in contexts
            if context.score >= self.settings.min_relevance_score
        ]

        fallback = not contexts
        answer = ""
        confidence = contexts[0].score if contexts else 0.0

        if intent == Intent.HUMAN_REQUEST:
            fallback = True
            confidence = 1.0
            answer = (
                "Entendi que voce precisa de atendimento humano. "
                "Marquei este atendimento para escalonamento."
            )
            self.repository.mark_attendance_escalated(
                attendance.id,
                reason="Usuario solicitou atendimento humano.",
            )
        elif fallback:
            answer = FALLBACK_ANSWER
            self.repository.mark_attendance_escalated(
                attendance.id,
                reason="Contexto insuficiente para resposta.",
            )
        else:
            answer = self.llm_gateway.generate(message, contexts)

        sources = _to_sources(contexts, self.repository)
        message_record = MessageRecord(
            id=new_id("msg"),
            attendance_id=attendance.id,
            user_message=message,
            assistant_answer=answer,
            fallback=fallback,
            intent=intent,
            confidence=round(confidence, 4),
            sources=sources,
        )
        self.repository.add_message(message_record)

        elapsed_ms = round((perf_counter() - started) * 1000)
        self.repository.add_ai_log(
            AiLog(
                id=new_id("ailog"),
                message_id=message_record.id,
                intent=intent,
                relevance_score=round(confidence, 4),
                fallback=fallback,
                source_document_ids=[source.document_id for source in sources],
                elapsed_ms=elapsed_ms,
            )
        )

        return AskResponse(
            answer=answer,
            fallback=fallback,
            intent=intent,
            confidence=round(confidence, 4),
            sources=[
                SourceResponse(
                    document_id=source.document_id,
                    chunk_id=source.chunk_id,
                    title=source.title,
                    version=source.version,
                    score=source.score,
                )
                for source in sources
            ],
            attendance_id=attendance.id,
            message_id=message_record.id,
        )

def _sanitize(message: str, max_chars: int) -> str:
    compact = " ".join(message.strip().split())
    return compact[:max_chars]


def _classify_intent(message: str) -> Intent:
    lower = message.lower()
    if any(term in lower for term in ["humano", "atendente", "pessoa"]):
        return Intent.HUMAN_REQUEST
    if re.search(r"\bchm-\d+\b", lower):
        return Intent.TICKET_STATUS
    if lower in {"oi", "ola", "olá", "bom dia", "boa tarde", "boa noite"}:
        return Intent.GREETING
    return Intent.PROCEDURE


def _to_sources(
    contexts: list[RetrievalResult],
    repository: InMemoryRepository,
) -> list[Source]:
    sources: list[Source] = []
    for context in contexts:
        document = repository.get_document(context.chunk.document_id)
        if not document:
            continue
        sources.append(
            Source(
                document_id=document.id,
                chunk_id=context.chunk.id,
                title=document.title,
                version=document.version,
                score=context.score,
            )
        )
    return sources
