from fastapi.testclient import TestClient

from app.domain.enums import Channel, Intent
from app.main import create_app

ASK_RESPONSE_KEYS = {
    "answer",
    "fallback",
    "intent",
    "confidence",
    "sources",
    "attendance_id",
    "message_id",
}
SOURCE_RESPONSE_KEYS = {"document_id", "title", "version", "score"}
INTENT_VALUES = {intent.value for intent in Intent}


def assert_official_ask_response_contract(body: dict) -> None:
    assert set(body) == ASK_RESPONSE_KEYS
    assert isinstance(body["answer"], str)
    assert isinstance(body["fallback"], bool)
    assert body["intent"] in INTENT_VALUES
    assert isinstance(body["confidence"], int | float)
    assert 0.0 <= body["confidence"] <= 1.0
    assert isinstance(body["sources"], list)
    assert body["attendance_id"].startswith("att-")
    assert body["message_id"].startswith("msg-")

    for source in body["sources"]:
        assert set(source) == SOURCE_RESPONSE_KEYS
        assert source["document_id"].startswith("doc-")
        assert isinstance(source["title"], str)
        assert isinstance(source["version"], str)
        assert isinstance(source["score"], int | float)
        assert 0.0 <= source["score"] <= 1.0


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
    assert_official_ask_response_contract(body)
    assert body["fallback"] is False
    assert body["sources"]


def test_ask_known_question_persists_attendance_message_and_sources() -> None:
    client = TestClient(create_app())

    ask_response = client.post(
        "/ask",
        json={
            "user_id": "web-user-001",
            "channel": "web",
            "message": "Como abrir chamado no suporte?",
        },
    )
    body = ask_response.json()

    attendance_response = client.get(f"/attendances/{body['attendance_id']}")

    assert attendance_response.status_code == 200
    attendance = attendance_response.json()
    assert attendance["attendance_id"] == body["attendance_id"]
    assert attendance["messages"][0]["message_id"] == body["message_id"]
    assert attendance["messages"][0]["sources"] == body["sources"]


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
    assert_official_ask_response_contract(body)
    assert body["fallback"] is True
    assert body["sources"] == []


def test_documents_reindex_contract_returns_indexed_counts() -> None:
    client = TestClient(create_app())

    response = client.post("/documents/reindex")

    body = response.json()
    assert response.status_code == 200
    assert set(body) == {"indexed_documents", "indexed_chunks"}
    assert body["indexed_documents"] >= 1
    assert body["indexed_chunks"] >= body["indexed_documents"]


def test_ask_requires_official_request_contract() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/ask",
        json={
            "user_id": "web-user-001",
            "message": "Como abrir chamado no suporte?",
        },
    )

    assert response.status_code == 422


def test_telegram_webhook_returns_official_ask_response_contract() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/telegram/webhook",
        json={
            "user_id": "telegram-123456",
            "message": "Como abrir chamado no suporte?",
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert_official_ask_response_contract(body)

    attendance_response = client.get(f"/attendances/{body['attendance_id']}")
    assert attendance_response.status_code == 200
    assert attendance_response.json()["channel"] == Channel.TELEGRAM.value


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
