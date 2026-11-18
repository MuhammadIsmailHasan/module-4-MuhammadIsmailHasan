---
inclusion: always
---

# Product Steering — Kanban Task Management

Business rules Kiro must respect when generating requirements, design, or code.

- **Rule:** Five roles exist — guest, member, supervisor, manager, admin — and are
  strictly additive: manager ⊇ supervisor ⊇ member ⊇ guest's view, with admin as a
  separate user/board-administration track.
  **Rationale:** Prevents permission logic from being duplicated or drifting per
  endpoint; a hierarchy is simpler to implement and to test than five independent rule sets.
  **Example:** `if role in ("member", "supervisor", "manager"): allow_move_card()`.

- **Rule:** Guests may view a **public** board's columns and cards, but never its
  comments or activity log, under any circumstance.
  **Rationale:** Matches the stated privacy requirement — public visibility is for
  status only, not internal discussion.
  **Example:** `GET /api/boards/{id}` for a guest omits `comments` and `activity_log`
  even if requested explicitly.

- **Rule:** Every new board is seeded with five default columns, in this order:
  `Todo, In Progress, Review, Revision, Done`.
  **Rationale:** Gives every generated board a consistent starting workflow and a fixed
  seed state for Kiro to build against.
  **Example:** On board creation, insert five `Column` rows with `order = 0..4` and
  those names.

- **Rule:** Card priority is restricted to exactly `high | medium | low`.
  **Rationale:** Keeps filtering and analytics simple and consistent; no free-text
  priority labels.
  **Example:** `priority = db.Column(db.Enum("high", "medium", "low"))`.

- **Rule:** A manager can flag any comment — their own or someone else's — as
  priority. Priority comments always sort above everything else on a card.
  This is purely a sort signal — it does not by itself grant the "create new
  card" action (see the next rule).
  **Rationale:** A manager's judgment about which comment matters right now is
  more useful than automatically pinning everything a manager happens to type.
  **Example:** manager clicks "Mark as priority" on a member's comment; it jumps
  to the top of the thread for everyone, with no card-creation action attached.

- **Rule:** The "create new card" quick action appears only on comments whose
  **author** is a manager — regardless of whether that comment is flagged
  priority.
  **Rationale:** Keeps the two mechanisms independent: priority controls sort
  order for anyone's comment; "create a card from this" stays a manager's own
  authorial action.
  **Example:** a member's comment, even if marked priority by a manager, never
  shows "create new card"; a manager's own comment always does.

- **Rule:** Comments are a 2-level tree: a top-level comment can have replies,
  but a reply cannot itself be replied to.
  **Rationale:** Keeps a card's discussion scannable instead of letting threads
  nest indefinitely.
  **Example:** the UI shows a "Reply" action on top-level comments only.

- **Rule:** There is no like button. Below the priority comments, the viewer
  can toggle the remaining top-level comments between **Latest** (newest
  first) and **Popular** (most replies first, ties broken by newest).
  **Rationale:** Reply count is a free, already-tracked signal of which
  comment generated discussion — no separate like/vote feature needed.
  **Example:** a comment with 5 replies outranks one with 2, regardless of
  which was posted first.

- **Rule:** A card's subtasks are a simple checklist — title + done/not-done +
  order — with no assignee or date of their own in the MVP.
  **Rationale:** A subtask is for breaking a card's work into visible steps, not
  for becoming a second card to manage.
  **Example:** checking a subtask's box is a one-click toggle, no modal needed.

- **Rule:** Categories are owned by a board (not global) and only
  supervisors, managers, and admins can create, edit, or delete them; any
  role that can view the board can use them as filter chips.
  **Rationale:** Boards run different kinds of work, so letting each board
  define its own categories beats forcing one shared taxonomy on all of them.
  **Example:** Board A's categories are `Design, Dev, Bug`; Board B's are
  `Legal, Finance` — neither list leaks into the other board's filter row.

- **Rule:** Google OAuth login is out of scope until the email/username + password MVP
  is complete and verified working end-to-end.
  **Rationale:** Avoids scope creep delaying the gradable MVP; OAuth is additive, not
  a blocker.
  **Example:** Ship and test `POST /api/auth/register` and `POST /api/auth/login`
  first; add the OAuth callback route only after MVP sign-off.
