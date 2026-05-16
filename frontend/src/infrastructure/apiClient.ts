import type {
  AskRequest,
  AskResponse,
  AttendanceSummary,
  DocumentCreateRequest,
  DocumentItem,
  MetricsSummary,
  ReindexResponse
} from "../domain/types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers
    },
    ...options
  });

  if (!response.ok) {
    throw new Error(`Erro ${response.status} ao chamar ${path}`);
  }

  return response.json() as Promise<T>;
}

export const apiClient = {
  ask(payload: AskRequest) {
    return request<AskResponse>("/ask", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },
  sendFeedback(messageId: string, useful: boolean) {
    return request<{ feedback_id: string }>("/feedback", {
      method: "POST",
      body: JSON.stringify({ message_id: messageId, useful })
    });
  },
  listAttendances() {
    return request<{ items: AttendanceSummary[] }>("/attendances");
  },
  listDocuments() {
    return request<{ items: DocumentItem[] }>("/documents");
  },
  createDocument(payload: DocumentCreateRequest) {
    return request<DocumentItem>("/documents", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },
  reindexDocuments() {
    return request<ReindexResponse>("/documents/reindex", {
      method: "POST"
    });
  },
  getMetrics() {
    return request<MetricsSummary>("/metrics");
  }
};
