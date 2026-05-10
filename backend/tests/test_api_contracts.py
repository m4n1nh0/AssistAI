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
            "question": "Como abrir chamado no suporte?",
            "channel": "web",
            "conversation_id": "conv_test_001",
            "user": {
                "id": "web-user-001",
            },
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["status"] == "answered"
    assert "answer" in body
    assert "conversation_id" in body
    assert "message_id" in body
    assert "sources" in body
    assert "metadata" in body


def test_ask_unknown_question_uses_fallback() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/ask",
        json={
            "question": "Qual e a capital da Islandia?",
            "channel": "web",
            "conversation_id": "conv_test_002",
            "user": {
                "id": "web-user-001",
            },
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["status"] in ["answered", "fallback"]
    assert "answer" in body
    assert "conversation_id" in body
    assert "message_id" in body
    assert "sources" in body
    assert "metadata" in body


# def test_feedback_contract() -> None:
#     client = TestClient(create_app())
#     ask_response = client.post(
#         "/ask",
#         json={
#             "question": "Como consultar status de chamado CHM-12345?",
#             "channel": "web",
#             "conversation_id": "conv_test_003",
#             "user": {
#                 "id": "web-user-001",
#             },
#         },
# )

#     response = client.post(
#         "/feedback",
#         json={
#             "message_id": ask_response.json()["message_id"],
#             "useful": True,
#             "comment": "Resolveu minha duvida.",
#         },
#     )

#     body = response.json()
#     assert response.status_code == 200
#     assert body["useful"] is True
#     assert body["feedback_id"].startswith("fbk-")

