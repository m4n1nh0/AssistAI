from uuid import uuid4

from app.ai.intent import classify_intent
from app.ai.llm_gateway import llm_gateway
from app.ai.retriever import retriever
from app.core.settings import settings
from app.domain.models import Channel, Intent, KnowledgeDocument, MessageRecord
from app.infrastructure.mcp_simulated import mcp_client
from app.infrastructure.repositories import repository


class AssistantService:
    def ask(self, user_id: str, channel: Channel, message: str) -> dict:
        attendance = repository.get_or_create_attendance(user_id=user_id, channel=channel)
        intent, confidence = classify_intent(message)

        repository.add_message(
            attendance,
            MessageRecord(id=f"msg-{uuid4().hex[:8]}", role="user", content=message, intent=intent),
        )

        if intent == Intent.GREETING:
            answer = "Ola! Posso ajudar com abertura de chamado, reset de senha, prioridade ou status de atendimento."
            sources = []
            fallback = False
        elif intent == Intent.HUMAN:
            repository.mark_handoff(attendance)
            answer = "Entendi. Vou marcar este atendimento para acao humana."
            sources = []
            fallback = False
        elif intent == Intent.TICKET_STATUS:
            ticket = mcp_client.get_ticket_status(message) if settings.enable_mcp_simulated else None
            if ticket:
                answer = (
                    f"O chamado {ticket['ticket_id']} esta {ticket['status']}. "
                    f"Ultima atualizacao: {ticket['last_update']}"
                )
                sources = []
                fallback = False
            else:
                answer, sources, fallback = self._answer_with_rag(message)
        else:
            answer, sources, fallback = self._answer_with_rag(message)
            if fallback:
                repository.mark_handoff(attendance)

        assistant_message = repository.add_message(
            attendance,
            MessageRecord(
                id=f"msg-{uuid4().hex[:8]}",
                role="assistant",
                content=answer,
                sources=sources,
                fallback=fallback,
                intent=intent,
            ),
        )

        return {
            "answer": answer,
            "fallback": fallback,
            "intent": intent.value,
            "confidence": confidence,
            "sources": [source.__dict__ for source in sources],
            "attendance_id": attendance.id,
            "message_id": assistant_message.id,
            "needs_human": attendance.needs_human,
            "suggested_actions": self._suggested_actions(intent, fallback),
        }

    def _answer_with_rag(self, message: str) -> tuple[str, list, bool]:
        contexts = [context for context in retriever.search(message) if context.score >= settings.min_relevance_score]

        if not contexts:
            return (
                "Nao encontrei base suficiente para responder com seguranca. Posso encaminhar para atendimento humano.",
                [],
                True,
            )

        answer = llm_gateway.generate_answer(message, contexts)
        return answer, retriever.to_sources(contexts), False

    @staticmethod
    def _suggested_actions(intent: Intent, fallback: bool) -> list[str]:
        if fallback or intent == Intent.HUMAN:
            return ["acionar humano", "registrar lacuna da base"]
        if intent == Intent.TICKET_STATUS:
            return ["consultar chamado", "atualizar usuario"]
        return ["avaliar resposta", "consultar fontes"]

    def create_document(self, payload: dict) -> KnowledgeDocument:
        document = KnowledgeDocument(id=f"doc-{uuid4().hex[:8]}", **payload)
        repository.add_document(document)
        retriever.add_document(document)
        return document


assistant_service = AssistantService()
