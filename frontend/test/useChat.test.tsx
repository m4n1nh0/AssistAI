import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { useChat } from "../src/application/hooks/useChat";

const apiClientMock = vi.hoisted(() => ({
  ask: vi.fn(),
  sendFeedback: vi.fn()
}));

vi.mock("../src/infrastructure/api/client", () => ({
  apiClient: apiClientMock
}));

beforeEach(() => {
  apiClientMock.ask.mockReset();
  apiClientMock.sendFeedback.mockReset();
  vi.spyOn(globalThis.crypto, "randomUUID").mockReturnValue(
    "11111111-1111-4111-8111-111111111111"
  );
});

describe("useChat", () => {
  it("inicia com mensagem de boas-vindas", () => {
    const { result } = renderHook(() => useChat());

    expect(result.current.messages).toHaveLength(1);
    expect(result.current.messages[0]).toMatchObject({
      id: "welcome",
      role: "assistant"
    });
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it("ignora mensagens vazias", async () => {
    const { result } = renderHook(() => useChat());

    await act(async () => {
      await result.current.sendMessage("   ");
    });

    expect(apiClientMock.ask).not.toHaveBeenCalled();
    expect(result.current.messages).toHaveLength(1);
  });

  it("envia a mensagem do usuario e adiciona a resposta da API", async () => {
    apiClientMock.ask.mockResolvedValueOnce({
      answer: "Use o portal de senhas.",
      fallback: false,
      intent: "procedimento",
      confidence: 0.9,
      sources: [{ document_id: "doc-1", title: "Senha", version: "1.0", score: 0.87 }],
      attendance_id: "att-1",
      message_id: "assistant-message-id"
    });
    const { result } = renderHook(() => useChat());

    await act(async () => {
      await result.current.sendMessage("  preciso resetar a senha  ");
    });

    expect(apiClientMock.ask).toHaveBeenCalledWith({
      user_id: "web-user-001",
      channel: "web",
      message: "preciso resetar a senha"
    });
    expect(result.current.messages).toHaveLength(3);
    expect(result.current.messages[1]).toMatchObject({
      id: "11111111-1111-4111-8111-111111111111",
      role: "user",
      content: "preciso resetar a senha"
    });
    expect(result.current.messages[2]).toMatchObject({
      id: "assistant-message-id",
      role: "assistant",
      content: "Use o portal de senhas.",
      messageId: "assistant-message-id"
    });
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it("mostra erro quando a API falha", async () => {
    apiClientMock.ask.mockRejectedValueOnce(new Error("offline"));
    const { result } = renderHook(() => useChat());

    await act(async () => {
      await result.current.sendMessage("status do chamado");
    });

    expect(result.current.messages).toHaveLength(2);
    expect(result.current.error).toBe("Nao foi possivel falar com a API agora.");
    expect(result.current.isLoading).toBe(false);
  });

  it("encaminha feedback para a API", async () => {
    apiClientMock.sendFeedback.mockResolvedValueOnce(undefined);
    const { result } = renderHook(() => useChat());

    await act(async () => {
      await result.current.sendFeedback("msg-1", true);
    });

    expect(apiClientMock.sendFeedback).toHaveBeenCalledWith({ message_id: "msg-1", useful: true });
  });
});
