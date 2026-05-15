import re
from time import perf_counter

from app.core.config import Settings
from app.domain.contracts import AskRequest, AskResponse, SourceResponse
from app.domain.enums import Intent
from app.domain.models import AiLog, MessageRecord, Source, new_id, utc_now
from app.infrastructure.llm.fake_llm import FakeLLMGateway
from app.infrastructure.mcp.simulated_tools import SimulatedToolRegistry
from app.infrastructure.rag.simple_retriever import RetrievalResult, SimpleRetriever
from app.infrastructure.repositories.memory import InMemoryRepository


class AssistantService:
    def __init__(
        self,
        repository: InMemoryRepository,
        retriever: SimpleRetriever,
        llm_gateway: FakeLLMGateway,
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
        attendance = self.repository.create_attendance(user.id, request.channel)

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
        elif intent == Intent.TICKET_STATUS:
            answer, confidence = self._answer_ticket_status(message)
            fallback = False
        elif fallback:
            answer = (
                "Nao encontrei base suficiente para responder com seguranca. "
                "Posso encaminhar este atendimento para um humano."
            )
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
            request_id=request.request_id,
            user_id=request.user_id,
            channel=request.channel,
            answer=answer,
            fallback=fallback,
            handoff_required=attendance.escalated,
            intent=intent,
            confidence=round(confidence, 4),
            sources=[
                SourceResponse(
                    document_id=source.document_id,
                    title=source.title,
                    version=source.version,
                    score=source.score,
                )
                for source in sources
            ],
            attendance_id=attendance.id,
            message_id=message_record.id,
            generated_at=utc_now(),
        )

    def _answer_ticket_status(self, message: str) -> tuple[str, float]:
        ticket_id = _extract_ticket_id(message)
        if not ticket_id:
            return (
                "Informe o numero do chamado no formato CHM-12345 para consulta.",
                0.75,
            )

        result = self.tools.ticket_status(ticket_id)
        output = result.output_payload
        answer = (
            f"O chamado {output.get('ticket_id', ticket_id)} esta "
            f"{output.get('status', 'indisponivel')}. "
            f"Ultima atualizacao: {output.get('last_update', 'sem registro')}."
        )
        return answer, 0.9 if result.success else 0.3


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


def _extract_ticket_id(message: str) -> str | None:
    match = re.search(r"\b(CHM-\d+)\b", message, flags=re.IGNORECASE)
    return match.group(1).upper() if match else None


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
                title=document.title,
                version=document.version,
                score=context.score,
            )
        )
    return sources
