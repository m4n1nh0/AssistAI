import json
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from importlib import import_module
from typing import Any
from urllib.parse import unquote, urlparse

from app.domain.contracts import DocumentCreateRequest
from app.domain.enums import Channel, DocumentStatus, Intent
from app.domain.models import (
    AiLog,
    Attendance,
    DocumentChunk,
    Feedback,
    Handoff,
    KnowledgeDocument,
    MessageRecord,
    Source,
    ToolCall,
    User,
    new_id,
)
from app.infrastructure.repositories.memory import _chunk_text, default_document_payloads


@dataclass(frozen=True, slots=True)
class MySqlConfig:
    url: str


class MySqlRepository:
    def __init__(self, config: MySqlConfig) -> None:
        self.config = config
        self._pymysql = import_module("pymysql")
        self._connection_params = _parse_mysql_url(config.url)

    @contextmanager
    def _cursor(self) -> Iterator[Any]:
        connection = self._pymysql.connect(
            **self._connection_params,
            cursorclass=self._pymysql.cursors.DictCursor,
            autocommit=False,
        )
        try:
            with connection.cursor() as cursor:
                yield cursor
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def seed_default_documents(self) -> None:
        if self.list_documents():
            return
        for payload in default_document_payloads():
            self.create_document(payload)

    def find_or_create_user(self, external_id: str, channel: Channel) -> User:
        with self._cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE external_id = %s AND channel = %s LIMIT 1",
                (external_id, channel.value),
            )
            row = cursor.fetchone()
            if row:
                return _user_from_row(row)
            user = User(id=new_id("usr"), external_id=external_id, channel=channel)
            cursor.execute(
                "INSERT INTO users (id, external_id, channel, created_at) VALUES (%s, %s, %s, %s)",
                (user.id, user.external_id, user.channel.value, user.created_at),
            )
            return user

    def find_or_create_attendance(
        self,
        user_id: str,
        channel: Channel,
        attendance_id: str | None = None,
    ) -> Attendance:
        with self._cursor() as cursor:
            if attendance_id:
                cursor.execute("SELECT * FROM attendances WHERE id = %s", (attendance_id,))
                row = cursor.fetchone()
                if row:
                    return _attendance_from_row(row)
            attendance = Attendance(
                id=attendance_id or new_id("att"),
                user_id=user_id,
                channel=channel,
            )
            cursor.execute(
                (
                    "INSERT INTO attendances (id, user_id, channel, escalated, started_at) "
                    "VALUES (%s, %s, %s, %s, %s)"
                ),
                (
                    attendance.id,
                    attendance.user_id,
                    attendance.channel.value,
                    attendance.escalated,
                    attendance.started_at,
                ),
            )
            return attendance

    def create_attendance(self, user_id: str, channel: Channel) -> Attendance:
        return self.find_or_create_attendance(user_id, channel)

    def mark_attendance_escalated(self, attendance_id: str, reason: str) -> Handoff:
        handoff = Handoff(id=new_id("hnd"), attendance_id=attendance_id, reason=reason)
        with self._cursor() as cursor:
            cursor.execute(
                "UPDATE attendances SET escalated = TRUE WHERE id = %s",
                (attendance_id,),
            )
            cursor.execute(
                (
                    "INSERT INTO handoffs (id, attendance_id, reason, created_at) "
                    "VALUES (%s, %s, %s, %s)"
                ),
                (handoff.id, handoff.attendance_id, handoff.reason, handoff.created_at),
            )
        return handoff

    def add_message(self, message: MessageRecord) -> MessageRecord:
        with self._cursor() as cursor:
            cursor.execute(
                (
                    "INSERT INTO messages "
                    "(id, attendance_id, user_message, assistant_answer, "
                    "fallback, intent, confidence, created_at) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                ),
                (
                    message.id,
                    message.attendance_id,
                    message.user_message,
                    message.assistant_answer,
                    message.fallback,
                    message.intent.value,
                    message.confidence,
                    message.created_at,
                ),
            )
            for source in message.sources:
                cursor.execute(
                    (
                        "INSERT INTO message_sources "
                        "(message_id, document_id, chunk_id, title, version, score) "
                        "VALUES (%s, %s, %s, %s, %s, %s)"
                    ),
                    (
                        message.id,
                        source.document_id,
                        source.chunk_id,
                        source.title,
                        source.version,
                        source.score,
                    ),
                )
        return message

    def add_feedback(self, message_id: str, useful: bool, comment: str | None) -> Feedback:
        with self._cursor() as cursor:
            cursor.execute("SELECT id FROM messages WHERE id = %s", (message_id,))
            if not cursor.fetchone():
                raise KeyError(f"Message not found: {message_id}")
            feedback = Feedback(
                id=new_id("fbk"),
                message_id=message_id,
                useful=useful,
                comment=comment,
            )
            cursor.execute(
                (
                    "INSERT INTO feedbacks (id, message_id, useful, comment, created_at) "
                    "VALUES (%s, %s, %s, %s, %s)"
                ),
                (
                    feedback.id,
                    feedback.message_id,
                    feedback.useful,
                    feedback.comment,
                    feedback.created_at,
                ),
            )
        return feedback

    def add_ai_log(self, log: AiLog) -> AiLog:
        with self._cursor() as cursor:
            cursor.execute(
                (
                    "INSERT INTO ai_logs "
                    "(id, message_id, intent, relevance_score, fallback, "
                    "source_document_ids, elapsed_ms, created_at) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                ),
                (
                    log.id,
                    log.message_id,
                    log.intent.value,
                    log.relevance_score,
                    log.fallback,
                    json.dumps(log.source_document_ids),
                    log.elapsed_ms,
                    log.created_at,
                ),
            )
        return log

    def add_tool_call(self, tool_call: ToolCall) -> ToolCall:
        with self._cursor() as cursor:
            cursor.execute(
                (
                    "INSERT INTO tool_calls "
                    "(id, message_id, tool_name, input_payload, output_payload, "
                    "success, created_at) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s)"
                ),
                (
                    tool_call.id,
                    tool_call.message_id,
                    tool_call.tool_name,
                    json.dumps(tool_call.input_payload),
                    json.dumps(tool_call.output_payload),
                    tool_call.success,
                    tool_call.created_at,
                ),
            )
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
        with self._cursor() as cursor:
            cursor.execute(
                (
                    "INSERT INTO documents "
                    "(id, title, category, channel, version, status, updated_at, "
                    "source, owner, sensitivity, content, tags) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                ),
                (
                    document.id,
                    document.title,
                    document.category,
                    document.channel,
                    document.version,
                    document.status.value,
                    document.updated_at,
                    document.source,
                    document.owner,
                    document.sensitivity,
                    document.content,
                    json.dumps(document.tags),
                ),
            )
            self._replace_chunks(cursor, document)
        return document

    def list_documents(self) -> list[KnowledgeDocument]:
        with self._cursor() as cursor:
            cursor.execute("SELECT * FROM documents ORDER BY updated_at DESC")
            return [_document_from_row(row) for row in cursor.fetchall()]

    def reindex_documents(self) -> tuple[int, int]:
        documents = self.list_documents()
        with self._cursor() as cursor:
            cursor.execute("DELETE FROM document_chunks")
            for document in documents:
                self._replace_chunks(cursor, document)
            cursor.execute("SELECT COUNT(*) AS total FROM document_chunks")
            chunks = int(cursor.fetchone()["total"])
        return len(documents), chunks

    def list_active_chunks(self) -> list[DocumentChunk]:
        with self._cursor() as cursor:
            cursor.execute(
                (
                    "SELECT c.* FROM document_chunks c "
                    "JOIN documents d ON d.id = c.document_id WHERE d.status = %s"
                ),
                (DocumentStatus.ACTIVE.value,),
            )
            return [_chunk_from_row(row) for row in cursor.fetchall()]

    def get_document(self, document_id: str) -> KnowledgeDocument | None:
        with self._cursor() as cursor:
            cursor.execute("SELECT * FROM documents WHERE id = %s", (document_id,))
            row = cursor.fetchone()
        return _document_from_row(row) if row else None

    def list_attendances(self) -> list[Attendance]:
        with self._cursor() as cursor:
            cursor.execute("SELECT * FROM attendances ORDER BY started_at DESC")
            return [_attendance_from_row(row) for row in cursor.fetchall()]

    def list_messages_by_attendance(self, attendance_id: str) -> list[MessageRecord]:
        with self._cursor() as cursor:
            cursor.execute(
                "SELECT * FROM messages WHERE attendance_id = %s ORDER BY created_at",
                (attendance_id,),
            )
            rows = cursor.fetchall()
        return [_message_from_row(row, self._sources_for_message(row["id"])) for row in rows]

    def count_messages_by_attendance(self) -> dict[str, int]:
        with self._cursor() as cursor:
            cursor.execute(
                "SELECT attendance_id, COUNT(*) AS total FROM messages GROUP BY attendance_id"
            )
            return {row["attendance_id"]: int(row["total"]) for row in cursor.fetchall()}

    def get_attendance(self, attendance_id: str) -> Attendance | None:
        with self._cursor() as cursor:
            cursor.execute("SELECT * FROM attendances WHERE id = %s", (attendance_id,))
            row = cursor.fetchone()
        return _attendance_from_row(row) if row else None

    def get_feedback_by_message(self, message_id: str) -> list[Feedback]:
        with self._cursor() as cursor:
            cursor.execute("SELECT * FROM feedbacks WHERE message_id = %s", (message_id,))
            return [_feedback_from_row(row) for row in cursor.fetchall()]

    def metrics_snapshot(self) -> dict[str, object]:
        attendances = self.list_attendances()
        messages = [
            message
            for attendance in attendances
            for message in self.list_messages_by_attendance(attendance.id)
        ]
        with self._cursor() as cursor:
            cursor.execute("SELECT * FROM feedbacks")
            feedbacks = [_feedback_from_row(row) for row in cursor.fetchall()]
        fallback_count = sum(1 for message in messages if message.fallback)
        useful_feedback = sum(1 for feedback in feedbacks if feedback.useful)
        top_intents: dict[str, int] = {}
        top_documents: dict[str, int] = {}
        for message in messages:
            top_intents[message.intent.value] = top_intents.get(message.intent.value, 0) + 1
            for source in message.sources:
                top_documents[source.title] = top_documents.get(source.title, 0) + 1
        return {
            "total_attendances": len(attendances),
            "total_messages": len(messages),
            "fallback_rate": fallback_count / len(messages) if messages else 0.0,
            "useful_feedback_rate": useful_feedback / len(feedbacks) if feedbacks else 0.0,
            "escalated_attendances": sum(1 for attendance in attendances if attendance.escalated),
            "top_intents": top_intents,
            "top_documents": top_documents,
            "unanswered_questions": [
                message.user_message for message in messages if message.fallback
            ][-10:],
        }

    def _sources_for_message(self, message_id: str) -> list[Source]:
        with self._cursor() as cursor:
            cursor.execute("SELECT * FROM message_sources WHERE message_id = %s", (message_id,))
            return [
                Source(
                    document_id=row["document_id"],
                    chunk_id=row["chunk_id"],
                    title=row["title"],
                    version=row["version"],
                    score=float(row["score"]),
                )
                for row in cursor.fetchall()
            ]

    def _replace_chunks(self, cursor: Any, document: KnowledgeDocument) -> None:
        cursor.execute("DELETE FROM document_chunks WHERE document_id = %s", (document.id,))
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
            cursor.execute(
                (
                    "INSERT INTO document_chunks (id, document_id, content, metadata, indexed_at) "
                    "VALUES (%s, %s, %s, %s, %s)"
                ),
                (
                    chunk.id,
                    chunk.document_id,
                    chunk.content,
                    json.dumps(chunk.metadata),
                    chunk.indexed_at,
                ),
            )


def _parse_mysql_url(url: str) -> dict[str, Any]:
    parsed = urlparse(url)
    return {
        "host": parsed.hostname or "localhost",
        "port": parsed.port or 3306,
        "user": unquote(parsed.username or ""),
        "password": unquote(parsed.password or ""),
        "database": parsed.path.lstrip("/"),
        "charset": "utf8mb4",
    }


def _user_from_row(row: dict[str, Any]) -> User:
    return User(
        id=row["id"],
        external_id=row["external_id"],
        channel=Channel(row["channel"]),
        created_at=row["created_at"],
    )


def _attendance_from_row(row: dict[str, Any]) -> Attendance:
    return Attendance(
        id=row["id"],
        user_id=row["user_id"],
        channel=Channel(row["channel"]),
        escalated=bool(row["escalated"]),
        started_at=row["started_at"],
    )


def _document_from_row(row: dict[str, Any]) -> KnowledgeDocument:
    return KnowledgeDocument(
        id=row["id"],
        title=row["title"],
        category=row["category"],
        channel=row["channel"],
        version=row["version"],
        status=DocumentStatus(row["status"]),
        updated_at=row["updated_at"],
        source=row["source"],
        owner=row["owner"],
        sensitivity=row["sensitivity"],
        content=row["content"],
        tags=json.loads(row.get("tags") or "[]"),
    )


def _chunk_from_row(row: dict[str, Any]) -> DocumentChunk:
    return DocumentChunk(
        id=row["id"],
        document_id=row["document_id"],
        content=row["content"],
        metadata=json.loads(row["metadata"]),
        indexed_at=row["indexed_at"],
    )


def _message_from_row(row: dict[str, Any], sources: list[Source]) -> MessageRecord:
    return MessageRecord(
        id=row["id"],
        attendance_id=row["attendance_id"],
        user_message=row["user_message"],
        assistant_answer=row["assistant_answer"],
        fallback=bool(row["fallback"]),
        intent=Intent(row["intent"]),
        confidence=float(row["confidence"]),
        sources=sources,
        created_at=row["created_at"],
    )


def _feedback_from_row(row: dict[str, Any]) -> Feedback:
    return Feedback(
        id=row["id"],
        message_id=row["message_id"],
        useful=bool(row["useful"]),
        comment=row["comment"],
        created_at=row["created_at"],
    )
