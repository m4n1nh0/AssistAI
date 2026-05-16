import { beforeEach, describe, expect, it, vi } from "vitest";

import { apiClient } from "../src/infrastructure/api/client";

const fetchMock = vi.fn();

beforeEach(() => {
  fetchMock.mockReset();
  vi.stubGlobal("fetch", fetchMock);
});

describe("apiClient", () => {
  it("envia perguntas para a API com payload JSON", async () => {
    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: () =>
        Promise.resolve({
          answer: "Resposta",
          fallback: false,
          intent: "procedimento",
          confidence: 0.94,
          sources: [],
          attendance_id: "att-1",
          message_id: "msg-1"
        })
    });

    const response = await apiClient.ask({
      user_id: "web-user",
      channel: "web",
      message: "Como reseto a senha?"
    });

    expect(fetchMock).toHaveBeenCalledWith("http://localhost:8000/ask", {
      headers: { "Content-Type": "application/json" },
      method: "POST",
      body: JSON.stringify({
        user_id: "web-user",
        channel: "web",
        message: "Como reseto a senha?"
      })
    });
    expect(response.message_id).toBe("msg-1");
  });

  it("envia feedback com o status escolhido", async () => {
    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ accepted: true })
    });

    await apiClient.sendFeedback({ message_id: "msg-1", useful: true });

    expect(fetchMock).toHaveBeenCalledWith("http://localhost:8000/feedback", {
      headers: { "Content-Type": "application/json" },
      method: "POST",
      body: JSON.stringify({ message_id: "msg-1", useful: true })
    });
  });

  it("lista atendimentos, documentos e metricas", async () => {
    fetchMock
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve([{ attendance_id: "att-1" }]) })
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve([{ document_id: "doc-1" }]) })
      .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ total_messages: 3 }) });

    await expect(apiClient.listAttendances()).resolves.toEqual([{ attendance_id: "att-1" }]);
    await expect(apiClient.listDocuments()).resolves.toEqual([{ document_id: "doc-1" }]);
    await expect(apiClient.metrics()).resolves.toEqual({ total_messages: 3 });

    expect(fetchMock).toHaveBeenNthCalledWith(1, "http://localhost:8000/attendances", {
      headers: { "Content-Type": "application/json" }
    });
    expect(fetchMock).toHaveBeenNthCalledWith(2, "http://localhost:8000/documents", {
      headers: { "Content-Type": "application/json" }
    });
    expect(fetchMock).toHaveBeenNthCalledWith(3, "http://localhost:8000/metrics", {
      headers: { "Content-Type": "application/json" }
    });
  });

  it("falha quando a API retorna erro HTTP", async () => {
    fetchMock.mockResolvedValueOnce({
      ok: false,
      status: 503,
      json: () => Promise.resolve({})
    });

    await expect(apiClient.listDocuments()).rejects.toThrow("API error 503");
  });
});
