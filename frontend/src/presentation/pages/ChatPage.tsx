import { SendHorizonal } from "lucide-react";
import { FormEvent, useEffect, useRef, useState } from "react";

import { useChat } from "../../application/hooks/useChat";
import { MessageBubble } from "../components/MessageBubble";

export function ChatPage() {
  const [input, setInput] = useState("");
  const { messages, isLoading, error, sendMessage, sendFeedback } = useChat();
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom whenever messages update or loading state changes
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

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
          <p>Canal Web conectado ao fluxo principal do assistente.</p>
        </div>
      </header>

      <div className="chat-log" role="log" aria-live="polite" aria-label="Histórico de mensagens">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} onFeedback={sendFeedback} />
        ))}
        {isLoading && (
          <div className="loading-line" aria-label="Aguardando resposta">
            <span className="typing-dots">
              <span /><span /><span />
            </span>
            Processando resposta…
          </div>
        )}
        {error && <div className="error-line" role="alert">{error}</div>}
        {/* Invisible anchor used for auto-scroll */}
        <div ref={bottomRef} />
      </div>

      <form className="composer" onSubmit={handleSubmit}>
        <input
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Pergunte sobre suporte interno"
          aria-label="Mensagem"
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading || !input.trim()} title="Enviar">
          <SendHorizonal size={18} />
        </button>
      </form>
    </section>
  );
}
