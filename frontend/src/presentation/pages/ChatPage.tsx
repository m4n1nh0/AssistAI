import { RotateCcw, SendHorizonal, Server } from "lucide-react";
import { FormEvent, useEffect, useMemo, useState } from "react";

import { useChat } from "../../application/hooks/useChat";
import type { ReadinessResponse } from "../../domain/contracts";
import { apiClient } from "../../infrastructure/api/client";
import { MessageBubble } from "../components/MessageBubble";

const suggestions = [
  "Como abrir chamado no suporte?",
  "Como solicitar reset de senha?",
  "Como consultar status de chamado CHM-12345?"
];

export function ChatPage() {
  const [input, setInput] = useState("");
  const [readiness, setReadiness] = useState<ReadinessResponse | null>(null);
  const [readinessError, setReadinessError] = useState(false);
  const {
    session,
    messages,
    isLoading,
    error,
    feedbackByMessage,
    sendMessage,
    sendFeedback,
    resetConversation
  } = useChat();

  const configuredIntegrations = useMemo(
    () => readiness?.integrations.filter((item) => item.configured).length ?? 0,
    [readiness]
  );

  useEffect(() => {
    apiClient
      .readiness()
      .then((response) => {
        setReadiness(response);
        setReadinessError(false);
      })
      .catch(() => setReadinessError(true));
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const value = input;
    setInput("");
    await sendMessage(value);
  }

  return (
    <section className="workspace chat-workspace">
      <header className="workspace-header">
        <div>
          <h1>Chat de atendimento</h1>
          <p>Sessao {session.conversationId}</p>
        </div>
        <div className={readinessError ? "api-status offline" : "api-status"}>
          <Server size={16} />
          <span>
            {readinessError
              ? "API indisponivel"
              : readiness
                ? `${readiness.app} ${readiness.version} - ${configuredIntegrations} integracoes`
                : "Verificando API"}
          </span>
        </div>
      </header>

      <div className="chat-log">
        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            message={message}
            feedback={message.messageId ? feedbackByMessage[message.messageId] : undefined}
            onFeedback={sendFeedback}
          />
        ))}
        {isLoading && <div className="loading-line">Processando resposta...</div>}
        {error && <div className="error-line">{error}</div>}
      </div>

      <div className="suggestion-row" aria-label="Perguntas sugeridas">
        {suggestions.map((suggestion) => (
          <button
            key={suggestion}
            type="button"
            onClick={() => setInput(suggestion)}
            disabled={isLoading}
          >
            {suggestion}
          </button>
        ))}
      </div>

      <form className="composer" onSubmit={handleSubmit}>
        <button
          className="composer-secondary"
          type="button"
          onClick={resetConversation}
          title="Limpar conversa"
          disabled={isLoading}
        >
          <RotateCcw size={18} />
        </button>
        <input
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Pergunte sobre suporte interno"
          aria-label="Mensagem"
          maxLength={2000}
        />
        <button type="submit" disabled={isLoading || !input.trim()} title="Enviar">
          <SendHorizonal size={18} />
        </button>
      </form>
    </section>
  );
}
