/** Pure drop-order computation mirroring backend app/common/ordering.py. */

export const GAP = 1e-6;

/**
 * Order for a card dropped at `index` among `siblings` (the orders of the target column, WITHOUT the
 * dragged card, ascending). Empty list 1.0; first min - 1; last max + 1; otherwise the average.
 */
export function computeDropOrder(siblings: number[], index: number): number {
  if (siblings.length === 0) return 1.0;
  const i = Math.max(0, Math.min(index, siblings.length));
  if (i === 0) return siblings[0] - 1;
  if (i === siblings.length) return siblings[siblings.length - 1] + 1;
  return (siblings[i - 1] + siblings[i]) / 2;
}

export function needsRebalance(prev: number | null, next: number | null): boolean {
  return prev !== null && next !== null && Math.abs(next - prev) < GAP;
}

/** Renumber 1.0, 2.0, ... keeping the existing order. */
export function rebalance(orders: number[]): number[] {
  return orders.map((_, i) => i + 1);
}

/** Index in `centers` (vertical midpoints of the cards, top to bottom) where a pointer at `y` would drop. */
export function dropIndex(centers: number[], y: number): number {
  let i = 0;
  while (i < centers.length && y > centers[i]) i++;
  return i;
}
