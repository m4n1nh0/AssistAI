export type Channel = "web" | "telegram";

export const ASSISTANT_CONTRACT_VERSION = "assistant.ask.v1" as const;

export type AssistantContractVersion = typeof ASSISTANT_CONTRACT_VERSION;

export type Intent =
  | "saudacao"
  | "procedimento"
  | "solicitacao_humana"
  | "consulta_chamado"
  | "fora_de_escopo"
  | "desconhecida";

export interface Source {
  document_id: string;
  title: string;
  version: string;
  score: number;
}

export interface RequestContext {
  conversation_id?: string | null;
  external_message_id?: string | null;
  locale: string;
  metadata: Record<string, string>;
}

export interface AskRequest {
  schema_version?: AssistantContractVersion;
  request_id?: string | null;
  user_id: string;
  channel: Channel;
  message: string;
  context?: RequestContext;
}

export interface AskResponse {
  schema_version: AssistantContractVersion;
  request_id?: string | null;
  user_id: string;
  channel: Channel;
  answer: string;
  fallback: boolean;
  handoff_required: boolean;
  intent: Intent;
  confidence: number;
  sources: Source[];
  attendance_id: string;
  message_id: string;
  generated_at: string;
}

export interface FeedbackRequest {
  message_id: string;
  useful: boolean;
  comment?: string;
}

export interface AttendanceListItem {
  attendance_id: string;
  user_id: string;
  channel: Channel;
  escalated: boolean;
  started_at: string;
  message_count: number;
}

export interface DocumentSummary {
  document_id: string;
  title: string;
  category: string;
  channel: string;
  version: string;
  status: "active" | "inactive" | "draft";
  updated_at: string;
  source: string;
  owner: string;
  sensitivity: string;
  tags: string[];
}

export interface MetricSummary {
  total_attendances: number;
  total_messages: number;
  fallback_rate: number;
  useful_feedback_rate: number;
  escalated_attendances: number;
  top_intents: Record<string, number>;
  top_documents: Record<string, number>;
  unanswered_questions: string[];
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  fallback?: boolean;
  messageId?: string;
}

export interface IntegrationStatus {
  name: string;
  adapter: string;
  configured: boolean;
}

export interface ReadinessResponse {
  status: "ready";
  app: string;
  version: string;
  environment: string;
  integrations: IntegrationStatus[];
}
