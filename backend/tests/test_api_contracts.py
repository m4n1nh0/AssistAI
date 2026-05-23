from fastapi.testclient import TestClient

from app.main import create_app


def test_health_contract() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ask_known_question_is_grounded_and_persisted_in_conversation() -> None:
    app = create_app()
    client = TestClient(app)

    first_response = client.post(
        "/ask",
        json={
            "question": "Como abrir chamado no suporte?",
            "channel": "web",
            "conversation_id": "conv_test_001",
            "user": {"id": "web-user-001"},
        },
    )
    second_response = client.post(
        "/ask",
        json={
            "question": "Como faco reset de senha?",
            "channel": "web",
            "conversation_id": "conv_test_001",
            "user": {"id": "web-user-001"},
        },
    )

    body = first_response.json()
    detail = client.get("/attendances/conv_test_001").json()

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert body["status"] == "answered"
    assert body["conversation_id"] == "conv_test_001"
    assert body["sources"][0]["chunk_id"].startswith("chk-")
    assert body["sources"][0]["version"] == "1.0"
    assert body["metadata"]["confidence"] >= 0.35
    assert len(detail["messages"]) == 2

    prompt = app.state.assistant_service.llm_gateway.last_prompt
    assert "Use exclusivamente" in prompt
    assert "CONTEXTO CONFIAVEL" in prompt


def test_ask_unknown_question_uses_safe_fallback() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/ask",
        json={
            "question": "Qual e a capital da Islandia?",
            "channel": "web",
            "conversation_id": "conv_test_002",
            "user": {"id": "web-user-001"},
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["status"] == "fallback"
    assert body["sources"] == []
    assert "Nao encontrei base suficiente" in body["answer"]
    assert body["metadata"]["confidence"] == 0.0


def test_feedback_is_linked_to_generated_message() -> None:
    app = create_app()
    client = TestClient(app)
    ask_response = client.post(
        "/ask",
        json={
            "question": "Como abrir chamado?",
            "channel": "web",
            "conversation_id": "conv_test_feedback",
            "user": {"id": "web-user-001"},
        },
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
    feedbacks = app.state.repository.get_feedback_by_message(body["message_id"])

    assert response.status_code == 200
    assert body["useful"] is True
    assert body["feedback_id"].startswith("fbk-")
    assert len(feedbacks) == 1
    assert feedbacks[0].comment == "Resolveu minha duvida."
