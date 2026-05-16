from __future__ import annotations

from app.core.config import Settings
from app.domain.enums import Channel, Intent
from app.infrastructure.graph.assistant_graph import AssistantGraph
from app.infrastructure.mcp.simulated_tools import SimulatedToolRegistry
from app.infrastructure.rag.simple_retriever import SimpleRetriever
from app.infrastructure.repositories.memory import InMemoryRepository


class FakeTestLLM:
    def generate(self, question: str, contexts: list, system_prompt: str | None = None) -> str:
        if not contexts:
            return "Nao encontrei base suficiente."
        title = contexts[0].chunk.metadata.get("title", "doc")
        return f"Resposta baseada em {title}."

    def generate_stream(self, question: str, contexts: list, system_prompt: str | None = None):
        yield self.generate(question, contexts, system_prompt)


def _make_graph() -> AssistantGraph:
    settings = Settings()
    repository = InMemoryRepository()
    repository.seed_default_documents()
    retriever = SimpleRetriever(repository)
    llm = FakeTestLLM()
    tools = SimulatedToolRegistry(enabled=True)

    return AssistantGraph(
        repository=repository,
        retriever=retriever,
        llm_gateway=llm,
        tools=tools,
        settings=settings,
    )


class TestAssistantGraph:
    def test_graph_known_question_returns_answer(self) -> None:
        graph = _make_graph()
        result = graph.run(
            message="Como abrir chamado no suporte?",
            user_id="test-user",
            channel=Channel.WEB,
        )

        assert result.answer
        assert result.fallback is False
        assert result.intent == Intent.PROCEDURE
        assert result.sources
        assert result.attendance_id.startswith("att-")
        assert result.message_id.startswith("msg-")

    def test_graph_unknown_question_triggers_fallback(self) -> None:
        graph = _make_graph()
        result = graph.run(
            message="Qual e a capital da Franca?",
            user_id="test-user",
            channel=Channel.WEB,
        )

        assert result.fallback is True
        assert result.sources == []
        assert "nao encontrei" in result.answer.lower()

    def test_graph_greeting(self) -> None:
        graph = _make_graph()
        result = graph.run(
            message="Ola",
            user_id="test-user",
            channel=Channel.WEB,
        )

        assert result.intent == Intent.GREETING
        assert not result.fallback

    def test_graph_human_request(self) -> None:
        graph = _make_graph()
        result = graph.run(
            message="Quero falar com um atendente",
            user_id="test-user",
            channel=Channel.WEB,
        )

        assert result.intent == Intent.HUMAN_REQUEST
        assert result.fallback is True

    def test_graph_ticket_status(self) -> None:
        graph = _make_graph()
        result = graph.run(
            message="Qual o status do chamado CHM-12345?",
            user_id="test-user",
            channel=Channel.WEB,
        )

        assert result.intent == Intent.TICKET_STATUS
        assert result.fallback is False
        assert "CHM-12345" in result.answer

    def test_graph_ticket_without_id(self) -> None:
        graph = _make_graph()
        result = graph.run(
            message="Quero consultar chamado CHM-99999",
            user_id="test-user",
            channel=Channel.WEB,
        )

        assert result.intent == Intent.TICKET_STATUS
        assert "CHM-99999" in result.answer

    def test_graph_persists_message(self) -> None:
        settings = Settings()
        repository = InMemoryRepository()
        repository.seed_default_documents()
        retriever = SimpleRetriever(repository)
        llm = FakeTestLLM()
        tools = SimulatedToolRegistry(enabled=True)

        graph = AssistantGraph(
            repository=repository,
            retriever=retriever,
            llm_gateway=llm,
            tools=tools,
            settings=settings,
        )

        result = graph.run(
            message="Como resetar minha senha?",
            user_id="test-user",
            channel=Channel.WEB,
        )

        assert result.message_id in repository.messages
        stored = repository.messages[result.message_id]
        assert stored.user_message == "Como resetar minha senha?"

    def test_graph_telegram_channel(self) -> None:
        graph = _make_graph()
        result = graph.run(
            message="Como abrir chamado?",
            user_id="tg-user-1",
            channel=Channel.TELEGRAM,
        )

        attendance = graph.repository.get_attendance(result.attendance_id)
        assert attendance is not None
        assert attendance.channel == Channel.TELEGRAM

    def test_graph_multiple_questions_different_attendances(self) -> None:
        graph = _make_graph()
        r1 = graph.run(
            message="Como abrir chamado?",
            user_id="user-1",
            channel=Channel.WEB,
        )
        r2 = graph.run(
            message="Como resetar senha?",
            user_id="user-1",
            channel=Channel.WEB,
        )

        assert r1.attendance_id != r2.attendance_id

    def test_graph_confidence_reflects_relevance(self) -> None:
        graph = _make_graph()
        result = graph.run(
            message="Como abrir chamado no suporte?",
            user_id="test-user",
            channel=Channel.WEB,
        )

        assert result.confidence > 0

    def test_graph_sources_contain_document_info(self) -> None:
        graph = _make_graph()
        result = graph.run(
            message="Como abrir chamado no suporte?",
            user_id="test-user",
            channel=Channel.WEB,
        )

        if result.sources:
            source = result.sources[0]
            assert source.document_id
            assert source.title
            assert source.score > 0

    def test_graph_fallback_escalates_attendance(self) -> None:
        graph = _make_graph()
        result = graph.run(
            message="O que e astronomia?",
            user_id="test-user",
            channel=Channel.WEB,
        )

        assert result.fallback is True
        attendance = graph.repository.get_attendance(result.attendance_id)
        assert attendance is not None
        assert attendance.escalated is True
