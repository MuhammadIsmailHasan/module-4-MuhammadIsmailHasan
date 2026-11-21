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

- **Rule:** There are no public boards (V12, Decision Y): every board is private.
  A guest (no account, no token) cannot list or browse boards. Anyone, signed in
  or not, opens a board read-only through the **public link** `/shared/{token}`
  (the V10 share link, renamed in V12) that only a **Manager or an Admin**
  creates, regenerates, or disables (the board owner cannot), and sees its
  columns, cards, card details, categories, and attachment links — never its
  comments or activity log, under any circumstance, and no write control. A
  signed-in user who already has access to the board gets the normal view
  instead. Disabling or regenerating the link invalidates the old one at once;
  there is no expiry date.
  **Rationale:** A link a Manager or Admin publishes is an explicit, revocable
  act; shared status is for status only, not internal discussion.
  **Example:** `GET /api/shared/{token}` omits `comments` and `activity_log`;
  `GET /api/boards` with no token returns `401`; the owner calling
  `POST /api/boards/{id}/share` gets `403`.

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
  one "username or email" value. Every account has both fields (the local
  database is reset on migration and re-seeded; there is no legacy-account
  path and no first-login email prompt). Failed logins are rate limited (5 per
  identifier and address, 20 per address, in 15 minutes) and a blocked request
  is `429`. Registration is not rate limited yet (deferred); the availability
  check is. Sign-out and the profile live in a user menu in the app header, not
  in the sidebar.
  **Rationale:** Two real fields allow field-level errors; limiting guesses
  protects passwords; one entry point per feature.
  **Example:** `POST /api/auth/login { "identifier": "ada", "password": "..." }`.
- **Rule:** A user uploads a profile picture on the Profile page: PNG, JPEG, or
  WebP, at most 2 MB, checked by the file's real content on the server. A user
  without a picture, or whose picture fails to load, shows initials from the full
  name. The picture shows in comments and replies, the board member lists
  (sidebar Team members, member search, assignee popover), and on cards (board
  card assignee, card modal chip). A guest on a share link sees initials only.
  **Rationale:** A picture the user owns replaces a URL that can break or
  track; the share view stays status-only.
  **Example:** `POST /api/users/me/avatar` with a 3 MB PNG returns `400`.
- **Rule:** A user's email is shown only to staff, in three places: the board
  member search (manager, admin), the assignee popover (a supervisor,
  manager, or admin with write access to the board), and (V12 round 2, Decisions
  M and S) the pending join-request list of the Invite modal, for the owner,
  manager, and admin, together with the requester's full name and avatar or
  initials. It never appears in comments, activity rows, notifications (rows or
  text), the public link and share view, the sidebar, or any list a member can read.
  **Rationale:** Staff need the email to tell two people with one name apart,
  and an approver needs it to recognise a requester; nobody else needs another
  person's address.
  **Example:** the member search row shows "Ada Lovelace", then "ada" and
  "ada@x.io"; a pending request row shows the same three values; the sidebar
  row shows "Ada Lovelace" and "ada" only.
- **Rule:** Google OAuth login is out of scope until the username/email + password MVP
  is complete and verified working end-to-end.
  **Rationale:** Avoids scope creep delaying the gradable MVP; OAuth is additive, not
  a blocker.
  **Example:** Ship and test `POST /api/auth/register` and `POST /api/auth/login`
  first; add the OAuth callback route only after MVP sign-off.

- **Rule:** A board is visible only to its owner (a Supervisor), its
  `BoardMember`s (role Member or Supervisor), Managers, and Admins; everyone
  else gets `403` (`401` without a token). Home lists the boards the viewer owns
  or belongs to; a Manager and an Admin see all. A Manager or an Admin is never
  a `BoardMember`. Only a Manager or an Admin adds a member directly (Member and
  Supervisor accounts only); the board owner adds people only through the
  **invite link**: the owner, a Manager, or an Admin generates it from the
  board's Invite button, a signed-in Member or Supervisor opens `/invite/{token}`
  and sends a join request, the owner sees the pending list (with each
  requester's email), and **only a Manager or an Admin approves or rejects**. A
  rejected user may ask again with no cooldown. A card's assignee must be the
  owner or a board member. The Sidebar Team members list shows the owner first,
  tagged "Owner", with no remove action on that row; the owner can still remove
  other members.
  **Rationale:** "Private" has to mean private from unrelated signed-in users;
  the owner can invite but cannot grant access alone.
  **Example:** a Member who is not on a board gets `403` opening it; the owner's
  `PATCH /api/join-requests/{id}` gets `403`.
- **Rule:** An author can delete their own comment or reply after a confirmation
  (a reply decrements the parent's `reply_count`; a top-level comment takes its
  replies with it). A Manager or an Admin cannot delete other people's comments.
  **Rationale:** An author may retract their own words; moderation is not part
  of this version.
  **Example:** `DELETE /api/comments/{id}` by a non-author, Manager included, is `403`.
- **Rule:** A Member may check and uncheck the subtasks of a card assigned to
  them, and the card's progress is derived from its subtasks (done of total,
  mapped to 0 to 10); progress is never typed by hand.
  **Rationale:** The checklist is the one source of how far a card is.
  **Example:** 2 of 4 subtasks done gives progress 5; a card with none shows no meter.

- **Rule:** Admin is deliberately not a superset of Manager: Admin cannot post
  or flag comments and gets `403` on analytics. This is a recorded decision,
  not an oversight.
  **Rationale:** Admin is a separate operations track; "fixing" the gap would
  quietly change the permission model.
  **Example:** `PATCH /api/comments/{id}/priority` as Admin → `403`.
