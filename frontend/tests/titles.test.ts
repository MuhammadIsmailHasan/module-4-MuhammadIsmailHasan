import fc from "fast-check";
import { describe, expect, it } from "vitest";
import { pageTitle, panelTitle } from "@/lib/titles";

describe("document titles (Property 59)", () => {
  it("puts the brand first and cuts long names", () => {
    expect(pageTitle("Alpha Board")).toBe("RevoTask | Alpha Board");
    expect(pageTitle("")).toBe("RevoTask");
    fc.assert(fc.property(fc.string(), (n) => {
      const t = pageTitle(n);
      return (t === "RevoTask" || t.startsWith("RevoTask | ")) && t.length <= 71 && !/[\n\r]/.test(t);
    }));
  });
  it("shows the unread count only above zero", () => {
    expect(panelTitle("inbox", 3)).toBe("RevoTask | Inbox (3)");
    expect(panelTitle("inbox", 0)).toBe("RevoTask | Inbox");
    expect(panelTitle("activity", 5)).toBe("RevoTask | Activity");
  });
});
