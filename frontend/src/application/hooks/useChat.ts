import { useMemo, useState } from "react";

import type { ChatMessage } from "../../domain/contracts";
import { apiClient } from "../../infrastructure/api/client";
import { createRequestId, getWebSession } from "../session/webSession";

const WELCOME_MESSAGE: ChatMessage = {
  id: "welcome",
  role: "assistant",
  content: "Ola. Posso ajudar com abertura de chamado, reset de senha ou status de atendimento."
};

export function useChat() {
  const [session] = useState(() => getWebSession());
  const [messages, setMessages] = useState<ChatMessage[]>([WELCOME_MESSAGE]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [feedbackByMessage, setFeedbackByMessage] = useState<Record<string, boolean>>({});

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
        schema_version: "assistant.ask.v1",
        request_id: createRequestId(),
        user_id: session.userId,
        channel: "web",
        message: trimmed,
        context: {
          conversation_id: session.conversationId,
          locale: "pt-BR",
          metadata: {
            origin: "web-chat"
          }
        }
      });

      setMessages((current) => [
        ...current,
        {
          id: response.message_id,
          role: "assistant",
          content: response.answer,
          fallback: response.fallback,
          sources: response.sources,
          messageId: response.message_id
        }
      ]);
    } catch (unknownError) {
      const message = unknownError instanceof Error ? unknownError.message : "";
      setError(
        message ? `Nao foi possivel falar com a API agora. ${message}` : "Nao foi possivel falar com a API agora."
      );
    } finally {
      setIsLoading(false);
    }
  }

  async function sendFeedback(messageId: string, useful: boolean) {
    await apiClient.sendFeedback({ message_id: messageId, useful });
    setFeedbackByMessage((current) => ({ ...current, [messageId]: useful }));
  }

  function resetConversation() {
    setMessages([WELCOME_MESSAGE]);
    setError(null);
    setFeedbackByMessage({});
  }

  return useMemo(
    () => ({
      session,
      messages,
      isLoading,
      error,
      feedbackByMessage,
      sendMessage,
      sendFeedback,
      resetConversation
    }),
    [session, messages, isLoading, error, feedbackByMessage]
  );
}
