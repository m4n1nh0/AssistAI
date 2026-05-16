from __future__ import annotations

from app.domain.contracts import AskRequest
from app.domain.enums import Channel, Intent


class TestAssistantService:
    def test_ask_known_question_returns_answer_with_sources(
        self, assistant_service
    ) -> None:
        response = assistant_service.ask(
            AskRequest(
                user_id="test-user",
                channel=Channel.WEB,
                message="Como abrir chamado no suporte?",
            )
        )

        assert response.answer
        assert response.fallback is False
        assert response.intent == Intent.PROCEDURE
        assert response.sources
        assert response.attendance_id.startswith("att-")
        assert response.message_id.startswith("msg-")
        assert response.confidence > 0

    def test_ask_unknown_question_triggers_fallback(
        self, assistant_service
    ) -> None:
        response = assistant_service.ask(
            AskRequest(
                user_id="test-user",
                channel=Channel.WEB,
                message="Qual e a capital da Islandia?",
            )
        )

        assert response.fallback is True
        assert "nao encontrei" in response.answer.lower()
        assert response.sources == []

    def test_ask_greeting_returns_greeting(
        self, assistant_service
    ) -> None:
        response = assistant_service.ask(
            AskRequest(
                user_id="test-user",
                channel=Channel.WEB,
                message="Ola",
            )
        )

        assert response.intent == Intent.GREETING
        assert not response.fallback

    def test_ask_human_request_escalates(
        self, assistant_service
    ) -> None:
        response = assistant_service.ask(
            AskRequest(
                user_id="test-user",
                channel=Channel.WEB,
                message="Quero falar com um humano",
            )
        )

        assert response.intent == Intent.HUMAN_REQUEST
        assert response.fallback is True

    def test_ask_ticket_status_with_valid_id(
        self, assistant_service
    ) -> None:
        response = assistant_service.ask(
            AskRequest(
                user_id="test-user",
                channel=Channel.WEB,
                message="Qual o status do chamado CHM-12345?",
            )
        )

        assert response.intent == Intent.TICKET_STATUS
        assert response.fallback is False
        assert "CHM-12345" in response.answer

    def test_ask_ticket_status_without_id(
        self, assistant_service
    ) -> None:
        response = assistant_service.ask(
            AskRequest(
                user_id="test-user",
                channel=Channel.WEB,
                message="Quero consultar o chamado CHM-99999",
            )
        )

        assert response.intent == Intent.TICKET_STATUS
        assert "CHM-99999" in response.answer

    def test_ask_persists_message(
        self, assistant_service
    ) -> None:
        response = assistant_service.ask(
            AskRequest(
                user_id="test-user",
                channel=Channel.WEB,
                message="Como resetar minha senha?",
            )
        )

        messages = assistant_service.repository.messages
        assert response.message_id in messages
        stored = messages[response.message_id]
        assert stored.user_message == "Como resetar minha senha?"
        assert stored.assistant_answer == response.answer

    def test_ask_sanitizes_long_message(
        self, assistant_service
    ) -> None:
        long_msg = "x" * 2500
        msg = long_msg[:2000]
        response = assistant_service.ask(
            AskRequest(
                user_id="test-user",
                channel=Channel.WEB,
                message=msg,
            )
        )

        stored = assistant_service.repository.messages[response.message_id]
        assert len(stored.user_message) <= 2000
        assert stored.user_message == msg

    def test_ask_multiple_questions_creates_separate_attendances(
        self, assistant_service
    ) -> None:
        r1 = assistant_service.ask(
            AskRequest(
                user_id="user-1",
                channel=Channel.WEB,
                message="Como abrir chamado?",
            )
        )
        r2 = assistant_service.ask(
            AskRequest(
                user_id="user-1",
                channel=Channel.WEB,
                message="Como resetar senha?",
            )
        )

        assert r1.attendance_id != r2.attendance_id

    def test_ask_telegram_channel_is_persisted(
        self, assistant_service
    ) -> None:
        response = assistant_service.ask(
            AskRequest(
                user_id="tg-user-1",
                channel=Channel.TELEGRAM,
                message="Como abrir chamado?",
            )
        )

        attendance = assistant_service.repository.get_attendance(
            response.attendance_id
        )
        assert attendance is not None
        assert attendance.channel == Channel.TELEGRAM
