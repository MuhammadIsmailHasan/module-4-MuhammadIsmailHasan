/** Plain rendering of a card description (no state, no handlers). */
export function CardDescription({ text }: { text: string | null }) {
  if (!text) return <p className="text-ink-muted">No description.</p>;
  return <p className="whitespace-pre-wrap">{text}</p>;
}
