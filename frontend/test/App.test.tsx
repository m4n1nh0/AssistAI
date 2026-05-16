import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { App } from "../src/presentation/App";

const apiClientMock = vi.hoisted(() => ({
  listAttendances: vi.fn(),
  listDocuments: vi.fn(),
  metrics: vi.fn()
}));

vi.mock("../src/infrastructure/api/client", () => ({
  apiClient: apiClientMock
}));

beforeEach(() => {
  apiClientMock.listAttendances.mockResolvedValue([
    {
      attendance_id: "att-1",
      user_id: "user-1",
      channel: "web",
      escalated: false,
      started_at: "2026-05-16T10:00:00Z",
      message_count: 2
    },
    {
      attendance_id: "att-2",
      user_id: "user-2",
      channel: "telegram",
      escalated: true,
      started_at: "2026-05-16T11:00:00Z",
      message_count: 5
    }
  ]);
  apiClientMock.listDocuments.mockResolvedValue([
    {
      document_id: "doc-1",
      title: "Reset de senha",
      category: "Suporte",
      channel: "web",
      version: "1.0",
      status: "active",
      updated_at: "2026-05-16T10:00:00Z",
      source: "kb",
      owner: "TI",
      sensitivity: "internal",
      tags: ["senha"]
    }
  ]);
  apiClientMock.metrics.mockResolvedValue({
    total_attendances: 12,
    total_messages: 40,
    fallback_rate: 0.25,
    useful_feedback_rate: 0.75,
    escalated_attendances: 3,
    top_intents: {},
    top_documents: {},
    unanswered_questions: []
  });
});

describe("App", () => {
  it("exibe o chat como tela inicial", () => {
    render(<App />);

    expect(screen.getByRole("heading", { name: "Chat de atendimento" })).toBeInTheDocument();
    expect(screen.getByText("AssistAI")).toBeInTheDocument();
  });

  it("navega entre historico, documentos e indicadores", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole("button", { name: "Historico" }));
    expect(await screen.findByText("att-1")).toBeInTheDocument();
    expect(screen.getByText("Automatizado")).toBeInTheDocument();
    expect(screen.getByText("Escalonado")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Documentos" }));
    expect(await screen.findByRole("heading", { name: "Reset de senha" })).toBeInTheDocument();
    expect(screen.getByText("Suporte")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Indicadores" }));
    expect(await screen.findByText("40")).toBeInTheDocument();
    expect(screen.getByText("25%")).toBeInTheDocument();
    expect(screen.getByText("75%")).toBeInTheDocument();

    await waitFor(() => {
      expect(apiClientMock.listAttendances).toHaveBeenCalledTimes(1);
      expect(apiClientMock.listDocuments).toHaveBeenCalledTimes(1);
      expect(apiClientMock.metrics).toHaveBeenCalledTimes(1);
    });
  });
});
