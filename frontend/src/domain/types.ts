export type Channel = "web" | "telegram";
export type Intent = "saudacao" | "procedimento" | "solicitacao_humana" | "fora_de_escopo" | "desconhecida";

export interface Source {
  document_id: string;
  title: string;
  version: string;
  score: number;
}

export interface AskRequest {
  user_id: string;
  channel: Channel;
  message: string;
}

export interface AskResponse {
  answer: string;
  fallback: boolean;
  intent: Intent;
  confidence: number;
  sources: Source[];
  attendance_id: string;
  message_id: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  text: string;
  sources?: Source[];
  fallback?: boolean;
  messageId?: string;
}

export interface AttendanceSummary {
  id: string;
  user_id: string;
  channel: Channel;
  total_messages: number;
  created_at: string;
}

export interface DocumentItem {
  id: string;
  title: string;
  category: string;
  channel: string;
  version: string;
  status: "draft" | "active" | "inactive";
  source: string;
  owner: string;
  sensitivity: string;
  content: string;
  tags: string[];
  updated_at: string;
}

export interface DocumentCreateRequest {
  title: string;
  category: string;
  content: string;
  channel: string;
  version: string;
  status: "draft" | "active" | "inactive";
  source: string;
  owner: string;
  sensitivity: string;
  tags: string[];
}

export interface ReindexResponse {
  indexed_documents: number;
  indexed_chunks: number;
}

export interface MetricsSummary {
  total_attendances: number;
  total_messages: number;
  fallback_rate: number;
  useful_feedback_rate: number | null;
  top_intents: Record<string, number>;
}
