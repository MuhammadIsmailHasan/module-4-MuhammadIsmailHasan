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

- **Rule:** A guest (no account, no token) cannot list or browse boards, public or
  private. A guest opens a board only through a **share link** `/shared/{token}`
  that the board's owner, a manager, or an admin enabled, and sees its columns,
  cards, card details, categories, and attachment links read-only — never its
  comments or activity log, under any circumstance. Disabling or regenerating
  the link invalidates the old one at once; there is no expiry date. A private
  board may have a share link (an explicit owner action). Every signed-in user
  can still read public boards.
  **Rationale:** A link the owner creates is an explicit, revocable act; public
  browsing exposed every public board to anyone. Shared status is for status
  only, not internal discussion.
  **Example:** `GET /api/shared/{token}` omits `comments` and `activity_log`;
  `GET /api/boards` with no token returns `401`.

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
  **author** is a manager, and only to a viewer who is a supervisor, manager,
  or admin (a plain member or guest never sees it) — regardless of whether
  that comment is flagged priority.
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

- **Rule:** Accounts have a unique `username` and a unique `email`; login takes
  one "username or email" value. Failed logins are rate limited (5 per
  identifier and address, 20 per address, in 15 minutes) and a blocked request
  is `429`. Registration is not rate limited yet (deferred); the availability
  check is. Sign-out and the profile live in a user menu in the app header, not
  in the sidebar.
  **Rationale:** Two real fields allow field-level errors; limiting guesses
  protects passwords; one entry point per feature.
  **Example:** `POST /api/auth/login { "identifier": "ada", "password": "..." }`.
- **Rule:** A user uploads a profile picture on the Profile page: PNG, JPEG, or
  WebP, at most 2 MB, checked by the file's real content on the server. A user
  without a picture, or whose picture fails to load, shows initials. A guest on
  a share link sees initials only.
  **Rationale:** A picture the user owns replaces a URL that can break or
  track; the share view stays status-only.
  **Example:** `POST /api/auth/me/avatar` with a 3 MB PNG returns `400`.
- **Rule:** A user's email is shown only to staff, in two places: the board
  member search (owner, manager, admin) and the assignee popover (a supervisor,
  manager, or admin with write access to the board). It never appears in
  comments, activity rows, notifications, the share view, the sidebar, or any
  list a member can read.
  **Rationale:** Staff need the email to tell two people with one name apart;
  nobody else needs another person's address.
  **Example:** the member search row shows "Ada Lovelace", then "ada" and
  "ada@x.io"; the sidebar row shows "Ada Lovelace" and "ada" only.
- **Rule:** Google OAuth login is out of scope until the username/email + password MVP
  is complete and verified working end-to-end.
  **Rationale:** Avoids scope creep delaying the gradable MVP; OAuth is additive, not
  a blocker.
  **Example:** Ship and test `POST /api/auth/register` and `POST /api/auth/login`
  first; add the OAuth callback route only after MVP sign-off.

- **Rule:** A private board is visible only to its owner, its `BoardMember`s,
  Managers, and Admins; a public board is visible to every signed-in user.
  Owner, Manager, and Admin can add or remove board members and manage the
  board's share link.
  **Rationale:** "Private" has to mean private from unrelated signed-in
  users too; a share link is the only way past it for someone without access.
  **Example:** a Member who is not on a private board gets `403` when opening it.

- **Rule:** Admin is deliberately not a superset of Manager: Admin cannot post
  or flag comments and gets `403` on analytics. This is a recorded decision,
  not an oversight.
  **Rationale:** Admin is a separate operations track; "fixing" the gap would
  quietly change the permission model.
  **Example:** `PATCH /api/comments/{id}/priority` as Admin → `403`.
