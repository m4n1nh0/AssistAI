import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { DocumentsPage } from "../src/presentation/pages/DocumentsPage";
import { HistoryPage } from "../src/presentation/pages/HistoryPage";
import { MetricsPage } from "../src/presentation/pages/MetricsPage";

const apiClientMock = vi.hoisted(() => ({
  listAttendances: vi.fn(),
  listDocuments: vi.fn(),
  metrics: vi.fn()
}));

vi.mock("../src/infrastructure/api/client", () => ({
  apiClient: apiClientMock
}));

beforeEach(() => {
  apiClientMock.listAttendances.mockReset();
  apiClientMock.listDocuments.mockReset();
  apiClientMock.metrics.mockReset();
});

describe("data pages", () => {
  it("carrega e atualiza documentos", async () => {
    const user = userEvent.setup();
    apiClientMock.listDocuments
      .mockResolvedValueOnce([
        {
          document_id: "doc-1",
          title: "FAQ",
          category: "Suporte",
          channel: "web",
          version: "1.0",
          status: "active",
          updated_at: "2026-05-16T10:00:00Z",
          source: "kb",
          owner: "TI",
          sensitivity: "internal",
          tags: []
        }
      ])
      .mockResolvedValueOnce([
        {
          document_id: "doc-2",
          title: "Politicas",
          category: "RH",
          channel: "web",
          version: "2.0",
          status: "draft",
          updated_at: "2026-05-16T10:00:00Z",
          source: "kb",
          owner: "RH",
          sensitivity: "internal",
          tags: []
        }
      ]);

    render(<DocumentsPage />);

    expect(await screen.findByRole("heading", { name: "FAQ" })).toBeInTheDocument();
    await user.click(screen.getByTitle("Atualizar"));
    expect(await screen.findByRole("heading", { name: "Politicas" })).toBeInTheDocument();
    expect(apiClientMock.listDocuments).toHaveBeenCalledTimes(2);
  });

  it("carrega e atualiza historico", async () => {
    const user = userEvent.setup();
    apiClientMock.listAttendances
      .mockResolvedValueOnce([
        {
          attendance_id: "att-1",
          user_id: "u1",
          channel: "web",
          escalated: false,
          started_at: "2026-05-16T10:00:00Z",
          message_count: 1
        }
      ])
      .mockResolvedValueOnce([
        {
          attendance_id: "att-2",
          user_id: "u2",
          channel: "telegram",
          escalated: true,
          started_at: "2026-05-16T10:00:00Z",
          message_count: 4
        }
      ]);

    render(<HistoryPage />);

    expect(await screen.findByText("att-1")).toBeInTheDocument();
    expect(screen.getByText("Automatizado")).toBeInTheDocument();
    await user.click(screen.getByTitle("Atualizar"));
    expect(await screen.findByText("att-2")).toBeInTheDocument();
    expect(screen.getByText("Escalonado")).toBeInTheDocument();
    expect(apiClientMock.listAttendances).toHaveBeenCalledTimes(2);
  });

  it("carrega indicadores e atualiza percentuais", async () => {
    const user = userEvent.setup();
    apiClientMock.metrics
      .mockResolvedValueOnce({
        total_attendances: 2,
        total_messages: 10,
        fallback_rate: 0.1,
        useful_feedback_rate: 0.5,
        escalated_attendances: 0,
        top_intents: {},
        top_documents: {},
        unanswered_questions: []
      })
      .mockResolvedValueOnce({
        total_attendances: 3,
        total_messages: 20,
        fallback_rate: 0.35,
        useful_feedback_rate: 0.8,
        escalated_attendances: 1,
        top_intents: {},
        top_documents: {},
        unanswered_questions: []
      });

    render(<MetricsPage />);

    expect(await screen.findByText("10")).toBeInTheDocument();
    expect(screen.getByText("10%")).toBeInTheDocument();
    await user.click(screen.getByTitle("Atualizar"));

    await waitFor(() => expect(screen.getByText("20")).toBeInTheDocument());
    expect(screen.getByText("35%")).toBeInTheDocument();
    expect(screen.getByText("80%")).toBeInTheDocument();
    expect(apiClientMock.metrics).toHaveBeenCalledTimes(2);
  });
});
