import { describe, expect, it } from "vitest";

import { formatPercent } from "../src/shared/format";

describe("formatPercent", () => {
  it("formata fracao como percentual arredondado", () => {
    expect(formatPercent(0.756)).toBe("76%");
  });
});
