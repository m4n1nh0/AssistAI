from collections import Counter, defaultdict
from datetime import UTC, datetime
from threading import RLock

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


class InMemoryRepository:
    def __init__(self) -> None:
        self._lock = RLock()
        self.users: dict[str, User] = {}
        self.attendances: dict[str, Attendance] = {}
        self.messages: dict[str, MessageRecord] = {}
        self.documents: dict[str, KnowledgeDocument] = {}
        self.chunks: dict[str, DocumentChunk] = {}
        self.feedbacks: dict[str, Feedback] = {}
        self.ai_logs: dict[str, AiLog] = {}
        self.handoffs: dict[str, Handoff] = {}
        self.tool_calls: dict[str, ToolCall] = {}

    def seed_default_documents(self) -> None:
        if self.documents:
            return

        for payload in default_document_payloads():
            self.create_document(payload)

    def find_or_create_user(self, external_id: str, channel: Channel) -> User:
        key = f"{channel}:{external_id}"
        with self._lock:
            for user in self.users.values():
                if user.external_id == external_id and user.channel == channel:
                    return user

            user = User(id=new_id("usr"), external_id=external_id, channel=channel)
            self.users[key] = user
            return user

    def find_or_create_attendance(
        self,
        user_id: str,
        channel: Channel,
        attendance_id: str | None = None,
    ) -> Attendance:
        if attendance_id and attendance_id in self.attendances:
            return self.attendances[attendance_id]

        attendance = Attendance(
            id=attendance_id or new_id("att"),
            user_id=user_id,
            channel=channel,
        )
        with self._lock:
            self.attendances[attendance.id] = attendance
        return attendance

    def create_attendance(self, user_id: str, channel: Channel) -> Attendance:
        return self.find_or_create_attendance(user_id, channel)

    def mark_attendance_escalated(self, attendance_id: str, reason: str) -> Handoff:
        with self._lock:
            attendance = self.attendances[attendance_id]
            attendance.escalated = True
            handoff = Handoff(id=new_id("hnd"), attendance_id=attendance_id, reason=reason)
            self.handoffs[handoff.id] = handoff
            return handoff

    def add_message(self, message: MessageRecord) -> MessageRecord:
        with self._lock:
            self.messages[message.id] = message
        return message

    def add_feedback(self, message_id: str, useful: bool, comment: str | None) -> Feedback:
        if message_id not in self.messages:
            raise KeyError(f"Message not found: {message_id}")

        feedback = Feedback(
            id=new_id("fbk"),
            message_id=message_id,
            useful=useful,
            comment=comment,
        )
        with self._lock:
            self.feedbacks[feedback.id] = feedback
        return feedback

    def add_ai_log(self, log: AiLog) -> AiLog:
        with self._lock:
            self.ai_logs[log.id] = log
        return log

    def add_tool_call(self, tool_call: ToolCall) -> ToolCall:
        with self._lock:
            self.tool_calls[tool_call.id] = tool_call
        return tool_call

    def create_document(self, payload: DocumentCreateRequest) -> KnowledgeDocument:
        document = KnowledgeDocument(
            id=new_id("doc"),
            title=payload.title,
            category=payload.category,
            channel=payload.channel,
            version=payload.version,
            status=payload.status,
            updated_at=datetime.now(UTC),
            source=payload.source,
            owner=payload.owner,
            sensitivity=payload.sensitivity,
            content=payload.content,
            tags=payload.tags,
        )
        with self._lock:
            self.documents[document.id] = document
            self._replace_chunks(document)
        return document

    def list_documents(self) -> list[KnowledgeDocument]:
        return sorted(self.documents.values(), key=lambda item: item.updated_at, reverse=True)

    def reindex_documents(self) -> tuple[int, int]:
        with self._lock:
            self.chunks.clear()
            for document in self.documents.values():
                self._replace_chunks(document)
        return len(self.documents), len(self.chunks)

    def list_active_chunks(self) -> list[DocumentChunk]:
        active_ids = {
            document.id
            for document in self.documents.values()
            if document.status == DocumentStatus.ACTIVE
        }
        return [chunk for chunk in self.chunks.values() if chunk.document_id in active_ids]

    def get_document(self, document_id: str) -> KnowledgeDocument | None:
        return self.documents.get(document_id)

    def list_attendances(self) -> list[Attendance]:
        return sorted(self.attendances.values(), key=lambda item: item.started_at, reverse=True)

    def list_messages_by_attendance(self, attendance_id: str) -> list[MessageRecord]:
        messages = [
            message for message in self.messages.values() if message.attendance_id == attendance_id
        ]
        return sorted(messages, key=lambda item: item.created_at)

    def count_messages_by_attendance(self) -> dict[str, int]:
        counter: dict[str, int] = defaultdict(int)
        for message in self.messages.values():
            counter[message.attendance_id] += 1
        return counter

    def get_attendance(self, attendance_id: str) -> Attendance | None:
        return self.attendances.get(attendance_id)

    def get_feedback_by_message(self, message_id: str) -> list[Feedback]:
        return [
            feedback
            for feedback in self.feedbacks.values()
            if feedback.message_id == message_id
        ]

    def metrics_snapshot(self) -> dict[str, object]:
        total_messages = len(self.messages)
        fallback_count = sum(1 for message in self.messages.values() if message.fallback)
        useful_feedback = sum(1 for feedback in self.feedbacks.values() if feedback.useful)
        total_feedback = len(self.feedbacks)
        top_intents = Counter(message.intent.value for message in self.messages.values())
        top_documents: Counter[str] = Counter()
        unanswered_questions: list[str] = []

        for message in self.messages.values():
            for source in message.sources:
                top_documents[source.title] += 1
            if message.fallback:
                unanswered_questions.append(message.user_message)

        return {
            "total_attendances": len(self.attendances),
            "total_messages": total_messages,
            "fallback_rate": fallback_count / total_messages if total_messages else 0.0,
            "useful_feedback_rate": useful_feedback / total_feedback if total_feedback else 0.0,
            "escalated_attendances": sum(
                1 for attendance in self.attendances.values() if attendance.escalated
            ),
            "top_intents": dict(top_intents.most_common(5)),
            "top_documents": dict(top_documents.most_common(5)),
            "unanswered_questions": unanswered_questions[-10:],
        }

    def _replace_chunks(self, document: KnowledgeDocument) -> None:
        stale_ids = [
            chunk_id
            for chunk_id, chunk in self.chunks.items()
            if chunk.document_id == document.id
        ]
        for chunk_id in stale_ids:
            del self.chunks[chunk_id]

        for index, content in enumerate(_chunk_text(document.content), start=1):
            chunk = DocumentChunk(
                id=new_id("chk"),
                document_id=document.id,
                content=content,
                metadata={
                    "document_id": document.id,
                    "title": document.title,
                    "category": document.category,
                    "version": document.version,
                    "status": document.status.value,
                    "chunk_index": str(index),
                },
            )
            self.chunks[chunk.id] = chunk


def _chunk_text(text: str, max_words: int = 120) -> list[str]:
    words = text.split()
    if not words:
        return []
    return [
        " ".join(words[index : index + max_words])
        for index in range(0, len(words), max_words)
    ]


def default_document_payloads() -> list[DocumentCreateRequest]:
    return [
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
