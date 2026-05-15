from collections.abc import AsyncIterator

import httpx
import pytest

from app.main import create_app

ASSISTANT_CONTRACT_VERSION = "assistant.ask.v1"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    transport = httpx.ASGITransport(app=create_app())
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.mark.anyio
async def test_health_contract(client: httpx.AsyncClient) -> None:
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.anyio
async def test_ask_known_question_returns_sources(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/ask",
        json={
            "user_id": "web-user-001",
            "channel": "web",
            "request_id": "req-web-001",
            "message": "Como abrir chamado no suporte?",
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["fallback"] is False
    assert body["schema_version"] == ASSISTANT_CONTRACT_VERSION
    assert body["request_id"] == "req-web-001"
    assert body["user_id"] == "web-user-001"
    assert body["channel"] == "web"
    assert body["handoff_required"] is False
    assert body["generated_at"]
    assert body["sources"]
    assert body["attendance_id"].startswith("att-")
    assert body["message_id"].startswith("msg-")


@pytest.mark.anyio
async def test_ask_unknown_question_uses_fallback(client: httpx.AsyncClient) -> None:
    response = await client.post(
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
    assert body["handoff_required"] is True
    assert body["sources"] == []


@pytest.mark.anyio
async def test_ask_rejects_invalid_contract_payload(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/ask",
        json={
            "schema_version": "assistant.ask.v0",
            "user_id": "web-user-001",
            "channel": "web",
            "message": "",
        },
    )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_telegram_webhook_uses_official_assistant_contract(
    client: httpx.AsyncClient,
) -> None:
    response = await client.post(
        "/telegram/webhook",
        json={
            "request_id": "req-tg-001",
            "user_id": "telegram-user-001",
            "message": "Como abrir chamado no suporte?",
            "context": {
                "conversation_id": "chat-123",
                "external_message_id": "telegram-message-456",
                "locale": "pt-BR",
                "metadata": {"username": "maria"},
            },
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["schema_version"] == ASSISTANT_CONTRACT_VERSION
    assert body["request_id"] == "req-tg-001"
    assert body["user_id"] == "telegram-user-001"
    assert body["channel"] == "telegram"
    assert body["fallback"] is False


@pytest.mark.anyio
async def test_feedback_contract(client: httpx.AsyncClient) -> None:
    ask_response = await client.post(
        "/ask",
        json={
            "user_id": "web-user-001",
            "channel": "web",
            "message": "Como consultar status de chamado CHM-12345?",
        },
    )

    response = await client.post(
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
