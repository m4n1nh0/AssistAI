from dataclasses import asdict
from uuid import uuid4

from app.core.config import settings
from app.db.models import AttendanceModel, MessageModel
from app.db.session import SessionLocal
from app.domain.entities import Attendance, Message, Source
from app.domain.enums import Intent
from app.infrastructure.llm_client import LLMClient
from app.infrastructure.qdrant_client import QdrantGateway
from app.infrastructure.repositories.memory import store
from app.rag.intent_classifier import IntentClassifier
from app.rag.loader import load_markdown_documents
from app.rag.retriever import KeywordRetriever
from app.security.input_sanitizer import sanitize_user_message
from app.security.prompt_injection import has_prompt_injection_risk
from app.schemas.ask import AskRequest, AskResponse, SourceResponse


class AssistantService:
    def __init__(self) -> None:
        self.intent_classifier = IntentClassifier()
        self.retriever = KeywordRetriever()
        self.llm = LLMClient()
        self.qdrant = QdrantGateway()

    def answer(self, payload: AskRequest) -> AskResponse:
        payload.message = sanitize_user_message(payload.message)
        attendance = self._get_or_create_attendance(payload)
        intent, confidence = self.intent_classifier.classify(payload.message)

        if has_prompt_injection_risk(payload.message):
            answer = "Não posso seguir instruções que tentem alterar as regras internas do atendimento."
            return self._persist_and_respond(payload, attendance, answer, True, Intent.OUT_OF_SCOPE, 0.95, [])

        if intent == Intent.GREETING:
            answer = "Olá! Como posso ajudar com suporte interno hoje?"
            return self._persist_and_respond(payload, attendance, answer, False, intent, confidence, [])

        if intent == Intent.HUMAN_REQUEST:
            answer = "Entendi. Vou marcar este atendimento para acompanhamento humano."
            return self._persist_and_respond(payload, attendance, answer, False, intent, confidence, [])

        retrieved = self._search_with_qdrant(payload.message)
        reliable_context = [item for item in retrieved if item["score"] >= settings.min_relevance_score]

        if not reliable_context:
            answer = "Não encontrei base suficiente para responder com segurança. Posso encaminhar para atendimento humano."
            return self._persist_and_respond(payload, attendance, answer, True, Intent.OUT_OF_SCOPE, confidence, [])

        context = "\n\n".join(item["payload"].get("chunk_text", "") for item in reliable_context)
        answer = self.llm.generate_answer(payload.message, context)
        sources = [
            Source(
                document_id=item["payload"].get("document_id", ""),
                title=item["payload"].get("title", ""),
                version=item["payload"].get("version", ""),
                score=item["score"],
            )
            for item in reliable_context
        ]
        return self._persist_and_respond(payload, attendance, answer, False, intent, confidence, sources)

    def _search_with_qdrant(self, message: str) -> list[dict]:
        try:
            return self.qdrant.search(message, limit=3)
        except Exception:
            documents = list(store.documents.values()) or load_markdown_documents(settings.knowledge_base_path)
            return [
                {
                    "id": f"{item.document.id}-fallback",
                    "score": item.score,
                    "payload": {
                        "document_id": item.document.id,
                        "title": item.document.title,
                        "version": item.document.version,
                        "chunk_text": item.excerpt,
                    },
                }
                for item in self.retriever.search(message, documents)
            ]

    def _get_or_create_attendance(self, payload: AskRequest) -> Attendance:
        try:
            with SessionLocal() as session:
                attendance_model = (
                    session.query(AttendanceModel)
                    .filter_by(user_id=payload.user_id, channel=payload.channel)
                    .one_or_none()
                )
                if attendance_model is not None:
                    attendance = Attendance(
                        id=attendance_model.id,
                        user_id=attendance_model.user_id,
                        channel=attendance_model.channel,
                        messages=[
                            Message(
                                id=message.id,
                                attendance_id=message.attendance_id,
                                user_message=message.user_message,
                                assistant_answer=message.assistant_answer,
                                fallback=message.fallback,
                                intent=Intent(message.intent),
                                confidence=message.confidence,
                                sources=[Source(**source) for source in (message.sources or [])],
                                created_at=message.created_at,
                            )
                            for message in attendance_model.messages
                        ],
                        created_at=attendance_model.created_at,
                    )
                    store.attendances[attendance.id] = attendance
                    return attendance

                attendance = Attendance(id=f"att-{uuid4()}", user_id=payload.user_id, channel=payload.channel)
                store.attendances[attendance.id] = attendance
                session.add(
                    AttendanceModel(id=attendance.id, user_id=attendance.user_id, channel=attendance.channel)
                )
                session.commit()
                return attendance
        except Exception:
            attendance = next(
                (
                    attendance
                    for attendance in store.attendances.values()
                    if attendance.user_id == payload.user_id and attendance.channel == payload.channel
                ),
                None,
            )
            if attendance:
                return attendance

            attendance = Attendance(id=f"att-{uuid4()}", user_id=payload.user_id, channel=payload.channel)
            store.attendances[attendance.id] = attendance
            return attendance

    def _persist_message(self, message: Message) -> None:
        try:
            with SessionLocal() as session:
                session.add(
                    MessageModel(
                        id=message.id,
                        attendance_id=message.attendance_id,
                        user_message=message.user_message,
                        assistant_answer=message.assistant_answer,
                        fallback=message.fallback,
                        intent=message.intent.value,
                        confidence=message.confidence,
                        sources=[asdict(source) for source in message.sources],
                    )
                )
                session.commit()
        except Exception:
            pass

    def _persist_and_respond(
        self,
        payload: AskRequest,
        attendance: Attendance,
        answer: str,
        fallback: bool,
        intent: Intent,
        confidence: float,
        sources: list[Source],
    ) -> AskResponse:
        message = Message(
            id=f"msg-{uuid4()}",
            attendance_id=attendance.id,
            user_message=payload.message,
            assistant_answer=answer,
            fallback=fallback,
            intent=intent,
            confidence=confidence,
            sources=sources,
        )
        attendance.messages.append(message)
        store.messages[message.id] = message
        self._persist_message(message)

        return AskResponse(
            answer=answer,
            fallback=fallback,
            intent=intent,
            confidence=confidence,
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
            message_id=message.id,
        )


def get_assistant_service() -> AssistantService:
    return AssistantService()
