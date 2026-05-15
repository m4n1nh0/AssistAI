import { useMemo, useRef, useState } from "react";
import type { FormEvent } from "react";
import { Bot, Check, Headphones, Loader2, Send, ThumbsDown, ThumbsUp, UserRound } from "lucide-react";

import { sendFeedback, sendMessage } from "../services/api";
import type { Source } from "../services/api";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  backendMessageId?: string;
  intent?: string;
  fallback?: boolean;
  sources?: Source[];
  actions?: string[];
};

export function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: crypto.randomUUID(),
      role: "assistant",
      content: "Ola! Sou seu assistente de atendimento. Posso ajudar com chamados, senha, prioridade e status.",
    },
  ]);
  const [input, setInput] = useState("");
  const [attendanceId, setAttendanceId] = useState<string | undefined>();
  const [isLoading, setIsLoading] = useState(false);
  const [feedbackSent, setFeedbackSent] = useState<Record<string, boolean>>({});
  const inputRef = useRef<HTMLTextAreaElement | null>(null);

  const lastIntent = useMemo(() => {
    return [...messages].reverse().find((message) => message.intent)?.intent;
  }, [messages]);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const text = input.trim();

    if (!text || isLoading) {
      return;
    }

    setMessages((current) => [
      ...current,
      {
        id: crypto.randomUUID(),
        role: "user",
        content: text,
      },
    ]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await sendMessage({ message: text });
      setAttendanceId(response.attendance_id);
      setMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: response.answer,
          backendMessageId: response.message_id,
          intent: response.intent,
          fallback: response.fallback,
          sources: response.sources,
          actions: response.suggested_actions,
        },
      ]);
    } catch {
      setMessages((current) => [
        ...current,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: "Tive uma falha ao falar com o servidor. Verifique se o backend esta rodando.",
        },
      ]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  }

  async function handleFeedback(messageId: string, useful: boolean) {
    await sendFeedback(messageId, useful);
    setFeedbackSent((current) => ({ ...current, [messageId]: true }));
  }

  return (
    <main className="app-shell">
      <section className="sidebar" aria-label="Resumo do atendimento">
        <div className="brand">
          <Headphones size={28} />
          <div>
            <h1>Atendimento IA</h1>
            <span>POC suporte interno</span>
          </div>
        </div>

        <div className="status-panel">
          <span className="status-dot" />
          <div>
            <strong>Fluxo ativo</strong>
            <p>FastAPI, RAG, feedback, Telegram e MCP simulado</p>
          </div>
        </div>

        <div className="meta-list">
          <div>
            <span>Atendimento</span>
            <strong>{attendanceId ?? "novo"}</strong>
          </div>
          <div>
            <span>Intencao</span>
            <strong>{lastIntent ?? "aguardando"}</strong>
          </div>
        </div>
      </section>

      <section className="chat-panel" aria-label="Chat de atendimento">
        <div className="messages">
          {messages.map((message) => (
            <article key={message.id} className={`message ${message.role}`}>
              <div className="avatar" aria-hidden="true">
                {message.role === "assistant" ? <Bot size={18} /> : <UserRound size={18} />}
              </div>
              <div className="bubble">
                <p>{message.content}</p>
                {message.fallback && <strong className="fallback-label">Fallback aplicado</strong>}
                {message.sources && message.sources.length > 0 && (
                  <div className="sources">
                    {message.sources.map((source) => (
                      <span key={source.document_id}>
                        {source.title} v{source.version} - score {source.score}
                      </span>
                    ))}
                  </div>
                )}
                {message.actions && message.actions.length > 0 && (
                  <div className="actions">
                    {message.actions.map((action) => (
                      <span key={action}>{action}</span>
                    ))}
                  </div>
                )}
                {message.role === "assistant" && message.backendMessageId && (
                  <div className="feedback-row">
                    {feedbackSent[message.backendMessageId] ? (
                      <span className="feedback-ok">
                        <Check size={14} /> Feedback registrado
                      </span>
                    ) : (
                      <>
                        <button type="button" onClick={() => handleFeedback(message.backendMessageId!, true)}>
                          <ThumbsUp size={15} />
                        </button>
                        <button type="button" onClick={() => handleFeedback(message.backendMessageId!, false)}>
                          <ThumbsDown size={15} />
                        </button>
                      </>
                    )}
                  </div>
                )}
              </div>
            </article>
          ))}

          {isLoading && (
            <article className="message assistant">
              <div className="avatar" aria-hidden="true">
                <Bot size={18} />
              </div>
              <div className="bubble typing">
                <Loader2 size={18} />
                Processando atendimento
              </div>
            </article>
          )}
        </div>

        <form className="composer" onSubmit={handleSubmit}>
          <textarea
            ref={inputRef}
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Digite sua pergunta..."
            rows={2}
          />
          <button type="submit" disabled={isLoading || input.trim().length === 0} aria-label="Enviar mensagem">
            <Send size={20} />
          </button>
        </form>
      </section>
    </main>
  );
}
