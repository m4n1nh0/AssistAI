import { useMemo, useState } from "react";

import type { ChatMessage } from "../../domain/contracts";
import { apiClient } from "../../infrastructure/api/client";

const USER_ID = "web-user-001";

export function useChat() {
  const [conversationId, setConversationId] = useState<string | undefined>();
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
      const response = await apiClient.ask({
        question: trimmed,
        channel: "web",
        conversation_id: conversationId,
        user: { id: USER_ID },
        metadata: { source: "chat-web" }
      });
      setConversationId(response.conversation_id);

      setMessages((current) => [
        ...current,
        {
          id: response.message_id,
          role: "assistant",
          content: response.answer,
          fallback: response.status === "fallback",
          sources: response.sources,
          messageId: response.message_id
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

