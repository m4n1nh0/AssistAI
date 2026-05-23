import ReactMarkdown from "react-markdown";

import type { ChatMessage } from "../../domain/contracts";
import { FeedbackButtons } from "./FeedbackButtons";

interface MessageBubbleProps {
  message: ChatMessage;
  onFeedback: (messageId: string, useful: boolean) => Promise<void>;
}

export function MessageBubble({ message, onFeedback }: MessageBubbleProps) {
  const isAssistant = message.role === "assistant";

  return (
    <article className={isAssistant ? "message assistant" : "message user"}>
      {isAssistant ? (
        <ReactMarkdown>{message.content}</ReactMarkdown>
      ) : (
        <p>{message.content}</p>
      )}
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
        <FeedbackButtons messageId={message.messageId} onFeedback={onFeedback} />
      )}
    </article>
  );
}
