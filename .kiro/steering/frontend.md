---
inclusion: always
---

# Frontend Steering — App Shell & Interaction Rules

This reflects the approved HTML prototype (`design/kanban-prototype.html`) — its
layout and interaction patterns are the real source of truth for the frontend,
overriding any looser prose description elsewhere.

- **Rule:** Build mobile-first: write the base (no media query) styles for a
  ~360–414px screen first, then use `min-width` media queries to add or adjust
  for tablet/desktop — never the reverse (a `max-width` query stripping a
  desktop layout down for mobile).
  **Rationale:** The primary device is a phone; a layout that was designed for
  desktop and then "made responsive" tends to leave desktop-only assumptions
  (fixed widths, hover-only affordances) baked in.
  **Example:** the prototype's own sidebar already does this —
  `.sidebar { transform: translateX(-100%); }` is the mobile default, and
  `@media (min-width: 960px) { .sidebar { position: static; transform: none; } }`
  is the desktop enhancement, not the other way around.

- **Rule:** On mobile, every primary action (add a card, open the inbox,
  switch board, open settings) sits within one thumb-reach zone — bottom
  third of the screen or a persistent header — never only at the top of a
  scrolled-away header.
  **Rationale:** A board can be tall; an action that's only reachable by
  scrolling back to the top isn't actually easy to reach on a phone.
  **Example:** the sidebar's off-canvas toggle sits in the mobile header, not
  buried at the bottom of a long scroll; the "+ Add a card" affordance per
  column follows the same rule.

- **Rule:** The app shell has a left `Sidebar` (brand, nav — including
  **Inbox** and **Activity** links — the **Boards** list, which *is* the
  board switcher, team members, profile) and a center `Main` area (board
  header + columns). Inbox and Activity share one **side panel** sliding in
  from the right, opened from the sidebar's own nav items or the header bell
  — there is no separate floating dock; the sidebar already covers that
  entry point. On mobile the sidebar is an off-canvas drawer behind a scrim;
  above 960px it's always visible.
  **Rationale:** A floating dock duplicated what the sidebar nav already
  offers — one entry point per feature is simpler to build and to use.
  **Example:** clicking "Inbox" in the sidebar and clicking the header bell
  both call the same `toggleSidePanel("inbox")`.

- **Rule:** A card drag-and-drop move inserts a placeholder element at the
  drop target, animates siblings into place with a FLIP transform, and on
  `dragend` calls the backend to persist the new column/order — reconciling
  local state with the response.
  **Rationale:** This is the exact pattern already proven in the prototype
  (`makePlaceholder`, `flipBoard`, `syncDataFromDOM`), and it's the only way
  the new position survives a page refresh.
  **Example:** on `dragend`, `PATCH /api/cards/{id}/move` with the computed
  `Float` order, then re-render from the server response.

- **Rule:** All colors, spacing, and radii are the CSS custom properties
  already defined in the prototype's `:root` (`--brand`, `--surface-*`,
  `--ink*`, `--space-*`, `--radius-*`, the `--label-*` pairs) — components
  consume these variables, never a hard-coded hex or pixel value.
  **Rationale:** One token set behind `BaseButton`/`BaseBadge`/`BaseModal`
  keeps the real app visually identical to the approved prototype as it's
  rebuilt in Next.js.
  **Example:** `background: var(--label-red-bg); color: var(--label-red-text);`
  for a high-priority badge.

- **Rule:** The card detail view is one two-pane modal used for **both**
  viewing and editing: the left pane holds title, description, priority,
  dates, attachments, the subtask checklist, and the card's own activity log;
  the right pane holds the comment thread and composer, in the same modal —
  never a separate screen or a second modal for comments.
  **Rationale:** Editing a card and discussing it are the same moment for the
  person doing it; splitting them across screens would just add navigation for
  no benefit.
  **Example:** the modal's `Save changes` button commits the left pane; the
  comment composer on the right posts independently, without closing the modal.

- **Rule:** The comment thread renders priority comments first (with a
  priority indicator), then the remaining top-level comments under a
  visible **Latest / Popular** toggle — "Popular" shown as a reply-count
  badge, not a like count — each with its (max one level of) replies nested
  underneath. A "Reply" action appears only on top-level comments, never on
  a reply. There is no like button anywhere in the thread.
  **Rationale:** Matches the agreed comment model exactly — the UI shouldn't
  offer an action (liking, or replying to a reply) that the backend doesn't
  support or will reject.
  **Example:** `<CommentThread sort={sort} onSortChange={setSort}/>` renders
  the toggle; clicking "Reply" only shows on `comment.parentId === null`.

- **Rule:** The **"create new card"** action renders only on comments whose
  `author.role === "manager"` — it does not depend on `is_priority`.
  **Rationale:** Keeps the two signals visually and logically separate: a
  priority badge can appear on anyone's comment, the create-card button only
  on a manager's.
  **Example:** `{comment.canCreateCard && <BaseButton size="sm">Create card</BaseButton>}`.

- **Rule:** The board's filter row renders category chips fetched from
  `GET /api/boards/{id}/categories` — never a hard-coded chip list. For
  supervisor/manager/admin, the sidebar has a **Categories** entry that opens
  a small CRUD screen (add/rename/recolor/delete) scoped to the current board.
  **Rationale:** Categories are now a real per-board feature, not the
  prototype's fixed Design/Dev/Bug/Research chips — the UI has to reflect
  whatever categories that specific board actually has.
  **Example:** switching boards re-fetches and re-renders a different chip
  set in the filter row.

- **Rule:** Clicking an attachment (link or file) opens it with
  `target="_blank" rel="noopener noreferrer"` — there is no in-app preview
  or viewer modal.
  **Rationale:** Matches the agreed behavior exactly, and avoids building a
  file-preview component for PDF/Word/RAR that isn't needed.
  **Example:** `<a href={attachment.url} target="_blank" rel="noopener noreferrer">{attachment.name}</a>`.

- **Rule:** The subtask checklist renders as a flat list of checkboxes with
  inline-editable titles and a drag handle for reordering — no nested modal,
  no per-subtask detail screen.
  **Rationale:** A subtask is meant to be checked off in passing, not opened.
  **Example:** clicking a subtask's checkbox calls
  `api.subtasks.update(id, { isDone: true })` directly from the list row.

- **Rule:** Default every component to a Server Component; make it a Client
  Component (`"use client"`) only when it needs state, an event handler, or a
  browser API (drag-and-drop, the modal, the comment composer, the sort
  toggle, the search input).
  **Rationale:** Most of a card's content (description, dates, activity text)
  never changes without a page re-fetch — shipping it as a Server Component
  means less JavaScript sent to a phone on a slow connection.
  **Example:** `CardDescription` and `ActivityList` are Server Components;
  `CardModal`, `CommentComposer`, and the drag-and-drop `Board` are Client
  Components.

- **Rule:** The login and register pages follow a modern split-panel SaaS
  auth layout — a brand/illustration panel alongside a form panel, an
  elevated rounded form card, generous whitespace — in the direction of the
  referenced design (a Dribbble HRIS dashboard login shot). I couldn't load
  that page's actual visuals here, so this is the general pattern to build
  toward, not a pixel-exact spec; send a screenshot if closer fidelity matters.
  **Rationale:** Names a concrete visual direction for the two pages that
  otherwise have no design reference at all, without inventing detail that
  wasn't actually seen.
  **Example:** desktop: two columns, illustration/brand side + form side;
  mobile: the illustration panel collapses away and only the form remains.

- **Rule:** The prototype's per-card 0–10 `progress` meter, `views` counter,
  and decorative Overview/Notes/Questions tabs are **stretch** features —
  build the required fields (priority, dates, attachments, subtasks,
  categories, assignment, comments, activity, notifications) first; only
  then layer these in, kept visually as-is. (Category chips are a required
  feature now, not stretch — see the category filter-row rule above.)
  **Rationale:** `progress`/`views`/the extra tabs weren't in the original
  feature list; they stay in scope by request, but shouldn't delay or crowd
  out the core paths.
  **Example:** ship `Card.priority`/`start_date`/`end_date`/subtasks/category
  end-to-end before adding `Card.progress`/`Card.views_count`.

- **Rule:** Comments/activity-log sections and the Inbox panel render only
  when the API response includes that data — the UI never decides on its own
  to hide them for a role; absence of the field *is* the access control.
  **Rationale:** Keeps "guests never see comments/activity" enforced in one
  place (the backend), so the frontend can't drift out of sync with it.
  **Example:** `{card.comments && <CommentThread items={card.comments}/>}` —
  a guest's API response simply omits `comments`/`activity`.
