from fastapi.testclient import TestClient

from app.main import create_app


def test_health_contract() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ask_known_question_returns_sources() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/ask",
        json={
            "user_id": "web-user-001",
            "channel": "web",
            "message": "Como abrir chamado no suporte?",
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["fallback"] is False
    assert body["sources"]
    assert body["attendance_id"].startswith("att-")
    assert body["message_id"].startswith("msg-")


def test_ask_unknown_question_uses_fallback() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/ask",
        json={
            "user_id": "web-user-001",
            "channel": "web",
            "message": "Qual e a capital da Islandia?",
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["fallback"] is True
    assert body["sources"] == []


def test_feedback_contract() -> None:
    client = TestClient(create_app())
    ask_response = client.post(
        "/ask",
        json={
            "user_id": "web-user-001",
            "channel": "web",
            "message": "Como consultar status de chamado CHM-12345?",
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
    assert response.status_code == 200
    assert body["useful"] is True
    assert body["feedback_id"].startswith("fbk-")

