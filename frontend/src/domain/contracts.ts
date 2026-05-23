/**
 * Contrato oficial de Pergunta e Resposta do Assistente Inteligente.
 * 
 * Este módulo define as interfaces TypeScript que padronizam a comunicação
 * entre Web, Telegram, API e Motor de IA, garantindo type-safety
 * e consistência com o backend (Pydantic models).
 *
 * Versão do Contrato: 1.0
 * Data: 2024-01-01
 */

// ============================================================================
// CONSTANTES
// ============================================================================

export const CONTRACT_VERSION = "1.0";

// ============================================================================
// TIPOS ENUMERADOS
// ============================================================================

export type Channel = "web" | "telegram";

export type Intent =
  | "saudacao"
  | "procedimento"
  | "solicitacao_humana"
  | "consulta_chamado"
  | "fora_de_escopo"
  | "desconhecida";

export type FallbackReason =
  | "low_score"
  | "no_sources"
  | "error"
  | "intent_out_of_scope"
  | "service_unavailable";

export type DocumentStatus = "active" | "inactive" | "draft";

export type ErrorCode =
  | "INVALID_REQUEST"
  | "QUESTION_TOO_LONG"
  | "UNSUPPORTED_CHANNEL"
  | "SERVICE_UNAVAILABLE"
  | "INTERNAL_ERROR"
  | "RATE_LIMIT_EXCEEDED";

// ============================================================================
// ENTRADA (REQUEST)
// ============================================================================

export interface RequestMetadata {
  timestamp: string; // ISO 8601 obrigatório
  user_agent?: string; // User agent do cliente
  ip_address?: string; // IP do cliente
  message_id?: string; // ID da mensagem (Telegram)
}

export interface AskRequest {
  version: string; // "1.0"
  question: string; // 1-1000 caracteres, obrigatório
  user_id?: string; // Identificador do usuário
  channel: Channel; // "web" ou "telegram", obrigatório
  session_id?: string; // ID da sessão
  conversation_id?: string; // ID da conversa para multi-turno
  request_id?: string; // ID único do request para rastreamento
  metadata: RequestMetadata; // Metadados obrigatórios
}

// ============================================================================
// SAÍDA (RESPONSE)
// ============================================================================

export interface SourceResponse {
  document_id: string; // ID do documento
  title: string; // Título do documento
  content: string; // Trecho relevante
  version: string; // Versão do documento
  score: number; // Score de relevância (0.0-1.0)
}

export interface ResponseMetadata {
  processing_time_ms: number; // Tempo de processamento
  model_used: string; // Ex: "gpt-4", "fallback"
  timestamp: string; // ISO 8601
}

export interface AskResponse {
  version: string; // "1.0"
  answer: string; // Resposta (max 4000 caracteres)
  sources: SourceResponse[]; // Até 5 fontes (RENOMEADO de Source)
  score: number; // Score geral (0.0-1.0)
  fallback: boolean; // Indica se foi fallback
  fallback_reason?: FallbackReason; // Razão do fallback
  conversation_id?: string; // ID da conversa para continuidade
  request_id?: string; // ID do request original (para rastreamento)
  attendance_id?: string; // ID do atendimento registrado
  message_id?: string; // ID da mensagem registrada para feedback
  metadata: ResponseMetadata; // Metadados da resposta
}

export interface ErrorDetail {
  field?: string; // Campo que gerou o erro
  message?: string; // Mensagem de erro
}

export interface ErrorResponse {
  version: string; // "1.0"
  error: {
    code: ErrorCode;
    message: string;
    details?: ErrorDetail;
  };
}

// ============================================================================
// FEEDBACK
// ============================================================================

export interface FeedbackRequest {
  message_id: string; // ID da mensagem para avaliação
  useful: boolean; // Útil ou não
  comment?: string; // Comentário opcional (max 1000 caracteres)
}

export interface FeedbackResponse {
  feedback_id: string; // ID do feedback registrado
  message_id: string; // ID da mensagem avaliada
  useful: boolean; // Valor registrado
  created_at: string; // ISO 8601
}

// ============================================================================
// HISTÓRICO DE MENSAGENS
// ============================================================================

export interface MessageResponse {
  message_id: string; // ID único da mensagem
  user_message: string; // Pergunta do usuário
  assistant_answer: string; // Resposta do assistente
  fallback: boolean; // Se usou fallback
  intent: Intent; // Intenção identificada
  confidence: number; // Confiança da identificação (0.0-1.0)
  sources: SourceResponse[]; // Fontes utilizadas
  created_at: string; // ISO 8601
}

// ============================================================================
// ATENDIMENTO (ATTENDANCE)
// ============================================================================

export interface AttendanceListItem {
  attendance_id: string; // ID único
  user_id: string; // ID do usuário
  channel: Channel; // Canal de origem
  escalated: boolean; // Se foi escalonado
  started_at: string; // ISO 8601
  message_count: number; // Quantidade de mensagens
}

export interface AttendanceDetailResponse {
  attendance_id: string; // ID único
  user_id: string; // ID do usuário
  channel: Channel; // Canal de origem
  escalated: boolean; // Se foi escalonado
  started_at: string; // ISO 8601
  messages: MessageResponse[]; // Lista de mensagens da conversa
}

// ============================================================================
// DOCUMENTOS
// ============================================================================

export interface DocumentSummary {
  document_id: string;
  title: string;
  version: string;
  status: DocumentStatus; // "active" | "inactive" | "draft"
  created_at: string; // ISO 8601
  updated_at: string; // ISO 8601
}

export interface DocumentCreateRequest {
  title: string; // Título do documento
  category: string; // Categoria
  channel?: string; // Canal (default: "both")
  version?: string; // Versão (default: "1.0")
  status?: DocumentStatus; // Status (default: "active")
  source?: string; // Fonte (default: "manual")
  owner?: string; // Proprietário (default: "suporte")
  sensitivity?: string; // Sensibilidade (default: "interno")
  content: string; // Conteúdo do documento
  tags?: string[]; // Tags para categorização
}

export interface DocumentResponse {
  document_id: string;
  title: string;
  category: string;
  channel: string;
  version: string;
  status: DocumentStatus;
  updated_at: string;
  source: string;
  owner: string;
  sensitivity: string;
  tags: string[];
}

export interface ReindexResponse {
  indexed_documents: number;
  indexed_chunks: number;
}

// ============================================================================
// PAGINAÇÃO
// ============================================================================

export interface PaginationMeta {
  total: number; // Total de itens
  page: number; // Página atual (1-indexed)
  page_size: number; // Itens por página
  has_more: boolean; // Se há mais páginas
}

export interface PaginatedResponse<T> {
  items: T[]; // Itens da página
  meta: PaginationMeta; // Metadados de paginação
}

// ============================================================================
// MÉTRICAS
// ============================================================================

export interface MetricSummary {
  total_attendances: number;
  total_messages: number;
  fallback_rate: number; // Percentual
  useful_feedback_rate: number; // Percentual
  escalated_attendances: number;
  top_intents: Record<string, number>;
  top_documents: Record<string, number>;
  unanswered_questions: string[];
}

// ============================================================================
// CHAT (APRESENTAÇÃO)
// ============================================================================

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: SourceResponse[];
  fallback?: boolean;
  messageId?: string;
  timestamp: string;
}

// ============================================================================
// UTILITÁRIOS: FACTORY
// ============================================================================

/**
 * Factory para criar AskRequest com valores padrão validados.
 */
export function createAskRequest(
  question: string,
  channel: Channel,
  userId?: string,
  conversationId?: string
): AskRequest {
  return {
    version: CONTRACT_VERSION,
    question: question.trim(),
    user_id: userId,
    channel,
    conversation_id: conversationId,
    request_id: generateRequestId(), // NOVO: gerar ID único
    metadata: {
      timestamp: new Date().toISOString(),
      user_agent: typeof navigator !== "undefined" ? navigator.userAgent : undefined,
    },
  };
}

/**
 * Gerar ID único para rastreamento de request.
 */
function generateRequestId(): string {
  return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

// ============================================================================
// UTILITÁRIOS: PARSING
// ============================================================================

/**
 * Parsear string ISO 8601 para Date.
 */
export function parseISOTimestamp(isoString: string): Date {
  return new Date(isoString);
}

/**
 * Formatar Date para ISO 8601 string.
 */
export function formatToISOTimestamp(date: Date): string {
  return date.toISOString();
}

// ============================================================================
// UTILITÁRIOS: TYPE GUARDS
// ============================================================================

/**
 * Type guard para validar AskResponse.
 */
export function isAskResponse(data: any): data is AskResponse {
  return (
    data &&
    typeof data === "object" &&
    "version" in data &&
    "answer" in data &&
    "sources" in data &&
    "score" in data &&
    "fallback" in data &&
    "metadata" in data &&
    Array.isArray(data.sources)
  );
}

/**
 * Type guard para validar ErrorResponse.
 */
export function isErrorResponse(data: any): data is ErrorResponse {
  return (
    data &&
    typeof data === "object" &&
    "version" in data &&
    "error" in data &&
    typeof data.error === "object" &&
    "code" in data.error &&
    "message" in data.error
  );
}

/**
 * Type guard para validar SourceResponse.
 */
export function isSourceResponse(data: any): data is SourceResponse {
  return (
    data &&
    typeof data === "object" &&
    "document_id" in data &&
    "title" in data &&
    "content" in data &&
    "score" in data &&
    "version" in data &&
    typeof data.score === "number" &&
    data.score >= 0 &&
    data.score <= 1
  );
}

/**
 * Type guard para validar MessageResponse.
 */
export function isMessageResponse(data: any): data is MessageResponse {
  return (
    data &&
    typeof data === "object" &&
    "message_id" in data &&
    "user_message" in data &&
    "assistant_answer" in data &&
    "fallback" in data &&
    "intent" in data &&
    "confidence" in data &&
    "sources" in data &&
    "created_at" in data &&
    Array.isArray(data.sources)
  );
}

/**
 * Type guard para validar PaginatedResponse.
 */
export function isPaginatedResponse<T>(data: any): data is PaginatedResponse<T> {
  return (
    data &&
    typeof data === "object" &&
    "items" in data &&
    "meta" in data &&
    Array.isArray(data.items) &&
    typeof data.meta === "object" &&
    "total" in data.meta &&
    "page" in data.meta &&
    "page_size" in data.meta &&
    "has_more" in data.meta
  );
}

