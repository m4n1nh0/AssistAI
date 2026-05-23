from fastapi.testclient import TestClient

from app.main import create_app


def _ask_payload(question: str) -> dict:
    return {
        "version": "1.0",
        "question": question,
        "user_id": "web-user-001",
        "channel": "web",
        "metadata": {
            "timestamp": "2026-05-22T12:00:00Z",
            "user_agent": "pytest",
        },
    }


def test_health_contract() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ask_known_question_returns_sources() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/ask",
        json=_ask_payload("Como abrir chamado no suporte?"),
    )

    body = response.json()
    assert response.status_code == 200
    assert body["fallback"] is False
    assert body["sources"]
    assert body["attendance_id"].startswith("att-")
    assert body["message_id"].startswith("msg-")
    assert body["version"] == "1.0"
    assert body["metadata"]["model_used"] == "mock-llm-context-v1"
    assert body["answer"].startswith("Com base na base interna")
    assert "abrir um chamado" in body["answer"].lower()


def test_ask_unknown_question_uses_fallback() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/ask",
        json=_ask_payload("Qual e a capital da Islandia?"),
    )

    body = response.json()
    assert response.status_code == 200
    assert body["fallback"] is True
    assert body["sources"] == []
    assert body["fallback_reason"] == "no_sources"
    assert "capital da Islandia" not in body["answer"]


def test_ask_low_relevance_uses_low_score_fallback() -> None:
    app = create_app()
    original_min_score = app.state.assistant_service.settings.min_relevance_score
    app.state.assistant_service.settings.min_relevance_score = 0.95
    client = TestClient(app)

    try:
        response = client.post(
            "/ask",
            json=_ask_payload("Como abrir chamado no suporte?"),
        )
    finally:
        app.state.assistant_service.settings.min_relevance_score = original_min_score

    body = response.json()
    assert response.status_code == 200
    assert body["fallback"] is True
    assert body["fallback_reason"] == "low_score"
    assert body["sources"] == []


def test_ask_persists_message_score_and_sources() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.post(
        "/ask",
        json=_ask_payload("Como solicitar reset de senha?"),
    )

    body = response.json()
    message = app.state.repository.messages[body["message_id"]]
    assert response.status_code == 200
    assert message.user_message == "Como solicitar reset de senha?"
    assert message.assistant_answer == body["answer"]
    assert message.confidence == body["score"]
    assert message.sources


def test_feedback_contract() -> None:
    client = TestClient(create_app())
    ask_response = client.post(
        "/ask",
        json=_ask_payload("Como consultar status de chamado CHM-12345?"),
    )

    response = client.post(
        "/feedback",
        json={
            "message_id": ask_response.json()["message_id"],
            "useful": True,
            "comment": "Resolveu minha duvida.",
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["useful"] is True
    assert body["feedback_id"].startswith("fbk-")

