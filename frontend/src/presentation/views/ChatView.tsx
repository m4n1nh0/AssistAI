import { Send, ThumbsDown, ThumbsUp } from "lucide-react";
import { FormEvent, useState } from "react";

import { useChat } from "../../application/useChat";

export function ChatView() {
  const [input, setInput] = useState("");
  const { messages, isLoading, error, canSend, sendMessage, sendFeedback } = useChat();

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await sendMessage(input);
    setInput("");
  }

  return (
    <div className="workspace chat-layout">
      <header className="workspace-header">
        <div>
          <p>Canal Web</p>
          <h1>Chat de atendimento</h1>
        </div>
        <span className="status-pill">RAG inicial</span>
      </header>

      <section className="message-list" aria-live="polite">
        {messages.map((message) => (
          <article key={message.id} className={`message ${message.role}`}>
            <p>{message.text}</p>

            {message.sources && message.sources.length > 0 && (
              <div className="sources">
                {message.sources.map((source) => (
                  <span key={`${source.document_id}-${source.version}`}>
                    {source.title} v{source.version} · score {source.score}
                  </span>
                ))}
              </div>
            )}

            {message.role === "assistant" && message.messageId && (
              <div className="feedback-actions">
                <button type="button" title="Marcar como útil" onClick={() => void sendFeedback(message.messageId!, true)}>
                  <ThumbsUp size={16} />
                </button>
                <button type="button" title="Marcar como não útil" onClick={() => void sendFeedback(message.messageId!, false)}>
                  <ThumbsDown size={16} />
                </button>
              </div>
            )}
          </article>
        ))}
        {isLoading && <span className="typing">Processando pergunta...</span>}
        {error && <span className="error-text">{error}</span>}
      </section>

      <form className="composer" onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Digite sua pergunta sobre suporte interno"
          aria-label="Mensagem"
        />
        <button type="submit" disabled={!canSend || input.trim().length === 0} title="Enviar mensagem">
          <Send size={18} />
        </button>
      </form>
    </div>
  );
}
