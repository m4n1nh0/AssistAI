from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_ask_contract_success():
    payload = {
        "question": "Como faço para redefinir minha senha?",
        "channel": "web",
        "conversation_id": "conv_123",
        "user": {
            "id": "user_001",
            "name": "Vinícius"
        },
        "metadata": {
            "page_url": "http://localhost:5173/chat"
        }
    }

    response = client.post("/ask", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert "answer" in data
    assert "status" in data
    assert "conversation_id" in data
    assert "message_id" in data
    assert "sources" in data
    assert "metadata" in data


def test_ask_contract_invalid_question():
    payload = {
        "question": "",
        "channel": "web"
    }

    response = client.post("/ask", json=payload)

    assert response.status_code == 422


def test_ask_contract_invalid_channel():
    payload = {
        "question": "Teste de canal inválido",
        "channel": "whatsapp"
    }

    response = client.post("/ask", json=payload)

    assert response.status_code == 422