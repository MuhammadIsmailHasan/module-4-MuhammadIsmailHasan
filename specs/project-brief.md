# Project Brief — Kanban Task Management App

## 1. Project Context & Purpose

A role-based Kanban task management web app for a team that needs both
day-to-day execution (boards, columns, cards, drag-and-drop) and
management-level oversight (analytics, cross-board visibility, user/board
administration) without the overseers having to open every board themselves.

Built spec-driven with Kiro: requirements → design → tasks → implementation,
with every change to the spec tracked through versioning and a changelog (see
`change-management.md` and `development-workflow.md`). The backend is a Flask
REST API; the frontend is a mobile-first Next.js app. Both deploy to public
URLs and are covered by automated tests (pytest for the API, Playwright for
the end-to-end Kanban journey).

## 2. Target Users & Goals

Five roles, strictly layered (each higher role includes everything the one
below it can do, except Admin which is a separate administrative track):

| Role | Can do | Goal |
|---|---|---|
| **Guest** | View public boards (columns + cards only) | See project status without an account, with no access to internal discussion |
| **Member** | Everything a guest sees, plus: move cards, edit cards, comment | Execute and update their own assigned work |
| **Supervisor** | Everything a member does, plus: create columns/cards, delete cards, archive cards, comment on cards, view analytics for *their* board, assign cards to members, set board public/private | Run one board end-to-end as its owner |
| **Manager** | Everything a supervisor does, plus: view detailed analytics across *all* boards, create boards and assign them to users, flag any comment as priority | Oversee multiple boards/teams without opening each one |
| **Admin** | Manage user accounts, create/assign boards | Keep the system and its users in order |

## 3. Core Features (with scope boundaries)

### Boards, columns & cards
- A **board** (project) contains **columns** (lists), which contain **cards**.
- New boards are seeded with five default columns: `Todo`, `In Progress`, `Review`,
  `Revision`, `Done`. Supervisors/managers may add more columns.
- Cards can be moved between columns via **drag and drop**; the new position must
  persist and survive a page refresh.
- Every card has a `title`, a free-text `description`, and a simple **subtask
  checklist** (title + done/not-done + order; no assignee or date of its own).
- Supervisors can delete and archive cards; managers/admins can archive boards.
- *Out of scope for now*: custom per-board workflow templates beyond the five
  default columns; subtasks with their own assignee/date.

### Card detail — one modal for viewing and editing
- Opening a card opens a single two-pane modal, used for both viewing and
  editing — never a separate screen.
  - **Left pane**: title, description, priority, dates, attachments, the
    subtask checklist, and the card's own activity log.
  - **Right pane**, same modal: the comment thread and composer.

### Priority & dates
- Every card has a priority: `high`, `medium`, or `low` (no custom labels for now).
- A card has an optional start date and end date (deadline) — two real date
  fields, not one free-text "due" string.
- Notifications fire to the assigned member: (a) when a card is assigned to
  them, and (b) when an assigned card reaches its end-date deadline.

### Attachments
- A card can have attachments: either a **link** or an uploaded **file** (PDF,
  Word, RAR).
- Clicking an attachment opens it in a **new browser tab** — no in-app
  preview/viewer.

### Comments & activity log
- Every member with access to a card can view its comments and activity log;
  guests never see either, even via a direct API call.
- Comments form a **2-level tree**: a top-level comment can have replies, but
  a reply can't itself be replied to.
- There's no like button. Below the priority comments, the viewer can toggle
  the remaining top-level comments between **Latest** (newest first) and
  **Popular** — popular meaning **most replies**, ties broken by newest first.
- A **manager** can flag any comment — their own or someone else's — as
  priority; priority comments always sort to the top of the thread.
- The **"create new card"** quick action appears only on comments authored by
  a manager — it's not tied to the priority flag.
- The activity log is append-only (card moved, edited, assigned, commented,
  archived, etc.): a per-card log inside the card modal, plus a board-wide
  feed reachable from the sidebar.

### Categories
- Supervisors, managers, and admins can create, edit, and delete **categories**
  — each board has its own set (categories aren't shared across boards).
- Categories appear as chips in the board's filter row, so anyone viewing the
  board can filter cards by category.
- Managing a board's categories is its own screen, reachable from the
  **sidebar** for the roles above.

### Notifications & inbox
- Notifications land in an in-app **Inbox** for the member they target
  (assignment, deadline reached).
- App shell: a left **sidebar** holds navigation (including **Inbox** and
  **Activity** links) plus the **Boards** list (this is the board switcher)
  and team/profile info; the **board** itself is the large central area.
  Inbox and Activity share one panel that slides in from the right, opened
  from the sidebar nav or the header bell — there's no separate floating
  dock; the sidebar already covers that. On mobile the sidebar becomes an
  off-canvas drawer.

### Analytics
- Supervisors see analytics for *their own* board; managers see detailed
  analytics across *all* boards.
- Analytics are **pre-aggregated** summaries (counts/trends, not raw card
  dumps) so a supervisor/manager can judge a board's progress without
  opening it.

### Auth & accounts
- Login/register with email or username + password; registration also
  collects full name.
- Users have an optional (`nullable`) avatar.
- Login and register pages follow a modern split-panel SaaS layout —
  brand/illustration panel alongside the form, elevated rounded form card —
  in the direction of a referenced Dribbble HRIS dashboard login design;
  exact pixel fidelity is still open (the page's visuals couldn't be fetched
  directly — a screenshot would let this get tightened up).
- Google OAuth login is **optional, post-MVP** — added only once the core
  auth and the rest of the required features are complete and working.
- Admins manage user accounts (create/edit/assign roles).

### Board visibility & archiving
- Supervisors can set a board's visibility to **public** or **private** from
  board settings.
- Boards and cards can be **archived** (reversible) in addition to deletion.

### Search & filter
- Users can search and filter cards within the **active** board (e.g. by
  priority, assignee, text).

### Stretch (not in the original scope, kept by request)
- A 0–10 per-card `progress` meter, a `views` counter, and the prototype's
  decorative Overview/Notes/Questions tabs. (Category, originally a
  prototype-only tag, is now a real feature — see **Categories** above, not
  stretch.) Build these only after every feature above is working end-to-end.

## 4. Technical Constraints & Stack

- **Backend**: Flask, one blueprint per domain —
  `auth, boards, columns, cards, categories, comments, notifications,
  analytics, users` — each layered `routes.py → service.py → repository.py
  → schema.py` (routes
  thin, service holds business logic, repository is the only place that
  touches the database, schema (de)serializes/validates). SQLAlchemy models
  with UUID primary keys, `created_at`/`updated_at`/`deleted_at`, and a
  `db.Column(db.Float)` `order` column on `Card`/`Subtask` for drag-and-drop
  reordering. CORS restricted to an explicit origin allow-list from an env
  var — never a wildcard.
- **Frontend**: Next.js (App Router, TypeScript), **mobile-first** —
  base styles target a phone screen, `min-width` queries add for larger
  screens. Server Components by default; a component becomes a Client
  Component only when it needs real interactivity (drag-and-drop, the card
  modal, the comment composer, the sort toggle). Shared base components
  (`BaseButton`, `BaseBadge`, `BaseModal`) styled from the prototype's CSS
  custom-property design tokens.
- **API shape**: every success response is `{ "data": ... }`, every error is
  `{ "error": { "code", "message" } }`, with the matching HTTP status.
- **Auth**: email/username + password (hashed), session or JWT; Google OAuth
  is additive and optional, wired in only after everything else is stable.
- **Testing**: `pytest` for the API (covering at minimum comment creation
  success/validation/auth/authorization cases); Playwright for the
  end-to-end Kanban journey against the live deployed URL, with no
  `waitForTimeout`.
- **Deployment**: Flask API and Next.js app each live on their own public URL
  (e.g. Render/Railway for the API, Vercel for the frontend); `.env.example`
  committed for both, no real `.env` files committed.

## 5. Non-Functional Requirements (Measurable)

1. **Performance** — API responses stay under 300ms at the 95th percentile
   under normal load; a board with 200 cards shows its first meaningful paint
   in under 2 seconds on a throttled mobile connection (Fast 3G).
2. **Security** — 100% of mutating endpoints re-validate the caller's role
   server-side; unauthorized calls return `403`, unauthenticated calls return
   `401`; 0 guest-facing responses ever include a `comments` or `activity`
   field, even on direct API calls to the comment/activity endpoints.
3. **Mobile usability** — every page is fully usable (no horizontal scroll,
   no cut-off or overlapping content) at 360–414px viewport widths; every
   primary action (add card, open inbox, switch board) sits within one
   thumb-reach zone on mobile.
4. **Auditability** — 100% of state-changing actions produce exactly one
   `ActivityLog` row in the same transaction as the change; `Board`/`Card`
   deletion is always soft (`deleted_at`), never a hard delete.
5. **Consistency** — 100% of API endpoints return the same success/error
   envelope shape, so the frontend's API client needs exactly one
   unwrap/throw path, never per-endpoint branching.
6. **Maintainability** — every backend domain stays inside its own blueprint
   (`routes → service → repository → schema`); no cross-domain code calls a
   model's `.query` directly outside that domain's own repository.

## Decisions Log

Resolved while reconciling the written requirements against an approved HTML
prototype, and through two later revision passes:

- **Inbox/Activity access**: no separate floating dock — the sidebar's own
  nav (Inbox, Activity) and the header bell open the shared right-side panel.
  (Supersedes an earlier "bottom dock" decision.)
- **Comment tree depth**: max depth 2 — a top-level comment plus one level
  of replies; replying to a reply is rejected, server-side included.
- **Comment popularity**: no like button — "Popular" is ranked by **reply
  count**, ties broken by newest first.
- **Comment priority mechanism**: a manager can flag *any* comment as
  priority (not only comments a manager authored); priority only affects
  sort order.
- **"Create new card" quick action**: tied to the comment's **author being a
  manager**, independent of the priority flag.
- **Categories**: promoted from a stretch, prototype-only tag to a real
  per-board CRUD feature — supervisor/manager/admin manage them from a
  sidebar screen; they populate the filter row for everyone viewing the board.
- **Attachments**: open in a new browser tab, no in-app preview.
- **Subtask scope**: a simple checklist (title + done + order), no
  assignee/date of its own.

Gaps the prototype itself still needs closing during implementation (not a
design choice — just missing from the mock-up): splitting its single `due`
text field into real `start_date`/`end_date`; an attachments section, a
subtask checklist, a category-managed filter row, and the priority/reply
comment UI in the card modal; a per-card activity log (the prototype's is
board-wide only); a sidebar nav for Inbox/Activity/Categories in place of the
floating dock; and role-based rendering (guest never receives
`comments`/`activity` from the API — the prototype has no role concept at all).
