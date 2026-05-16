from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import create_app


class TestE2EIntegration:
    def setup_method(self) -> None:
        self.client = TestClient(create_app())

    def test_health_endpoint(self) -> None:
        response = self.client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_ask_and_feedback_flow(self) -> None:
        ask_resp = self.client.post(
            "/ask",
            json={
                "user_id": "e2e-user",
                "channel": "web",
                "message": "Como abrir chamado no suporte?",
            },
        )
        assert ask_resp.status_code == 200
        ask_body = ask_resp.json()
        assert ask_body["answer"]
        assert ask_body["fallback"] is False
        assert ask_body["sources"]
        assert ask_body["attendance_id"].startswith("att-")
        assert ask_body["message_id"].startswith("msg-")

        feedback_resp = self.client.post(
            "/feedback",
            json={
                "message_id": ask_body["message_id"],
                "useful": True,
                "comment": "Respondeu corretamente.",
            },
        )
        assert feedback_resp.status_code == 200
        feedback_body = feedback_resp.json()
        assert feedback_body["feedback_id"].startswith("fbk-")
        assert feedback_body["useful"] is True

    def test_ask_fallback_flow(self) -> None:
        response = self.client.post(
            "/ask",
            json={
                "user_id": "e2e-user",
                "channel": "web",
                "message": "Qual e a capital do Brasil?",
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["fallback"] is True
        assert body["sources"] == []
        assert "nao encontrei" in body["answer"].lower()

    def test_attendances_list_and_detail(self) -> None:
        self.client.post(
            "/ask",
            json={
                "user_id": "e2e-att",
                "channel": "web",
                "message": "Como resetar senha?",
            },
        )

        list_resp = self.client.get("/attendances")
        assert list_resp.status_code == 200
        attendances = list_resp.json()
        assert len(attendances) >= 1

        att_id = attendances[0]["attendance_id"]
        detail_resp = self.client.get(f"/attendances/{att_id}")
        assert detail_resp.status_code == 200
        detail = detail_resp.json()
        assert detail["attendance_id"] == att_id
        assert len(detail["messages"]) >= 1

    def test_documents_list(self) -> None:
        response = self.client.get("/documents")
        assert response.status_code == 200
        docs = response.json()
        assert len(docs) >= 4

    def test_documents_create_and_reindex(self) -> None:
        create_resp = self.client.post(
            "/documents",
            json={
                "title": "Documento E2E",
                "category": "teste",
                "content": "Conteudo de teste para validacao E2E.",
                "tags": ["e2e", "teste"],
            },
        )
        assert create_resp.status_code == 201
        doc = create_resp.json()
        assert doc["title"] == "Documento E2E"

        reindex_resp = self.client.post("/documents/reindex")
        assert reindex_resp.status_code == 200
        reindex_data = reindex_resp.json()
        assert reindex_data["indexed_documents"] >= 5

    def test_metrics_endpoint(self) -> None:
        self.client.post(
            "/ask",
            json={
                "user_id": "e2e-metrics",
                "channel": "web",
                "message": "Como abrir chamado?",
            },
        )

        response = self.client.get("/metrics")
        assert response.status_code == 200
        metrics = response.json()
        assert metrics["total_attendances"] >= 1
        assert metrics["total_messages"] >= 1
        assert "fallback_rate" in metrics
        assert "top_intents" in metrics

    def test_telegram_webhook(self) -> None:
        response = self.client.post(
            "/telegram/webhook",
            json={
                "user_id": "tg-e2e-user",
                "message": "Como abrir chamado?",
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["answer"]
        assert body["attendance_id"].startswith("att-")

    def test_multiple_users_independent(self) -> None:
        r1 = self.client.post(
            "/ask",
            json={
                "user_id": "user-a",
                "channel": "web",
                "message": "Como abrir chamado?",
            },
        )
        r2 = self.client.post(
            "/ask",
            json={
                "user_id": "user-b",
                "channel": "web",
                "message": "Como resetar senha?",
            },
        )

        assert r1.json()["attendance_id"] != r2.json()["attendance_id"]

    def test_full_flow_ask_attendances_documents_metrics(self) -> None:
        self.client.post(
            "/ask",
            json={
                "user_id": "e2e-full",
                "channel": "web",
                "message": "Como abrir chamado?",
            },
        )
        self.client.post(
            "/ask",
            json={
                "user_id": "e2e-full",
                "channel": "web",
                "message": "O que e Python?",
            },
        )
        self.client.post(
            "/ask",
            json={
                "user_id": "e2e-full",
                "channel": "web",
                "message": "Quero falar com um humano",
            },
        )

        atts = self.client.get("/attendances").json()
        assert len(atts) >= 3

        docs = self.client.get("/documents").json()
        assert len(docs) >= 4

        metrics = self.client.get("/metrics").json()
        assert metrics["total_messages"] >= 3
