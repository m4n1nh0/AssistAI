import { ThumbsDown, ThumbsUp } from "lucide-react";
import { useState } from "react";

interface FeedbackButtonsProps {
  messageId: string;
  onFeedback: (messageId: string, useful: boolean) => Promise<void>;
}

export function FeedbackButtons({ messageId, onFeedback }: FeedbackButtonsProps) {
  const [selected, setSelected] = useState<"up" | "down" | null>(null);
  const [sending, setSending] = useState(false);
  const [failed, setFailed] = useState(false);

  async function handleFeedback(useful: boolean) {
    setSending(true);
    setFailed(false);
    try {
      await onFeedback(messageId, useful);
      setSelected(useful ? "up" : "down");
    } catch {
      setFailed(true);
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="feedback-actions" aria-label="Feedback da resposta">
      <button
        type="button"
        className={selected === "up" ? "icon-button selected" : "icon-button"}
        onClick={() => handleFeedback(true)}
        disabled={sending}
        title="Resposta util"
      >
        <ThumbsUp size={16} />
      </button>
      <button
        type="button"
        className={selected === "down" ? "icon-button selected" : "icon-button"}
        onClick={() => handleFeedback(false)}
        disabled={sending}
        title="Resposta nao util"
      >
        <ThumbsDown size={16} />
      </button>
      {selected && <span className="feedback-status">Feedback registrado.</span>}
      {failed && <span className="feedback-error">Falha ao registrar feedback.</span>}
    </div>
  );
}

