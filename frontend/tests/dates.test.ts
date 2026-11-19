import fc from "fast-check";
import { describe, expect, it } from "vitest";
import { isRangeValid, minSelectable, normalizeRange, toIso, fromIso, withStart } from "@/lib/dates";

const day = fc.integer({ min: 0, max: 400 }).map((n) => toIso(new Date(2026, 0, 1 + n)));

describe("dates", () => {
  it("round-trips ISO days", () => {
    fc.assert(fc.property(day, (d) => toIso(fromIso(d)) === d));
  });

  it("treats empty and same-day ranges as valid", () => {
    expect(isRangeValid("", "")).toBe(true);
    expect(isRangeValid("2026-11-19", "")).toBe(true);
    expect(isRangeValid("2026-11-19", "2026-11-19")).toBe(true);
    expect(isRangeValid("2026-11-20", "2026-11-19")).toBe(false);
  });

  it("Property: any sequence of calendar picks leaves the end empty or not before the start", () => {
    fc.assert(
      fc.property(fc.array(day, { minLength: 1, maxLength: 30 }), (picks) => {
        let r = { start: "", end: "" };
        for (const p of picks) {
          r = normalizeRange(r.start, r.end, p);
          expect(isRangeValid(r.start, r.end)).toBe(true);
        }
      }),
    );
  });

  it("Property: moving the start never produces an inverted range", () => {
    fc.assert(
      fc.property(day, day, day, (s, e, s2) => {
        const base = isRangeValid(s, e) ? { start: s, end: e } : { start: s, end: "" };
        const next = withStart(base, s2);
        expect(isRangeValid(next.start, next.end)).toBe(true);
      }),
    );
  });

  it("clears the end when the start moves past it, and keeps it when it does not", () => {
    expect(withStart({ start: "2026-11-10", end: "2026-11-12" }, "2026-11-15")).toEqual({ start: "2026-11-15", end: "", cleared: true });
    expect(withStart({ start: "2026-11-10", end: "2026-11-12" }, "2026-11-12")).toEqual({ start: "2026-11-12", end: "2026-11-12", cleared: false });
  });

  it("disables days before the start only while the end is being picked", () => {
    expect(minSelectable({ start: "2026-11-10", end: "" })).toBe("2026-11-10");
    expect(minSelectable({ start: "2026-11-10", end: "2026-11-12" })).toBeUndefined();
    expect(minSelectable({ start: "", end: "" })).toBeUndefined();
  });
});
