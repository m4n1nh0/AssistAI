import { ThumbsDown, ThumbsUp } from "lucide-react";
import { useState } from "react";

interface FeedbackButtonsProps {
  messageId: string;
  onFeedback: (messageId: string, useful: boolean) => Promise<void>;
}

export function FeedbackButtons({ messageId, onFeedback }: FeedbackButtonsProps) {
  const [selected, setSelected] = useState<"up" | "down" | null>(null);

  async function handleFeedback(useful: boolean) {
    setSelected(useful ? "up" : "down");
    await onFeedback(messageId, useful);
  }

  return (
    <div className="feedback-actions" aria-label="Feedback da resposta">
      <button
        type="button"
        className={selected === "up" ? "icon-button selected" : "icon-button"}
        onClick={() => handleFeedback(true)}
        title="Resposta util"
      >
        <ThumbsUp size={16} />
      </button>
      <button
        type="button"
        className={selected === "down" ? "icon-button selected" : "icon-button"}
        onClick={() => handleFeedback(false)}
        title="Resposta nao util"
      >
        <ThumbsDown size={16} />
      </button>
    </div>
  );
}

