import { SendHorizonal } from "lucide-react";
import { FormEvent, useState } from "react";

import { useChat } from "../../application/hooks/useChat";
import { MessageBubble } from "../components/MessageBubble";

export function ChatPage() {
  const [input, setInput] = useState("");
  const { messages, isLoading, error, sendMessage, sendFeedback } = useChat();

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

      <div className="chat-log">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} onFeedback={sendFeedback} />
        ))}
        {isLoading && <div className="loading-line">Processando resposta...</div>}
        {error && <div className="error-line">{error}</div>}
      </div>

      <form className="composer" onSubmit={handleSubmit}>
        <input
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Pergunte sobre suporte interno"
          aria-label="Mensagem"
        />
        <button type="submit" disabled={isLoading || !input.trim()} title="Enviar">
          <SendHorizonal size={18} />
        </button>
      </form>
    </section>
  );
}

