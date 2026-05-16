import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { MessageBubble } from "../src/presentation/components/MessageBubble";

describe("MessageBubble", () => {
  it("renderiza resposta do assistente com fontes e feedback", () => {
    render(
      <MessageBubble
        message={{
          id: "assistant-1",
          role: "assistant",
          content: "Procedimento encontrado.",
          messageId: "msg-1",
          sources: [{ document_id: "doc-1", title: "Manual", version: "2.1", score: 0.912 }]
        }}
        onFeedback={vi.fn()}
      />
    );

    expect(screen.getByText("Procedimento encontrado.")).toBeInTheDocument();
    expect(screen.getByText("Manual v2.1 (91%)")).toBeInTheDocument();
    expect(screen.getByLabelText("Feedback da resposta")).toBeInTheDocument();
  });

  it("renderiza mensagem do usuario sem feedback", () => {
    render(
      <MessageBubble
        message={{
          id: "user-1",
          role: "user",
          content: "Oi"
        }}
        onFeedback={vi.fn()}
      />
    );

    expect(screen.getByText("Oi")).toBeInTheDocument();
    expect(screen.queryByLabelText("Feedback da resposta")).not.toBeInTheDocument();
  });
});
