import type {
  AskRequest,
  AskResponse,
  AttendanceListItem,
  DocumentSummary,
  FeedbackRequest,
  MetricSummary
} from "../../domain/contracts";
import { appConfig } from "../../application/config";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${appConfig.apiUrl}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    },
    ...init
  });

  if (!response.ok) {
    throw new Error(`API error ${response.status}`);
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
  sendFeedback(payload: FeedbackRequest) {
    return request("/feedback", {
      method: "POST",
      body: JSON.stringify(payload)
    });
  },
  listAttendances() {
    return request<AttendanceListItem[]>("/attendances");
  },
  listDocuments() {
    return request<DocumentSummary[]>("/documents");
  },
  metrics() {
    return request<MetricSummary>("/metrics");
  }
};
