import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { FeedbackButtons } from "../src/presentation/components/FeedbackButtons";

describe("FeedbackButtons", () => {
  it("marca feedback positivo e negativo", async () => {
    const user = userEvent.setup();
    const onFeedback = vi.fn().mockResolvedValue(undefined);
    render(<FeedbackButtons messageId="msg-1" onFeedback={onFeedback} />);

    const up = screen.getByTitle("Resposta util");
    const down = screen.getByTitle("Resposta nao util");

    await user.click(up);
    expect(onFeedback).toHaveBeenCalledWith("msg-1", true);
    expect(up).toHaveClass("selected");

    await user.click(down);
    expect(onFeedback).toHaveBeenCalledWith("msg-1", false);
    expect(down).toHaveClass("selected");
    expect(up).not.toHaveClass("selected");
  });
});
