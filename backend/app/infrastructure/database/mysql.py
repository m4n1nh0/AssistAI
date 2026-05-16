import json
import logging
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse

from app.domain.models import AiLog, Attendance, Feedback, Handoff, MessageRecord, User

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class MySqlConfig:
    url: str
    connect_timeout_seconds: float = 3.0


class MySqlUnitOfWork:
    def __init__(self, config: MySqlConfig) -> None:
        self.config = config

    def __enter__(self) -> "MySqlUnitOfWork":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        return None

    @contextmanager
    def connection(self) -> Iterator[Any]:
        try:
            import pymysql
        except ImportError as exc:
            raise MySqlUnavailable("PyMySQL is not installed.") from exc

        parsed = urlparse(self.config.url)
        if parsed.scheme not in {"mysql", "mysql+pymysql"}:
            raise MySqlUnavailable(f"Unsupported MySQL URL scheme: {parsed.scheme}")

        database = parsed.path.lstrip("/")
        try:
            connection = pymysql.connect(
                host=parsed.hostname or "localhost",
                port=parsed.port or 3306,
                user=parsed.username or "",
                password=parsed.password or "",
                database=database or None,
                charset="utf8mb4",
                autocommit=False,
                connect_timeout=self.config.connect_timeout_seconds,
                cursorclass=pymysql.cursors.DictCursor,
            )
        except Exception as exc:  # pragma: no cover - depends on local MySQL availability.
            raise MySqlUnavailable(f"MySQL unavailable: {exc}") from exc

        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()


class MySqlUnavailable(RuntimeError):
    pass


class MySqlAuditStore:
    def __init__(self, unit_of_work: MySqlUnitOfWork, enabled: bool = True) -> None:
        self.unit_of_work = unit_of_work
        self.enabled = enabled
        self._schema_ready = False

    def persist_interaction(
        self,
        user: User,
        attendance: Attendance,
        message: MessageRecord,
        ai_log: AiLog,
        handoff: Handoff | None = None,
    ) -> None:
        self._safe_run(
            lambda connection: self._persist_interaction(
                connection,
                user,
                attendance,
                message,
                ai_log,
                handoff,
            )
        )

    def persist_feedback(self, feedback: Feedback) -> None:
        self._safe_run(lambda connection: self._persist_feedback(connection, feedback))

    def _safe_run(self, operation: Callable[[Any], None]) -> None:
        if not self.enabled:
            return

        try:
            with self.unit_of_work.connection() as connection:
                if not self._schema_ready:
                    _ensure_schema(connection)
                    self._schema_ready = True
                operation(connection)
        except MySqlUnavailable as exc:
            logger.warning("mysql_persistence_skipped", extra={"reason": str(exc)})
        except Exception as exc:  # pragma: no cover - defensive guard for external DB errors.
            logger.exception("mysql_persistence_failed", extra={"reason": str(exc)})

    def _persist_interaction(
        self,
        connection: Any,
        user: User,
        attendance: Attendance,
        message: MessageRecord,
        ai_log: AiLog,
        handoff: Handoff | None,
    ) -> None:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (id, external_id, channel, created_at)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE external_id = VALUES(external_id), channel = VALUES(channel)
                """,
                (user.id, user.external_id, user.channel.value, user.created_at),
            )
            cursor.execute(
                """
                INSERT INTO attendances (id, user_id, channel, escalated, started_at)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE escalated = VALUES(escalated)
                """,
                (
                    attendance.id,
                    attendance.user_id,
                    attendance.channel.value,
                    attendance.escalated,
                    attendance.started_at,
                ),
            )
            cursor.execute(
                """
                INSERT INTO messages (
                  id, attendance_id, user_message, assistant_answer,
                  fallback, intent, confidence, created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                  assistant_answer = VALUES(assistant_answer),
                  fallback = VALUES(fallback),
                  intent = VALUES(intent),
                  confidence = VALUES(confidence)
                """,
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
            cursor.execute("DELETE FROM message_sources WHERE message_id = %s", (message.id,))
            for source in message.sources:
                cursor.execute(
                    """
                    INSERT INTO message_sources (
                      message_id, document_id, title, version, score
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        message.id,
                        source.document_id,
                        source.title,
                        source.version,
                        source.score,
                    ),
                )

            cursor.execute(
                """
                INSERT INTO ai_logs (
                  id, message_id, intent, relevance_score, fallback,
                  source_document_ids, elapsed_ms, created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                  relevance_score = VALUES(relevance_score),
                  fallback = VALUES(fallback),
                  source_document_ids = VALUES(source_document_ids),
                  elapsed_ms = VALUES(elapsed_ms)
                """,
                (
                    ai_log.id,
                    ai_log.message_id,
                    ai_log.intent.value,
                    ai_log.relevance_score,
                    ai_log.fallback,
                    json.dumps(ai_log.source_document_ids, ensure_ascii=True),
                    ai_log.elapsed_ms,
                    ai_log.created_at,
                ),
            )

            if handoff:
                cursor.execute(
                    """
                    INSERT INTO handoffs (id, attendance_id, reason, created_at)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE reason = VALUES(reason)
                    """,
                    (handoff.id, handoff.attendance_id, handoff.reason, handoff.created_at),
                )

    def _persist_feedback(self, connection: Any, feedback: Feedback) -> None:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO feedbacks (id, message_id, useful, comment, created_at)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE useful = VALUES(useful), comment = VALUES(comment)
                """,
                (
                    feedback.id,
                    feedback.message_id,
                    feedback.useful,
                    feedback.comment,
                    feedback.created_at,
                ),
            )


def _ensure_schema(connection: Any) -> None:
    statements = [
        """
        CREATE TABLE IF NOT EXISTS users (
          id VARCHAR(64) PRIMARY KEY,
          external_id VARCHAR(128) NOT NULL,
          channel VARCHAR(32) NOT NULL,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS attendances (
          id VARCHAR(64) PRIMARY KEY,
          user_id VARCHAR(64) NOT NULL,
          channel VARCHAR(32) NOT NULL,
          escalated BOOLEAN DEFAULT FALSE,
          started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS messages (
          id VARCHAR(64) PRIMARY KEY,
          attendance_id VARCHAR(64) NOT NULL,
          user_message TEXT NOT NULL,
          assistant_answer TEXT NOT NULL,
          fallback BOOLEAN DEFAULT FALSE,
          intent VARCHAR(64),
          confidence DECIMAL(5, 4),
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS message_sources (
          id BIGINT AUTO_INCREMENT PRIMARY KEY,
          message_id VARCHAR(64) NOT NULL,
          document_id VARCHAR(64) NOT NULL,
          title VARCHAR(255) NOT NULL,
          version VARCHAR(32) NOT NULL,
          score DECIMAL(6, 4) NOT NULL,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          INDEX idx_message_sources_message_id (message_id)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS ai_logs (
          id VARCHAR(64) PRIMARY KEY,
          message_id VARCHAR(64) NOT NULL,
          intent VARCHAR(64),
          relevance_score DECIMAL(6, 4),
          fallback BOOLEAN DEFAULT FALSE,
          source_document_ids JSON,
          elapsed_ms INT,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS handoffs (
          id VARCHAR(64) PRIMARY KEY,
          attendance_id VARCHAR(64) NOT NULL,
          reason TEXT NOT NULL,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS feedbacks (
          id VARCHAR(64) PRIMARY KEY,
          message_id VARCHAR(64) NOT NULL,
          useful BOOLEAN NOT NULL,
          comment TEXT,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
    ]

    with connection.cursor() as cursor:
        for statement in statements:
            cursor.execute(statement)
