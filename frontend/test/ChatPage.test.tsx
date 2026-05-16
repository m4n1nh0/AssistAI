import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { ChatPage } from "../src/presentation/pages/ChatPage";

const chatMock = vi.hoisted(() => ({
  messages: [
    {
      id: "welcome",
      role: "assistant" as const,
      content: "Ola."
    }
  ],
  isLoading: false,
  error: null as string | null,
  sendMessage: vi.fn(),
  sendFeedback: vi.fn()
}));

vi.mock("../src/application/hooks/useChat", () => ({
  useChat: () => chatMock
}));

beforeEach(() => {
  chatMock.messages = [
    {
      id: "welcome",
      role: "assistant",
      content: "Ola."
    }
  ];
  chatMock.isLoading = false;
  chatMock.error = null;
  chatMock.sendMessage.mockReset();
  chatMock.sendFeedback.mockReset();
});

describe("ChatPage", () => {
  it("envia a mensagem digitada e limpa o campo", async () => {
    const user = userEvent.setup();
    chatMock.sendMessage.mockResolvedValue(undefined);
    render(<ChatPage />);

    const input = screen.getByLabelText("Mensagem");
    await user.type(input, "Abrir chamado");
    await user.click(screen.getByTitle("Enviar"));

    expect(chatMock.sendMessage).toHaveBeenCalledWith("Abrir chamado");
    expect(input).toHaveValue("");
  });

  it("bloqueia envio vazio e mostra estados de carregamento e erro", () => {
    chatMock.isLoading = true;
    chatMock.error = "Falha";
    render(<ChatPage />);

    expect(screen.getByTitle("Enviar")).toBeDisabled();
    expect(screen.getByText("Processando resposta...")).toBeInTheDocument();
    expect(screen.getByText("Falha")).toBeInTheDocument();
  });
});
