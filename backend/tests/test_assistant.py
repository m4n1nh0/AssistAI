from app.application.assistant_service import assistant_service
from app.domain.models import Channel


def test_known_question_returns_sources():
    response = assistant_service.ask("test-user", Channel.WEB, "Como faço para abrir um chamado?")

    assert response["fallback"] is False
    assert response["sources"]
    assert response["attendance_id"].startswith("att-")


def test_unknown_question_uses_fallback_and_handoff():
    response = assistant_service.ask("test-user-2", Channel.WEB, "Qual o cardapio do almoco?")

    assert response["fallback"] is True
    assert response["needs_human"] is True


def test_ticket_status_uses_simulated_mcp():
    response = assistant_service.ask("test-user-3", Channel.WEB, "Qual o status do CHM-12345?")

    assert "CHM-12345" in response["answer"]
    assert response["intent"] == "consulta_chamado"
