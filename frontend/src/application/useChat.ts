import { useMemo, useState } from "react";

import type { ChatMessage } from "../domain/types";
import { apiClient } from "../infrastructure/apiClient";

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      text: "Olá! Envie uma pergunta sobre suporte interno para começarmos."
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canSend = useMemo(() => !isLoading, [isLoading]);

  async function sendMessage(text: string) {
    const trimmed = text.trim();
    if (!trimmed || isLoading) {
      return;
    }

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: "user",
      text: trimmed
    };

    setMessages((current) => [...current, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.ask({
        user_id: "web-user-001",
        channel: "web",
        message: trimmed
      });

      setMessages((current) => [
        ...current,
        {
          id: response.message_id,
          role: "assistant",
          text: response.answer,
          sources: response.sources,
          fallback: response.fallback,
          messageId: response.message_id
        }
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro inesperado ao enviar mensagem.");
    } finally {
      setIsLoading(false);
    }
  }

  async function sendFeedback(messageId: string, useful: boolean) {
    await apiClient.sendFeedback(messageId, useful);
  }

  return {
    messages,
    isLoading,
    error,
    canSend,
    sendMessage,
    sendFeedback
  };
}
