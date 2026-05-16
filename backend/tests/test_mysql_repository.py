from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.domain.contracts import DocumentCreateRequest
from app.domain.enums import Channel, DocumentStatus, Intent
from app.domain.models import AiLog, MessageRecord, new_id
from app.infrastructure.database.models import Base
from app.infrastructure.database.mysql_repository import MySqlRepository


def _make_repo() -> MySqlRepository:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session_maker = sessionmaker(bind=engine)
    return MySqlRepository(session_maker)


class TestMySqlRepository:
    def test_find_or_create_user_creates_and_caches(self) -> None:
        repo = _make_repo()
        user1 = repo.find_or_create_user("ext-1", Channel.WEB)
        user2 = repo.find_or_create_user("ext-1", Channel.WEB)

        assert user1.id == user2.id
        assert user1.external_id == "ext-1"
        assert user1.channel == Channel.WEB

    def test_find_or_create_user_different_channels(self) -> None:
        repo = _make_repo()
        user1 = repo.find_or_create_user("ext-1", Channel.WEB)
        user2 = repo.find_or_create_user("ext-1", Channel.TELEGRAM)

        assert user1.id != user2.id

    def test_create_attendance(self) -> None:
        repo = _make_repo()
        user = repo.find_or_create_user("ext-1", Channel.WEB)
        attendance = repo.create_attendance(user.id, Channel.WEB)

        assert attendance.id.startswith("att-")
        assert attendance.user_id == user.id
        assert attendance.channel == Channel.WEB
        assert attendance.escalated is False

    def test_mark_attendance_escalated(self) -> None:
        repo = _make_repo()
        user = repo.find_or_create_user("ext-1", Channel.WEB)
        attendance = repo.create_attendance(user.id, Channel.WEB)

        result = repo.mark_attendance_escalated(
            attendance.id, "test reason"
        )

        assert result.attendance_id == attendance.id
        assert result.reason == "test reason"

        att = repo.get_attendance(attendance.id)
        assert att is not None
        assert att.escalated is True

    def test_add_message(self) -> None:
        repo = _make_repo()
        user = repo.find_or_create_user("ext-1", Channel.WEB)
        attendance = repo.create_attendance(user.id, Channel.WEB)

        message = MessageRecord(
            id=new_id("msg"),
            attendance_id=attendance.id,
            user_message="pergunta",
            assistant_answer="resposta",
            fallback=False,
            intent=Intent.PROCEDURE,
            confidence=0.95,
            sources=[],
        )
        result = repo.add_message(message)

        assert result.id == message.id

        messages = repo.list_messages_by_attendance(attendance.id)
        assert len(messages) == 1
        assert messages[0].user_message == "pergunta"

    def test_add_feedback(self) -> None:
        repo = _make_repo()
        user = repo.find_or_create_user("ext-1", Channel.WEB)
        attendance = repo.create_attendance(user.id, Channel.WEB)
        message = MessageRecord(
            id=new_id("msg"),
            attendance_id=attendance.id,
            user_message="teste",
            assistant_answer="r",
            fallback=False,
            intent=Intent.PROCEDURE,
            confidence=0.5,
            sources=[],
        )
        repo.add_message(message)

        feedback = repo.add_feedback(message.id, True, "comentario")

        assert feedback.message_id == message.id
        assert feedback.useful is True
        assert feedback.comment == "comentario"

        feedbacks = repo.get_feedback_by_message(message.id)
        assert len(feedbacks) == 1

    def test_create_and_list_documents(self) -> None:
        repo = _make_repo()
        doc = repo.create_document(
            DocumentCreateRequest(
                title="Teste",
                category="geral",
                content="Conteudo do documento de teste.",
                tags=["tag1"],
            )
        )

        assert doc.title == "Teste"
        assert doc.status == DocumentStatus.ACTIVE

        docs = repo.list_documents()
        assert len(docs) == 1

    def test_seed_default_documents(self) -> None:
        repo = _make_repo()
        repo.seed_default_documents()

        docs = repo.list_documents()
        assert len(docs) == 4

    def test_reindex_documents(self) -> None:
        repo = _make_repo()
        repo.seed_default_documents()
        doc_count, chunk_count = repo.reindex_documents()

        assert doc_count == 4
        assert chunk_count >= 4

    def test_list_active_chunks(self) -> None:
        repo = _make_repo()
        repo.seed_default_documents()
        chunks = repo.list_active_chunks()

        assert len(chunks) >= 4
        assert all(chunk.document_id for chunk in chunks)

    def test_count_messages_by_attendance(self) -> None:
        repo = _make_repo()
        user = repo.find_or_create_user("ext-1", Channel.WEB)
        att1 = repo.create_attendance(user.id, Channel.WEB)
        att2 = repo.create_attendance(user.id, Channel.WEB)

        for _ in range(3):
            repo.add_message(
                MessageRecord(
                    id=new_id("msg"),
                    attendance_id=att1.id,
                    user_message="q",
                    assistant_answer="a",
                    fallback=False,
                    intent=Intent.PROCEDURE,
                    confidence=0.5,
                    sources=[],
                )
            )
        repo.add_message(
            MessageRecord(
                id=new_id("msg"),
                attendance_id=att2.id,
                user_message="q",
                assistant_answer="a",
                fallback=False,
                intent=Intent.PROCEDURE,
                confidence=0.5,
                sources=[],
            )
        )

        counts = repo.count_messages_by_attendance()
        assert counts[att1.id] == 3
        assert counts[att2.id] == 1

    def test_metrics_snapshot(self) -> None:
        repo = _make_repo()
        repo.seed_default_documents()
        user = repo.find_or_create_user("ext-1", Channel.WEB)
        att = repo.create_attendance(user.id, Channel.WEB)

        repo.add_message(
            MessageRecord(
                id=new_id("msg"),
                attendance_id=att.id,
                user_message="q1",
                assistant_answer="a1",
                fallback=False,
                intent=Intent.PROCEDURE,
                confidence=0.9,
                sources=[],
            )
        )
        repo.add_message(
            MessageRecord(
                id=new_id("msg"),
                attendance_id=att.id,
                user_message="q2",
                assistant_answer="fallback",
                fallback=True,
                intent=Intent.PROCEDURE,
                confidence=0.0,
                sources=[],
            )
        )

        metrics = repo.metrics_snapshot()
        assert metrics["total_attendances"] == 1
        assert metrics["total_messages"] == 2
        assert metrics["fallback_rate"] == 0.5
        assert len(metrics["unanswered_questions"]) == 1

    def test_get_document_not_found(self) -> None:
        repo = _make_repo()
        doc = repo.get_document("nonexistent")
        assert doc is None

    def test_list_attendances_empty(self) -> None:
        repo = _make_repo()
        assert repo.list_attendances() == []

    def test_add_ai_log(self) -> None:
        repo = _make_repo()
        log = AiLog(
            id=new_id("ailog"),
            message_id=new_id("msg"),
            intent=Intent.PROCEDURE,
            relevance_score=0.95,
            fallback=False,
            source_document_ids=["doc-1"],
            elapsed_ms=100,
        )
        result = repo.add_ai_log(log)
        assert result.id == log.id
