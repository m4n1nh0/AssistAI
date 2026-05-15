import type { ChatMessage } from "../../domain/contracts";
import { FeedbackButtons } from "./FeedbackButtons";

interface MessageBubbleProps {
  message: ChatMessage;
  feedback?: boolean;
  onFeedback: (messageId: string, useful: boolean) => Promise<void>;
}

export function MessageBubble({ message, feedback, onFeedback }: MessageBubbleProps) {
  const isAssistant = message.role === "assistant";

  return (
    <article className={isAssistant ? "message assistant" : "message user"}>
      <p>{message.content}</p>
      {message.fallback && <span className="message-badge">Escalonamento sugerido</span>}
      {message.sources && message.sources.length > 0 && (
        <div className="source-list">
          {message.sources.map((source) => (
            <span key={source.document_id}>
              {source.title} v{source.version} ({Math.round(source.score * 100)}%)
            </span>
          ))}
        </div>
      )}
      {isAssistant && message.messageId && (
        <FeedbackButtons messageId={message.messageId} selected={feedback} onFeedback={onFeedback} />
      )}
    </article>
  );
}
