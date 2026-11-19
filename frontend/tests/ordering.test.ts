import fc from "fast-check";
import { describe, expect, it } from "vitest";
import { computeDropOrder, dropIndex, needsRebalance, rebalance } from "@/lib/ordering";

describe("computeDropOrder", () => {
  it("handles empty, first, last and middle", () => {
    expect(computeDropOrder([], 0)).toBe(1.0);
    expect(computeDropOrder([3, 5], 0)).toBe(2);
    expect(computeDropOrder([3, 5], 2)).toBe(6);
    expect(computeDropOrder([3, 5], 1)).toBe(4);
  });
});

describe("Property 15: drop order and rebalance", () => {
  it("every insertion keeps the list strictly ascending, with rebalance on a tiny gap", () => {
    fc.assert(
      fc.property(fc.array(fc.nat(60), { minLength: 1, maxLength: 80 }), (positions) => {
        let orders: number[] = [];
        for (const raw of positions) {
          const index = raw % (orders.length + 1);
          const prev = index > 0 ? orders[index - 1] : null;
          const next = index < orders.length ? orders[index] : null;
          if (needsRebalance(prev, next)) orders = rebalance(orders);
          const value = computeDropOrder(orders, index);
          orders = [...orders.slice(0, index), value, ...orders.slice(index)];
          for (let i = 1; i < orders.length; i++) expect(orders[i]).toBeGreaterThan(orders[i - 1]);
        }
      }),
      { numRuns: 100 },
    );
  });

  it("rebalance renumbers 1..n", () => {
    fc.assert(
      fc.property(fc.array(fc.double({ noNaN: true, min: -1e6, max: 1e6 }), { maxLength: 30 }), (xs) => {
        expect(rebalance(xs)).toEqual(xs.map((_, i) => i + 1));
      }),
    );
  });

  it("needsRebalance only for two neighbours closer than 1e-6", () => {
    expect(needsRebalance(1, 1 + 1e-7)).toBe(true);
    expect(needsRebalance(1, 2)).toBe(false);
    expect(needsRebalance(null, 2)).toBe(false);
  });
});

describe("dropIndex", () => {
  it("returns how many card centres are above the pointer", () => {
    expect(dropIndex([10, 30, 50], 5)).toBe(0);
    expect(dropIndex([10, 30, 50], 35)).toBe(2);
    expect(dropIndex([10, 30, 50], 99)).toBe(3);
    expect(dropIndex([], 10)).toBe(0);
  });
});
