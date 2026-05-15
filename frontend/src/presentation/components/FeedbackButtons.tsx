import { ThumbsDown, ThumbsUp } from "lucide-react";
import { useState } from "react";

interface FeedbackButtonsProps {
  messageId: string;
  selected?: boolean;
  onFeedback: (messageId: string, useful: boolean) => Promise<void>;
}

export function FeedbackButtons({ messageId, selected, onFeedback }: FeedbackButtonsProps) {
  const [localSelection, setLocalSelection] = useState<"up" | "down" | null>(
    selected === undefined ? null : selected ? "up" : "down"
  );
  const [isSending, setIsSending] = useState(false);

  async function handleFeedback(useful: boolean) {
    setLocalSelection(useful ? "up" : "down");
    setIsSending(true);
    try {
      await onFeedback(messageId, useful);
    } finally {
      setIsSending(false);
    }
  }

  return (
    <div className="feedback-actions" aria-label="Feedback da resposta">
      <button
        type="button"
        className={localSelection === "up" ? "icon-button selected" : "icon-button"}
        onClick={() => handleFeedback(true)}
        disabled={isSending}
        title="Resposta util"
      >
        <ThumbsUp size={16} />
      </button>
      <button
        type="button"
        className={localSelection === "down" ? "icon-button selected" : "icon-button"}
        onClick={() => handleFeedback(false)}
        disabled={isSending}
        title="Resposta nao util"
      >
        <ThumbsDown size={16} />
      </button>
    </div>
  );
}
