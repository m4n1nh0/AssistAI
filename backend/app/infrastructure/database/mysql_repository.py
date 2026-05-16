from __future__ import annotations

import json
import logging
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session, sessionmaker

from app.domain.contracts import DocumentCreateRequest
from app.domain.enums import Channel, DocumentStatus
from app.domain.models import (
    AiLog,
    Attendance,
    DocumentChunk,
    Feedback,
    Handoff,
    KnowledgeDocument,
    MessageRecord,
    ToolCall,
    User,
    new_id,
)
from app.domain.protocols import Repository
from app.infrastructure.database.models import (
    AiLogModel,
    AttendanceModel,
    DocumentChunkModel,
    DocumentModel,
    FeedbackModel,
    HandoffModel,
    MessageModel,
    ToolCallModel,
    UserModel,
)

logger = logging.getLogger(__name__)


class MySqlRepository(Repository):
    def __init__(self, session_maker: sessionmaker[Session]) -> None:
        self._session_maker = session_maker

    def _session(self) -> Session:
        return self._session_maker()

    # ------------------------------------------------------------------
    # Users
    # ------------------------------------------------------------------

    def find_or_create_user(
        self, external_id: str, channel: Channel
    ) -> User:
        with self._session() as session:
            model = (
                session.query(UserModel)
                .filter_by(external_id=external_id, channel=channel.value)
                .first()
            )
            if model:
                return _user_from_model(model)

            model = UserModel(
                id=new_id("usr"),
                external_id=external_id,
                channel=channel.value,
            )
            session.add(model)
            session.commit()
            return _user_from_model(model)

    # ------------------------------------------------------------------
    # Attendances
    # ------------------------------------------------------------------

    def create_attendance(
        self, user_id: str, channel: Channel
    ) -> Attendance:
        model = AttendanceModel(
            id=new_id("att"),
            user_id=user_id,
            channel=channel.value,
        )
        with self._session() as session:
            session.add(model)
            session.commit()
            return _attendance_from_model(model)

    def mark_attendance_escalated(
        self, attendance_id: str, reason: str
    ) -> Handoff:
        with self._session() as session:
            att = (
                session.query(AttendanceModel)
                .filter_by(id=attendance_id)
                .first()
            )
            if att:
                att.escalated = True

            handoff = HandoffModel(
                id=new_id("hnd"),
                attendance_id=attendance_id,
                reason=reason,
            )
            session.add(handoff)
            session.commit()
            return Handoff(
                id=handoff.id,
                attendance_id=handoff.attendance_id,
                reason=handoff.reason,
                created_at=handoff.created_at,
            )

    # ------------------------------------------------------------------
    # Messages
    # ------------------------------------------------------------------

    def add_message(self, message: MessageRecord) -> MessageRecord:
        model = MessageModel(
            id=message.id,
            attendance_id=message.attendance_id,
            user_message=message.user_message,
            assistant_answer=message.assistant_answer,
            fallback=message.fallback,
            intent=message.intent.value,
            confidence=message.confidence,
            created_at=message.created_at,
        )
        with self._session() as session:
            session.add(model)
            session.commit()
        return message

    # ------------------------------------------------------------------
    # Feedback
    # ------------------------------------------------------------------

    def add_feedback(
        self, message_id: str, useful: bool, comment: str | None
    ) -> Feedback:
        model = FeedbackModel(
            id=new_id("fbk"),
            message_id=message_id,
            useful=useful,
            comment=comment,
        )
        with self._session() as session:
            session.add(model)
            session.commit()
            return Feedback(
                id=model.id,
                message_id=model.message_id,
                useful=model.useful,
                comment=model.comment,
                created_at=model.created_at,
            )

    # ------------------------------------------------------------------
    # AI Logs
    # ------------------------------------------------------------------

    def add_ai_log(self, log: AiLog) -> AiLog:
        model = AiLogModel(
            id=log.id,
            message_id=log.message_id,
            intent=log.intent.value,
            relevance_score=log.relevance_score,
            fallback=log.fallback,
            source_document_ids=json.dumps(log.source_document_ids),
            elapsed_ms=log.elapsed_ms,
        )
        with self._session() as session:
            session.add(model)
            session.commit()
        return log

    # ------------------------------------------------------------------
    # Tool calls
    # ------------------------------------------------------------------

    def add_tool_call(self, tool_call: ToolCall) -> ToolCall:
        model = ToolCallModel(
            id=tool_call.id,
            message_id=tool_call.message_id,
            tool_name=tool_call.tool_name,
            input_payload=json.dumps(tool_call.input_payload),
            output_payload=json.dumps(tool_call.output_payload),
            success=tool_call.success,
        )
        with self._session() as session:
            session.add(model)
            session.commit()
        return tool_call

    # ------------------------------------------------------------------
    # Documents
    # ------------------------------------------------------------------

    def seed_default_documents(self) -> None:
        with self._session() as session:
            existing = session.query(DocumentModel).count()
            if existing > 0:
                return

        defaults = [
            DocumentCreateRequest(
                title="Procedimento de abertura de chamado",
                category="help-desk",
                content=(
                    "Para abrir um chamado, acesse o portal de suporte interno, "
                    "escolha a categoria do problema, descreva o impacto e anexe "
                    "evidencias quando existirem. Ao final, acompanhe pelo numero "
                    "de protocolo gerado."
                ),
                tags=["chamado", "portal", "suporte"],
            ),
            DocumentCreateRequest(
                title="Reset de senha",
                category="acesso",
                content=(
                    "Para solicitar reset de senha, use a opcao de recuperacao no "
                    "portal corporativo. Se nao conseguir concluir, abra um chamado "
                    "na categoria acesso e informe seu identificador de usuario."
                ),
                tags=["senha", "acesso", "login"],
            ),
            DocumentCreateRequest(
                title="Consulta de status de chamado",
                category="help-desk",
                content=(
                    "O status de um chamado pode ser consultado pelo numero de "
                    "protocolo no portal de suporte. Chamados em andamento mostram "
                    "a ultima atualizacao registrada pela equipe responsavel."
                ),
                tags=["status", "chamado", "protocolo"],
            ),
            DocumentCreateRequest(
                title="Atendimento humano e fallback",
                category="governanca",
                content=(
                    "Quando o usuario solicitar atendimento humano ou quando nao "
                    "houver base suficiente para resposta, o atendimento deve ser "
                    "marcado para escalonamento."
                ),
                tags=["humano", "escalonamento", "fallback"],
            ),
        ]
        for payload in defaults:
            self.create_document(payload)

    def create_document(
        self, payload: DocumentCreateRequest
    ) -> KnowledgeDocument:
        doc_id = new_id("doc")
        model = DocumentModel(
            id=doc_id,
            title=payload.title,
            category=payload.category,
            channel=payload.channel,
            version=payload.version,
            status=payload.status.value,
            source=payload.source,
            owner=payload.owner,
            sensitivity=payload.sensitivity,
            content=payload.content,
        )
        with self._session() as session:
            session.add(model)
            self._replace_chunks(session, doc_id, payload.content)
            session.commit()

        return self.get_document(doc_id)

    def list_documents(self) -> list[KnowledgeDocument]:
        with self._session() as session:
            models = (
                session.query(DocumentModel)
                .order_by(DocumentModel.updated_at.desc())
                .all()
            )
            return [_doc_from_model(m) for m in models]

    def reindex_documents(self) -> tuple[int, int]:
        with self._session() as session:
            docs = session.query(DocumentModel).all()
            session.query(DocumentChunkModel).delete()
            doc_count = len(docs)
            chunk_count = 0
            for doc in docs:
                chunks = self._replace_chunks(
                    session, doc.id, doc.content
                )
                chunk_count += chunks
            session.commit()
            return doc_count, chunk_count

    def list_active_chunks(self) -> list[DocumentChunk]:
        with self._session() as session:
            models = (
                session.query(DocumentChunkModel)
                .join(
                    DocumentModel,
                    DocumentChunkModel.document_id == DocumentModel.id,
                )
                .filter(DocumentModel.status == "active")
                .all()
            )
            return [
                DocumentChunk(
                    id=m.id,
                    document_id=m.document_id,
                    content=m.content,
                    metadata={
                        "chunk_index": str(m.chunk_index),
                    },
                )
                for m in models
            ]

    def get_document(
        self, document_id: str
    ) -> KnowledgeDocument | None:
        with self._session() as session:
            model = (
                session.query(DocumentModel)
                .filter_by(id=document_id)
                .first()
            )
            return _doc_from_model(model) if model else None

    def _replace_chunks(
        self, session: Session, document_id: str, content: str
    ) -> int:
        session.query(DocumentChunkModel).filter_by(
            document_id=document_id
        ).delete()
        words = content.split()
        max_words = 120
        chunks = [
            " ".join(words[i : i + max_words])
            for i in range(0, len(words), max_words)
        ]
        for index, chunk_content in enumerate(chunks, start=1):
            session.add(
                DocumentChunkModel(
                    id=new_id("chk"),
                    document_id=document_id,
                    content=chunk_content,
                    chunk_index=index,
                )
            )
        return len(chunks)

    # ------------------------------------------------------------------
    # Attendances (list / get)
    # ------------------------------------------------------------------

    def list_attendances(self) -> list[Attendance]:
        with self._session() as session:
            models = (
                session.query(AttendanceModel)
                .order_by(AttendanceModel.started_at.desc())
                .all()
            )
            return [_attendance_from_model(m) for m in models]

    def get_attendance(
        self, attendance_id: str
    ) -> Attendance | None:
        with self._session() as session:
            model = (
                session.query(AttendanceModel)
                .filter_by(id=attendance_id)
                .first()
            )
            return _attendance_from_model(model) if model else None

    def list_messages_by_attendance(
        self, attendance_id: str
    ) -> list[MessageRecord]:
        with self._session() as session:
            models = (
                session.query(MessageModel)
                .filter_by(attendance_id=attendance_id)
                .order_by(MessageModel.created_at)
                .all()
            )
            return [_msg_from_model(m) for m in models]

    def count_messages_by_attendance(self) -> dict[str, int]:
        with self._session() as session:
            rows = (
                session.query(
                    MessageModel.attendance_id,
                    func.count(MessageModel.id),
                )
                .group_by(MessageModel.attendance_id)
                .all()
            )
            return {row[0]: row[1] for row in rows}

    def get_feedback_by_message(
        self, message_id: str
    ) -> list[Feedback]:
        with self._session() as session:
            models = (
                session.query(FeedbackModel)
                .filter_by(message_id=message_id)
                .all()
            )
            return [
                Feedback(
                    id=m.id,
                    message_id=m.message_id,
                    useful=m.useful,
                    comment=m.comment,
                    created_at=m.created_at,
                )
                for m in models
            ]

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------

    def metrics_snapshot(self) -> dict[str, Any]:
        with self._session() as session:
            total_attendances = session.query(AttendanceModel).count()
            total_messages = session.query(MessageModel).count()

            fallback_count = (
                session.query(MessageModel)
                .filter(MessageModel.fallback.is_(True))
                .count()
            )

            total_feedback = session.query(FeedbackModel).count()
            useful_feedback = (
                session.query(FeedbackModel)
                .filter(FeedbackModel.useful.is_(True))
                .count()
            )

            escalated = (
                session.query(AttendanceModel)
                .filter(AttendanceModel.escalated.is_(True))
                .count()
            )

            # top intents
            intent_rows = (
                session.query(
                    MessageModel.intent,
                    func.count(MessageModel.id),
                )
                .filter(MessageModel.intent.isnot(None))
                .group_by(MessageModel.intent)
                .order_by(func.count(MessageModel.id).desc())
                .limit(5)
                .all()
            )
            top_intents = {
                row[0] or "unknown": row[1] for row in intent_rows
            }

            # unanswered / fallback questions
            unanswered_rows = (
                session.query(MessageModel.user_message)
                .filter(MessageModel.fallback.is_(True))
                .order_by(MessageModel.created_at.desc())
                .limit(10)
                .all()
            )
            unanswered_questions = [row[0] for row in unanswered_rows]

            return {
                "total_attendances": total_attendances,
                "total_messages": total_messages,
                "fallback_rate": fallback_count / total_messages
                if total_messages
                else 0.0,
                "useful_feedback_rate": useful_feedback / total_feedback
                if total_feedback
                else 0.0,
                "escalated_attendances": escalated,
                "top_intents": top_intents,
                "top_documents": {},
                "unanswered_questions": unanswered_questions,
            }


# ------------------------------------------------------------------
# Model -> Domain converters
# ------------------------------------------------------------------


def _user_from_model(model: UserModel) -> User:
    return User(
        id=model.id,
        external_id=model.external_id,
        channel=Channel(model.channel),
        created_at=model.created_at,
    )


def _attendance_from_model(model: AttendanceModel) -> Attendance:
    return Attendance(
        id=model.id,
        user_id=model.user_id,
        channel=Channel(model.channel),
        escalated=model.escalated,
        started_at=model.started_at,
    )


def _msg_from_model(model: MessageModel) -> MessageRecord:
    from app.domain.enums import Intent

    return MessageRecord(
        id=model.id,
        attendance_id=model.attendance_id,
        user_message=model.user_message,
        assistant_answer=model.assistant_answer,
        fallback=model.fallback,
        intent=Intent(model.intent) if model.intent else Intent.UNKNOWN,
        confidence=float(model.confidence) if model.confidence else 0.0,
        sources=[],
        created_at=model.created_at,
    )


def _doc_from_model(model: DocumentModel) -> KnowledgeDocument:
    return KnowledgeDocument(
        id=model.id,
        title=model.title,
        category=model.category,
        channel=model.channel,
        version=model.version,
        status=DocumentStatus(model.status),
        updated_at=model.updated_at,
        source=model.source or "",
        owner=model.owner or "",
        sensitivity=model.sensitivity or "",
        content=model.content,
        tags=[],
    )
