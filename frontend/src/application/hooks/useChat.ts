import { useMemo, useState } from "react";

import type { ChatMessage } from "../../domain/contracts";
import { apiClient } from "../../infrastructure/api/client";

const USER_ID = "web-user-001";

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      content: "Ola. Posso ajudar com abertura de chamado, reset de senha ou status de atendimento."
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function sendMessage(content: string) {
    const trimmed = content.trim();
    if (!trimmed || isLoading) {
      return;
    }

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      content: trimmed
    };

    setMessages((current) => [...current, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const request = {
        version: "1.0",
        question: trimmed,
        user_id: USER_ID,
        channel: "web",
        metadata: {
          timestamp: new Date().toISOString(),
          user_agent: navigator.userAgent,
        },
      };

      const response = await apiClient.ask(request);
      const assistantId = response.request_id ?? crypto.randomUUID();

      setMessages((current) => [
        ...current,
        {
          id: assistantId,
          role: "assistant",
          content: response.answer,
          fallback: response.fallback,
          sources: response.sources,
          messageId: assistantId,
          timestamp: new Date().toISOString(),
        }
      ]);
    } catch {
      setError("Nao foi possivel falar com a API agora.");
    } finally {
      setIsLoading(false);
    }
  }

  async function sendFeedback(messageId: string, useful: boolean) {
    await apiClient.sendFeedback({ message_id: messageId, useful });
  }

  return useMemo(
    () => ({
      messages,
      isLoading,
      error,
      sendMessage,
      sendFeedback
    }),
    [messages, isLoading, error]
  );
}

