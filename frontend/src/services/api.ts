export type ChatRequest = {
  user_id?: string;
  channel?: "web" | "telegram";
  message: string;
};

export type Source = {
  document_id: string;
  title: string;
  version: string;
  score: number;
};

export type ChatResponse = {
  attendance_id: string;
  message_id: string;
  answer: string;
  fallback: boolean;
  intent: string;
  confidence: number;
  sources: Source[];
  needs_human: boolean;
  suggested_actions: string[];
};

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api";

export async function sendMessage(payload: ChatRequest): Promise<ChatResponse> {
  const response = await fetch(`${API_URL}/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      user_id: payload.user_id ?? "web-user-001",
      channel: payload.channel ?? "web",
      message: payload.message,
    }),
  });

  if (!response.ok) {
    throw new Error("Nao foi possivel enviar a mensagem.");
  }

  return response.json();
}

export async function sendFeedback(messageId: string, useful: boolean) {
  const response = await fetch(`${API_URL}/feedback`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message_id: messageId, useful }),
  });

  if (!response.ok) {
    throw new Error("Nao foi possivel registrar o feedback.");
  }
}
