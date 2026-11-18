# Frontend Guidelines

Coding standards for the Next.js app.

---

**Rule:** Build UI only from `components/shared/Base*` (`BaseButton`,
`BaseBadge`, `BaseModal`); never a raw `<button>`, ad-hoc badge `<span>`, or a
one-off modal.

**Rationale:** One place to fix styling, states, and accessibility for every
button/badge/modal in the app, instead of N near-duplicates.

**Example:**
```tsx
// Bad
<button className="bg-red-500 px-3 py-1 rounded" onClick={onDelete}>Delete</button>

// Good
<BaseButton variant="danger" onClick={onDelete}>Delete</BaseButton>
```

---

**Rule:** Default to a Server Component. Add `"use client"` only once a
component actually needs `useState`/`useEffect`, an event handler, or a
browser API.

**Rationale:** Most of the card/board content is read-only on first render —
rendering it server-side means less JS shipped to a phone on a slow
connection, which matters more here than on desktop.

**Example:**
```tsx
// Bad: client component for something that never changes without a refetch
"use client"
export function CardDescription({ text }: { text: string }) {
  return <p>{text}</p>
}

// Good: plain server component
export function CardDescription({ text }: { text: string }) {
  return <p>{text}</p>
}
// "use client" only on CardModal, CommentComposer, the drag-and-drop Board, etc.
```

---

**Rule:** Components never call `fetch`/`axios` inline; all requests go
through a typed API client that unwraps the `{ data }` / `{ error }` envelope
in one place.

**Rationale:** Keeps auth headers, base URL, and error handling consistent,
and means a component never has to know the envelope shape itself.

**Example:**
```tsx
// Bad
useEffect(() => { fetch("/api/cards/" + id).then(r => r.json()).then(setCard) }, [id])

// Good
useEffect(() => { api.cards.get(id).then(setCard) }, [id]) // api.cards.get already unwraps { data }
```

---

**Rule:** Build the layout mobile-first: base styles target a ~360–414px
screen with no media query; `min-width` queries add or change things for
larger screens. Never ship a desktop layout with a `max-width` query that
strips it down for mobile.

**Rationale:** A layout retrofitted from desktop tends to keep desktop-only
assumptions (fixed widths, hover-only menus) that break on a phone; starting
from mobile avoids that by construction.

**Example:**
```css
/* Bad: desktop-first */
.sidebar { width: 264px; }
@media (max-width: 960px) { .sidebar { display: none; } }

/* Good: mobile-first */
.sidebar { transform: translateX(-100%); }
@media (min-width: 960px) { .sidebar { position: static; transform: none; } }
```

---

**Rule:** A drag-and-drop reorder inserts a placeholder element at the drop
target and animates the other cards into place (FLIP) instead of snapping
them; the move is only committed to the backend on `dragend`, once.

**Rationale:** Matches the already-approved interaction feel, and keeps the
backend call to exactly one `PATCH` per completed drag, not one per
`dragover` event.

**Example:**
```tsx
// Bad: call the API on every dragover tick
onDragOver={() => api.cards.move(id, computeOrder())}

// Good: move a placeholder locally, commit once on drop
onDragEnd={() => api.cards.move(id, { columnId, order: computeOrder() })}
```

---

**Rule:** The comment thread component only shows a "Reply" action on a
top-level comment (`parentId === null`); a reply never renders its own
"Reply" button. There is no like button, and the "create new card" action is
keyed off `comment.canCreateCard` (the author being a manager), not
`comment.isPriority`.

**Rationale:** The backend rejects a reply-to-a-reply with `400` and has no
like endpoint — the UI shouldn't offer actions that don't exist or are
guaranteed to fail; keeping priority and create-card as separate booleans
avoids one standing in for the other by accident.

**Example:**
```tsx
{comment.parentId === null && <BaseButton onClick={() => openReplyBox(comment.id)}>Reply</BaseButton>}
{comment.canCreateCard && <BaseButton size="sm">Create card</BaseButton>}
<BaseBadge>{comment.replyCount} replies</BaseBadge>
```

---

**Rule:** The filter row's category chips are rendered from
`api.categories.listForBoard(boardId)`, never a hard-coded array; an
attachment link/button always opens with
`target="_blank" rel="noopener noreferrer"`, never a custom preview modal.

**Rationale:** A board's categories are its own, fetched data — a
hard-coded chip list would show the wrong categories on every other board.
A new tab is the agreed behavior for attachments; building a preview
component for PDF/Word/RAR would be solving a problem nobody asked for.

**Example:**
```tsx
// Bad
const CHIPS = ["Design", "Dev", "Bug", "Research"]

// Good
const { data: categories } = useCategories(boardId)
...
<a href={attachment.url} target="_blank" rel="noopener noreferrer">{attachment.name}</a>
```

---

**Rule:** Colors, spacing, and radii come only from the design-token CSS
variables defined once at the root (`--brand`, `--surface-*`, `--space-*`,
`--radius-*`, the `--label-*` pairs) — never a literal hex code or raw pixel
value inside a component.

**Rationale:** Keeps every `Base*` component visually identical to the
approved prototype, and means a palette tweak is a one-file change.

**Example:**
```tsx
// Bad
<span style={{ background: "#f6dada", color: "#9a2f2f" }}>High</span>

// Good
<BaseBadge style={{ background: "var(--label-red-bg)", color: "var(--label-red-text)" }}>High</BaseBadge>
```

---

**Rule:** Every interactive element is reachable by `Tab` and shows a visible
focus ring; `outline: none` is never applied without a replacement focus
style.

**Rationale:** Baseline keyboard accessibility, cheap to keep if enforced
from the first component.

**Example:**
```css
/* Bad */
button:focus { outline: none; }

/* Good */
button:focus-visible { outline: 2px solid var(--focus-ring); }
```
