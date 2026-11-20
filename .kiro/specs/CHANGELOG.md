# Changelog

## V1 - Initial Release
- Initial requirements generated from `specs/project-brief.md` and `.kiro/steering/*.md`.
- Initial implementation scope established: auth, roles, boards and columns, cards, drag-and-drop, categories, comments, activity log, notifications and inbox, analytics, board visibility and archiving, search and filter. Google OAuth is out of scope. Progress, views, and decorative tabs are stretch.
- Incorporates five user decisions: `Board.owner_id` (supervisor ownership, guest-only privacy, supervisor analytics scope); members move and edit only assigned cards; create-card action shown to supervisor, manager, and admin on manager-authored comments; board soft delete and archive limited to manager and admin; admin permissions (no commenting or priority flagging).

### Impact
- Requirements: 1 to 16 (new).
- Design: created in `.kiro/specs/design.md` (V1). Adds `Board.owner_id` to the data model, omits `updated_at` on the append-only `ActivityLog`, and adds a `(user_id, card_id, type, notify_date)` unique constraint on `Notification`. `data-model.md` steering needs a sync for these.
- Tasks: not yet created.

## V2 - 2026-11-18
### Changes
- **Decision A (specification):** private boards are gated for unrelated signed-in users. New `BoardMember` entity and `Board_Access` concept; Req 3 gains member add/remove and owner reassign/clear; Req 11.6 replaced; Board_Access wording applied to Req 4, 5, 6, 7, 8, 9, 12.
- **Decision B (specification, no behavior change):** Admin's exclusion from commenting, priority flagging, and analytics (2.5, 10.4) recorded as intentional in a new Decisions Log.
- **Decision C (specification, breaking):** `email_or_username` replaced by one case-insensitive `login_identifier` in the API, the data model, and the glossary.
- **Decision D (specification, breaking):** 4.18 replaced. Attachment files are served through signed, time-limited URLs (15 minutes) that enforce Board_Access; a permanently public URL is no longer allowed.
- **Secondary defaults (specification):** 24h JWT and logout; password minimum and hashing; notification mark-as-read endpoints; order boundary and rebalance rules (5.1 exception); Subtask reorder formula; cross-board move guard; 6.8 cascade dropped; 401 vs 403 standardized (11.5 for a tokenless Guest changes 403 to 401); card unassign; search fields; overdue definition; child-row soft-delete rule; wider pytest coverage (15.5 to 15.7); APP_TIMEZONE for the deadline job.
- **Clarifications after consistency check (specification):** added `Board_Staff_Access` (owner/BoardMember Supervisor, Manager, Admin) for all write actions so an unrelated Supervisor cannot write on a public board; Req 7.14 kept and steering aligned; Req 7.16 Guest status (403 public, 401 private); Req 4.25 signature failures always 403.
- **Other findings (specification):** Decisions 1-5 and A-D labeled in the document; board ownership reassign/clear; case-insensitive unique Category names per board (409).
- **Design:** revised to V2 (BoardMember, `can_access`, signed URLs, new endpoints, properties 1 to 36). **Steering:** `data-model.md`, `backend.md`, `frontend.md`, `api-conventions.md`, `product.md` updated to match.

### Reason
- Resolve the product owner's decisions A to D and the gaps found in review of V1.

### Impact
- Requirements: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15 (all but 14 and 16).
- Design: data model, access control, attachments, ordering, auth, endpoints, correctness properties.
- Tasks: `tasks.md` created from V2 (22 task groups).
- Open: login_identifier format, public-board interpretation of Decision A, and attachment delivery cost (see Open Questions in requirements). Root `specs/v2` created.

## V3 - 2026-11-18
### Changes
- **API documentation (specification):** new Requirement 17. A hand-written `backend/openapi.yaml` and `backend/API.md` document every endpoint. Swagger UI at `/api/docs` is registered only when the new optional `APP_ENV` is `development` or `testing`; it defaults to `production` and is hidden there.
- **Design:** new `APP_ENV` variable, `app/docs.py`, an "API Documentation" section, Properties 37 and 38.
- **Tasks:** new task group 23 (23.1 to 23.4).

### Reason
- The backend has no written API reference; the product owner asked for API.md and a Swagger page that production must not expose.

### Impact
- Requirements: 17 (new). Design: environment variables, backend layout, new section. Tasks: 23 (new). Code: not changed yet.


## V4 - 2026-11-18
### Changes
- **Specification (breaking):** every API response carries top-level `status` (HTTP status code) and `message`. Success is `{ status, message, data }`; error is `{ status, message, error: { code, message } }`. Req 13.2 to 13.4 revised, 13.11 added; examples in 1.1, 1.15, 7.2, 10.5 updated. The Swagger UI HTML, raw OpenAPI document, and successful file bytes are exempt.
- **Specification:** the backend uses flask-smorest with marshmallow schemas (Req 13.12 to 13.15); validation failures return 400 `VALIDATION_ERROR`, never 422. Requirement 17 revised: the OpenAPI document is generated (no hand-written `openapi.yaml`, `flask-swagger-ui`, or `pyyaml`), exported by `flask export-openapi` to `backend/openapi.json`, served only when `APP_ENV` is `development` or `testing`; `API.md` stays hand-written. Decision E recorded.
- **Design:** `app/api.py`, `app/common/envelope.py`, per-blueprint smorest layering, envelope and error tables, Properties 36 to 38 rewritten, V4 migration notes.
- **Tasks:** new group 24 (migrate the implemented backend), group 23 rewritten for generated docs, task 14.4 reworded, dependency graph rebuilt.
- **Steering:** `api-conventions.md`, `backend.md`, `tech.md`, `structure.md` updated.
- **Implementation sweep:** tasks 1 to 13 are implemented and committed (36 pytest tests pass) on plain `flask.Blueprint` with the old `{ "data": ... }` envelope. Checkpoints 6.5 and 14.6, tasks 14.2 to 14.4, all property tests, and the frontend (15 to 22) are not done.

### Reason
- The product owner asked for `status` and `message` on every response and for flask-smorest to define schemas and responses.

### Impact
- Requirements: 1, 7, 10, 13, 17 and the Decisions Log. Design: layout, envelope, errors, API documentation, Properties 36 to 38. Tasks: 14.4, 23, 24 (new).
- Code: group 24 migrated the backend to flask-smorest and the `status`/`message` envelope, and group 23 added generated OpenAPI, `backend/openapi.json` and `backend/API.md`. This breaks the response shape for any client written against V3.
- Open: Swagger UI assets load from a CDN under flask-smorest (Open Question 4).

## V5 - 2026-11-18
### Changes
- **Specification:** Decision F. Models declare SQLAlchemy relationships only for real cross-table reads (`Board.columns`, `Board.members`, `Card.subtasks`, `Card.attachments`, `Comment.replies`) with `back_populates`, `lazy="raise"`, and no delete cascade; models have no `to_dict`. Repositories load related rows with `selectinload`. New criteria: 13.16 to 13.18, 14.12 (constant query count per list endpoint), 15.8 and 15.9 (query-count and `lazy="raise"` tests).
- **Design:** relationship table, repository loading table, no-`to_dict` rationale, Property 39, V5 notes. Component loading choices: no `joinedload` for assignee or category (not allowed relationships); comment author role comes from a joined `select(Comment, User.role)`.
- **Tasks:** new group 25 (relationships, eager loading, optional tests, checkpoint), after group 24 and before frontend group 15.
- **Steering:** `data-model.md` and `backend.md` rules added; `data-model.md` `login_identifier` example corrected to the functional unique index.

### Reason
- Keep list endpoints inside the 300 ms p95 target while allowing cross-table reads, and keep viewer-dependent serialization out of models.

### Impact
- Requirements: 13, 14, 15, Decisions Log. Design: data model, repository loading, Property 39. Tasks: 25 (new). Code: group 25 implemented (relationships and eager loading, 63 tests passing); no migration needed.

## V6 - 2026-11-18
### Changes
- **Specification (breaking, supersedes the envelope part of Decision E):** Decision G. `status` is a boolean, `true` exactly when the HTTP status is 2xx; the numeric HTTP status travels on the HTTP line only. The message text appears once at the top level. Success is `{ status, message, data }`; error is `{ status: false, message, error: { code, details? } }` with no `error.message`. `VALIDATION_ERROR` carries `error.details` (field to list of messages). Mutating endpoints send a descriptive message; reads send "OK". Req 13.2 to 13.4, 13.11, 13.13, 1.1, 1.15, 7.2, 10.5 and the Glossary updated.
- **Design:** envelope, `EnvelopeApi` error rendering, `ok()` default message, error table, `lib/api.ts` `ApiError(httpStatus, code, message, details)`, Property 36 rewritten, V6 notes.
- **Tasks:** 1.2, 3.2, 8.1, 14.4, 15.3, 23.3, 24.1 to 24.3 and Notes updated; no checkbox changed.
- **Steering:** `api-conventions.md` and `backend.md` updated.

### Reason
- The error body repeated the message in two places, and a boolean `status` is a clearer success flag than echoing the HTTP code.

### Impact
- Requirements: 1, 7, 10, 13 and the Decisions Log. Design: envelope and errors. Tasks: see above.
- Code: not changed yet; group 24 targets the V6 shape. Any client written against V4 must change.
- Open: error messages without custom text fall back to the HTTP reason phrase (design choice, not in requirements).

## V7 - 2026-11-19
### Changes
- **Specification (design/UI):** Decision H. The Frontend is styled with Tailwind CSS v4 and shadcn/ui, themed from the prototype's design tokens. Tailwind's theme is mapped to `styles/tokens.css` (default palette and arbitrary values are not used); `BaseButton`, `BaseBadge`, and `BaseModal` stay the only shared primitives and become thin wrappers over shadcn/ui `Button`, `Badge`, and `Dialog`. The look follows the approved prototype and may be refined (spacing, motion, hierarchy). Req 14.5, 14.9, 14.10 reworded; 14.13 to 14.15 added (Tailwind and shadcn/ui, `lg` = 960px, focus ring from `--ring`). Glossary: Design_Tokens, shadcn/ui.
- **Design:** key-decision row, frontend layout (`components/ui/`, `lib/utils.ts`, Tailwind `globals.css`), component table, new "Frontend Styling" section with the token mapping table, V7 notes.
- **Tasks:** new group 26 (26.1 to 26.5) after task 15 and before the app shell tasks; dependency graph rebuilt.
- **Steering and guidelines:** `tech.md`, `frontend.md`, `structure.md`, and `guidelines/frontend.md` updated (Tailwind and shadcn/ui rules, mobile-first and token examples in Tailwind terms, no arbitrary values, focus ring token corrected from `--focus-ring` to `--ring`).

### Reason
- The product owner asked for Tailwind CSS and the shadcn/ui design system while keeping the existing prototype UI as the reference.

### Impact
- Requirements: 14 (5, 9, 10, 13 to 15), Glossary, Decisions Log. Design: frontend layout, components, styling. Tasks: 26 (new).
- Code: frontend only; the backend and API are unchanged. The existing plain-CSS components are restyled in group 26; their props and logic do not change.
- Resolved on request: follow the prototype strictly for palette and layout, refinements allowed; steering and guidelines may be revised.
- **Look refresh (same revision, V7):** on request the visual reference changed from the HTML prototype to a light project-management dashboard (white surfaces, navy brand, pastel tags, icon rail with boards panel, flat columns, bordered cards). Decision H, Design_Tokens, Req 14.13, design ("Look refresh"), steering (`frontend.md`, `tech.md`), `guidelines/frontend.md`, and the `specs/v7` snapshot now name that reference; the prototype stays the reference for behaviour and content. Tasks: 26.7 added. No code outside `frontend/`.
- **Fidelity pass (same revision, V7):** the restyle was checked against the prototype and rebuilt to match it (frosted surfaces, accent bars, card and header layout, two-pane modal). Req 14.9 now also forbids numeric literals for sizes, layers, durations, and opacities (named token utilities only). Design: "Prototype fidelity" and "No magic numbers" notes. Tasks: 26.6 added.

## V8 - 2026-11-19
### Changes
- **Specification (behaviour and UI):** Decision I. The board and the Card modal follow a Trello-style model: a viewport-locked board with scrolling columns, a large Card modal with attribute chips and popovers, one range calendar for dates, a searchable assignee popover, a modal footer, a collapsible Sidebar with visibility icons, a Home page of boards, HTML5 drag-and-drop (a pointer-event rewrite was reverted, see below), and the Inter font.
- **Requirements:** 3.20 to 3.22 added; 4.20 and 4.21 reworded; 4.30 to 4.35 added; 5.2 reworded ("on drop"); 5.13 added; 14.7 and 14.10 reworded; 14.16 to 14.19 added; 4.36 to 4.38, 7.21, and 8.8 added; Decisions Log row I; introduction counts.
- **Design:** component table (Sidebar, BoardsHome, Board, CardModal, CardChips, DateRangePicker, MemberPicker, shared popover and calendar), layout entries, new section "Board and Card Modal Interaction (Decision I)", V8 revision and migration notes.
- **Tasks:** new group 27 (27.1 to 27.9, with 27.6.1 optional); dependency graph rebuilt (waves 32 to 36 are new, later waves renumbered).
- **Steering and guidelines:** `frontend.md`, `tech.md`, `structure.md`, and `guidelines/frontend.md` updated.

### Reason
- The product owner asked for the Trello board experience: a scrolling main panel, a large card modal with Trello-shaped attributes, a calendar range picker, a searchable member picker, a modal footer, no column select, a collapsible Sidebar, visibility icons, and the Trello font.

### Impact
- Requirements: 3, 4, 5, 14 and the Decisions Log. Design: frontend components and interaction. Tasks: 27 (new).
- Code: frontend only; the backend and API are unchanged (the start-not-after-end rule already exists in the Backend, Req 4.3). New packages: `@fontsource-variable/inter`, `@radix-ui/react-popover`, `react-day-picker`.
- Breaking: the Card modal loses its "Move to column" select, so a Card moves only by drag-and-drop; the HTML5 drag API is used, so touch support depends on the browser (open question). The `/boards` route becomes a page instead of a redirect.
- API (additive): activity rows gain `actor_name`; comments and replies gain `author_name` (Req 7.21, 8.8). No existing field changes.
- Resolved on request: all recommendations accepted: Home first and a boards page; Sidebar toggle with tooltips remembered in the browser; wrapped board names; Inter self-hosted (Atlassian Sans is proprietary); lock icons display only; no board background colour (token tint instead); Dutask palette kept; draft edits committed from the footer; date label stays "End date"; popover for the member picker; pointer-event drag for touch.
- **Revision within V8 (owner feedback after the first build):** smaller corner radii (Dutask look, main panel included); the Sidebar toggle is the logo mark and the app is named RevoTask; the pointer-event drag is reverted to the previous HTML5 behaviour; the card modal panes scroll (bug: the pane grid grew to its content); Attachments become a two-column card with a Link or File selector; Subtasks get their own card; comments and activity show real names (bug: names came only from the board-member list). Req 4.20 (three cards), 4.36 to 4.38, 5.13, 7.21, 8.8, 14.16, 14.19, Decision I reworded. Tasks: 27.5 reworded; new group 28 (28.1 to 28.4). Design: new bullets "Drag", "Pane scrolling", "Names", "Brand and radii".
- **Round 3 within V8 (owner feedback on the modal):** a control, type, and spacing scale (40px controls, 32px compact, 14/13/12px text, 24/20/16px spacing) so inputs, buttons, and chips balance; Activity in its own card; Attachments as bordered tiles with type icons; footer Archive, Delete, Save changes (right-aligned, no Close button); header "card title | board name" that follows the title field; the Sidebar tooltip no longer stays open after a click (cause: `focus-within`); larger board cards and fluid columns; an activity log that reads actor, action, object, from to. Requirements: 4.20, 4.35, 4.36 reworded; 4.39, 4.40, 8.9, 8.10, 14.20 to 14.22 added; Decision I "where applied". Design: bullets "Modal header" to "Board card and columns". Tasks: new group 29 (29.1 to 29.6). Steering: `frontend.md`.
- **API (additive, round 3):** new `metadata` keys on new Activity_Log rows (`card_title`, `changes`, `from_column_name`, `to_column_name`, `assignee_name`, subtask `title`, attachment `name`); no field, schema, or migration change; old rows keep their old keys. The V8 impact line "Code: frontend only" is therefore no longer true for round 3.
- **Round 4 within V8 (owner feedback on the visual system):** one type and spacing system (18/14/14/13/12px, 8px grid, 16px card padding) replacing the round 3 values; a Sidebar type hierarchy and a single Team members section with add (member search, popover or modal) and remove; a one-row Board header without Add Member or the settings icon, with a search modal below 960px; bordered Category chips; an avatar tooltip on board Cards; Card modal attributes as plain icon rows, a header with only the title and close icon, staged attachment changes applied on Save with a discard prompt, confirmation popovers for deletes, equal tile and button heights; a threaded comment layout; searchable selects everywhere; button roles (danger, secondary, primary); the Categories screen built now. Decision J: the Inbox and the two activity feeds are paged with `limit` and `before`. Requirements: 3.23 to 3.25, 4.41 to 4.45, 6.13, 7.22, 8.11, 8.12, 9.11, 9.12, 13.19, 14.23 to 14.26 added; 4.21, 4.35, 14.10, 14.20 reworded. Design: section "Round 4". Tasks: new group 30; 19.2 narrowed to the admin users screen. Steering: `frontend.md`, `api-conventions.md`.
- **API (round 4):** `limit` and `before` query parameters on `GET /api/notifications`, `GET /api/boards/{id}/activity`, and `GET /api/cards/{id}/activity` (response shape unchanged); new `GET /api/boards/{id}/candidates`. This reverses the earlier "no pagination" rule for these three lists only. New frontend packages: `@radix-ui/react-tooltip`, `cmdk`.
- **Round 5 within V8 (owner feedback on header, Home, and the modal):** two-row Board header with bordered sections and a sideways-scrolling category strip with arrows; Home tiles with a coloured cover, description, progress, counts, and member avatars; an analytics strip on Home for Supervisors (owned boards) and Managers, Admins still excluded (Decision B); an optional board description; the Card title shown as text with Edit; aligned date rows; a file drop zone; the modal close icon inside the header row; Category and Priority as two badge types; lowercase Category names. Requirements: 3.23 reworded; 3.26 to 3.29, 4.46 to 4.50, 6.14, 10.8 added. Design: section "Round 5". Tasks: new group 31. Steering: `data-model.md`, `frontend.md`.
- **API and schema (round 5):** `Board.description` (nullable, max 500) with a migration; `GET /api/boards` adds `card_count`, `done_count`, `overdue_count`, `member_count`. Additive only.
- **Round 5 amendment (same version):** the Home board tile has no coloured cover band (owner request); Req 3.29 and the design note are reworded and the `--size-tile-cover` token is removed.
## V9 - 2026-11-20
### Changes
- **Specification and test additions (no behaviour change):** end-to-end Playwright specifications for sign-in and sign-out, happy and negative cases.
- **Requirements:** 1.19 to 1.38 added (IDs `AUTH-E2E-SI-01` to `-10`, `AUTH-E2E-SO-01` to `-08`); 15.10 to 15.15 added (suite files, environment variables `E2E_BASE_URL`, `E2E_USER_IDENTIFIER`, `E2E_USER_PASSWORD`, `.env.example`, no `waitForTimeout`, isolation); Glossary terms added; Open Questions 5 to 7 added; introduction names V9.
- **Design:** section "Auth End-to-End Tests (V9)", end-to-end paragraph in the Testing Strategy, V9 revision notes.
- **Tasks:** new group 32 (32.1 to 32.6); no existing task renumbered; dependency graph gains waves 64 to 67.
### Reason
- The product owner asked for Playwright end-to-end specifications covering sign-in and sign-out.
### Impact
- Requirements: 1 and 15. Design: testing sections. Tasks: 32 (new).
- Code: none yet; the tasks add files only under `frontend/tests/e2e/auth/`, `frontend/playwright.config.ts`, and `frontend/.env.example`. Steering is unchanged.
- Findings, open for the product owner: (5) no Frontend route guard exists and `/boards` is open to Guests, so SO-03 and SO-05 are pending; (6) sign-out is the Sidebar "Log out" item, not a header control; (7) an invalid Token on a server render has no specified behaviour. Also: the Token is the `kanban_token` cookie, not browser storage.

## V10 - 2026-11-20
### Changes
**Specification changes**
- **Decision K, share links (specification, breaking):** Guests no longer browse public Boards. A Guest opens a Board only through `/shared/{token}`, read-only (columns, cards, card details, categories, attachment links); never comments or activity. New nullable unique `Board.share_token`; the Board_Owner, a Manager, and an Admin enable, disable, and regenerate it; disabling or regenerating invalidates the old link and its outstanding file URLs at once; private Boards may have a link; no expiry. A signed-in user with Board_Access who opens a link gets the normal view. Without a link, `/boards` needs sign-in. New Requirement 18. Reverses Req 11.4, 11.5, 11.7 as written in V2 to V9 and the Guest half of Decision A; Members can still read public Boards (restated as Req 11.13).
- **Decision L, header user menu and Profile (specification):** one App_Header on every signed-in page with a User_Menu (Profile above Log out); the Sidebar loses both entries. Profile page: full name, avatar (https URL), read-only Username and Email, change password. New Requirement 19. Resolves V9 Open Question 6.
- **Decision M, separate Username and Email (specification, breaking; supersedes Decision C and resolves Open Question 1):** unique case-insensitive `username` (3 to 30, `a-z 0-9 _ .`) and `email`; `login_identifier` dropped; register shows field-level errors and 409 carries `error.details` per field; `GET /api/auth/availability`; migration backfill and a small blocking Email_Prompt for accounts without an email; candidate search by Username prefix and exact Email, returning `id`, `full_name`, `username` only.
- **Decision N, login form (specification, breaking):** one "Username or email" input; request field `identifier`; the Backend classifies it; one generic 401; `user` shape `{ id, full_name, username, email, avatar_url }`.
- **Decision O, rate limiting (specification, breaking for the error shape; reverses Req 1.18):** Postgres-backed Rate_Limiter: login 5 failures per (identifier, IP) and 20 per IP in 15 minutes, reset on success; register and availability have their own limits; 429 `RATE_LIMITED` with `Retry-After` and `details.retry_after`; thresholds from environment variables, test overrides without `APP_ENV`; the Frontend shows a countdown. New Requirement 20. Amends Decision G: `error.details` also appears on a registration `CONFLICT` and on `RATE_LIMITED`.
- **Decision P, route guard (specification; resolves Open Question 5):** every `(app)` page is a Protected_Route, guarded by `frontend/proxy.ts`.
- **V9 Playwright criteria updated:** AUTH-E2E-SI-01 to -10 and SO-01 to -08 now use the "Username or email" form, the User_Menu_Trigger as the signed-in indicator, and the header sign-out; SO-03 and SO-05 are no longer pending; new IDs SI-11 (rate limit, Throwaway_Identifier), SI-12 (email shape), SO-09 (menu order), SO-10 (no Sidebar Log out or Profile). Req 1.19 to 1.42, 15.11, 15.15 to 15.19.

**Design changes**
- New section "V10 Design"; revised access function, role matrix, auth, users, boards, attachments (share scope), data model (User, Board, RateLimitAttempt), error table, testing strategy, and the Auth End-to-End Tests section. Properties 1, 2, 4, 5, 17, 21, 28, 34, 36 revised; 40 to 46 added. Next.js 16 `proxy.ts` is the guard file; `BaseMenu` and `@radix-ui/react-dropdown-menu` are added.

**Implementation changes**
- None yet. Tasks group 33 (33.1 to 33.27) carries the work. 33.26 (steering and guidelines sync) is done in this revision.

**Steering and guidelines (done in this revision)**
- `product.md` (guest and share-link rule, private-board rule, account and rate-limit rule), `data-model.md` (username and email, `share_token`, `RateLimitAttempt`, visibility example), `api-conventions.md` (429, `details` on 409 and 429, auth, share, profile, candidates), `backend.md` (categories, board access, auth and rate limit, `shared` blueprint), `frontend.md` (app header, login and register, route guard, shared view, sidebar), `structure.md` (`shared` domain, `BaseMenu`), `tech.md` (dropdown-menu package, rate-limit variables), `guidelines/backend.md` (envelope example brought to the current shape with 429; this was already out of date since V4), `guidelines/database.md`, `guidelines/frontend.md`.

### Breaking API changes
- `POST /api/auth/login`: request field `login_identifier` renamed to `identifier`; a value that fits neither shape returns 400 `VALIDATION_ERROR`.
- `POST /api/auth/register`: request fields `login_identifier` replaced by `username` and `email`; duplicate returns 409 `CONFLICT` with `error.details` per field.
- Register and login `user`: `login_identifier` removed, `username` and `email` added (`email` may be null for migrated accounts).
- `GET /api/boards` without a Token: 401 (was the public Boards). `GET /api/boards/{id}`, `/cards`, `/categories`, `/columns`, attachment URL, and card routes without a Token: 401 for public Boards too (were readable).
- Comment endpoints for a Guest on a public Board: 401 (was 403). Activity endpoints for a Guest: 401.
- `GET /api/boards/{id}/candidates`: matches Username prefix and exact Email (was `login_identifier`), returns `id`, `full_name`, `username`.
- New status and code: HTTP 429 `RATE_LIMITED` with a `Retry-After` header on login, register, and availability. `error.details` now also appears on a registration 409 and on 429.
- Signed_File_URL signature string gains a scope suffix, so URLs issued before deploy stop verifying (15-minute lifetime; the existing re-issue path covers them).
- Database: `users.login_identifier` dropped; `users.username`, `users.email`, `boards.share_token`, and `rate_limit_attempts` added (revision `b7d2e4f6a801`, reversible, data-losing in part on downgrade).
- Frontend: Log out and the profile entry leave the Sidebar; `/boards` and every `(app)` page redirect to `/login` without the cookie; `/shared/{token}` is new.

### Additive API changes
- `GET /api/auth/availability`, `GET|PATCH /api/auth/me`, `POST /api/auth/change-password`, `GET|POST|DELETE /api/boards/{id}/share`, `POST /api/boards/{id}/share/regenerate`, and the read-only `/api/shared/{token}` routes (board, cards, categories, card, attachment URL).

### Reason
- The product owner asked to stop exposing public Boards to anyone, to give every signed-in page one account menu, to split Username and Email with field-level errors, to rate limit sign-in and registration, and to bring the V9 e2e criteria in line with the result.

### Impact
- Requirements: 1, 3, 4, 6, 7, 8, 11, 12, 13, 14, 15, 17, new 18 to 20, Glossary, Decisions K to P, Open Questions. Design and tasks as above. Root `specs/v10/` holds the changed domains.
- Open (see `requirements.md` Open Questions 7 to 13): invalid Token on a server render; thresholds for register and availability; change-password rate limit; avatar upload; legacy identifiers that fit neither shape; candidate search by name; shared view assignee name and filters. Findings of the consistency check are listed in the V10 reply and in "Consistency check" below.

### Consistency check (V10)
- Resolved by agreed decisions, no action: Req 1.18 (rate limiting deferred) against Decision O; Open Questions 1, 3, 5, 6; Req 11.4 and the V9 Guest user story against Decision K and P.
- Amendment needing confirmation: Decision G said `error.details` appears only for `VALIDATION_ERROR`. Decisions M and O require it on a registration 409 and on 429. Recorded as an amendment in Decision G, Req 13.3, Property 36, and the steering.
- Deviation needing confirmation: the rate-limit e2e test uses a generated Throwaway_Identifier that belongs to no account, not a seeded throwaway account, because Req 1.38 and 15.15 forbid creating accounts in the suite and the limiter counts failures for unknown identifiers.
- Risk: the per-IP limit of 20 can be reached by repeated suite runs from one address inside 15 minutes (task 33.27).
- Old ticked tasks and the V8 to V9 snapshots keep the V9 wording by design.

### Round 2 within V10 - 2026-11-20
This is an amendment of V10, not a new version. V10 is specified but not implemented, so no V11 exists. Where this entry and the V10 entry above disagree, this entry wins; the V10 text is kept as history.

#### Changes
**Specification changes**
- **Decision Q, registration rate limiting deferred (amends Decision O; answers Open Question 8 for register):** `POST /api/auth/register` has no rate limit. The `register` scope and `RATE_LIMIT_REGISTER_MAX` are removed. Login limiting is unchanged. **Kept by the specifier, not ordered by the owner, and reversible:** the limiter on `GET /api/auth/availability` (default 60 per Client_IP per window, `RATE_LIMIT_AVAILABILITY_MAX`) stays because the endpoint is an enumeration vector. Req 20: RL-07 withdrawn (ID kept), RL-08, RL-10, RL-15 reworded, RL-18 added. "Register rate limiting deferred" is recorded as a gap in Decision Q and Open Question 14.
- **Decision R, avatar upload (amends Decision L; resolves Open Question 10):** the `https` avatar URL rule is withdrawn. The user uploads PNG, JPEG, or WebP, at most 2 MB; the type is read from the leading bytes; the file is stored under a generated name; replacing or removing deletes the old file after commit. Endpoints `POST` and `DELETE /api/auth/me/avatar` and the signature-checked `GET /api/auth/avatars/{user_id}/file`. `avatar_url` is a Signed_File_URL (scope `avatar`) built by the Decision D signing code and file store, issued only in responses to signed-in requests; a Guest on a Share_Link sees initials. `User.avatar_url` becomes `avatar_path`; `PATCH /api/auth/me` and the admin user endpoints reject `avatar_url`. Req 19.8 to 19.10 reworded, 19.18 to 19.33 added, 1.6 reworded; Req 15.20 to 15.22 (API tests, component tests, no avatar test in the auth e2e suite).
- **Decision S, Email shown to staff (reverses part of Decision M; resolves Open Question 12; see Decision M):** `GET /api/boards/{id}/candidates` returns `id`, `full_name`, `username`, and `email`, and matches `full_name`, `username` by prefix, and `email` by exact value, case-insensitively; only the Board_Owner, a Manager, and an Admin may call it. The assignee popover lists the Board's members through `GET /api/boards/{id}/members?include=email` (403 without Board_Staff_Access) and stays hidden from a Member. The Email appears in those two places only, never in Comments, Activity_Log rows, Notifications, the Shared_View, the Sidebar, or a Member-visible list. Req 3.25 reworded, 3.30 to 3.32 added, 4.33 reworded, 15.24.
- **Decision T, invalid Token redirects on every request (amends Decision P; resolves Open Question 7):** `frontend/proxy.ts` rejects a cookie that is not a decodable, unexpired Token and removes it on the redirect; a server render that gets a Backend 401 redirects to the route handler `/session-expired`, which removes the cookie and redirects to `/login` with a Safe_Return_Path in `next`; client-side 401 handling is unchanged; `/login`, `/register`, and `/shared/{token}` ignore a stale cookie, and shared routes treat an invalid Bearer Token as no Token. New Playwright criteria AUTH-E2E-SO-11 (cookie `bogus`, visit `/boards`, expect the login page and the cookie removed) and SO-12 (well-formed but forged Token). Req 1.34 and 1.37 reworded, 1.55 to 1.62 added, 14.28, 15.23, 18.24.
- **Open Questions:** 7, 8 (for register), 10, and 12 marked resolved with a pointer; 14 (availability limiter kept), 15 (avatar visibility), and 16 (Email exposure through name search) added; the others are untouched.

**Design changes**
- New section "Round 2 within V10"; revised auth, users, attachments (avatar signing scope), data model (`avatar_path`, no `register` scope), routing (`proxy.ts`, `/session-expired`), testing strategy, and the auth e2e section. Properties 47 to 49 added (avatar image type and size, safe return path and usable Token, Email exposure); Property 46 (profile update rules) now covers the avatar field being rejected on `PATCH`.

**Implementation changes**
- None. Tasks 33.5, 33.16, 33.18, and 33.19 were edited in place; new tasks 33.28 to 33.40 (no existing ID renumbered).

**Steering and guidelines (done in this revision)**
- `product.md` (registration deferred, avatar upload, Email shown to staff), `data-model.md` (`avatar_path`), `api-conventions.md` (candidates with `email`, `include=email`, avatar endpoints), `backend.md` (register not limited, avatar signing), `frontend.md` (Profile avatar, member search and Email, route guard and `/session-expired`), `tech.md` (rate-limit variables without a register value), `guidelines/backend.md` (content-based upload rule), `guidelines/database.md` (`avatar_path`), `guidelines/frontend.md` (Email rendered by two components, safe return path).
- Root `specs/v10/` snapshot files updated: `00-OVERVIEW`, `01-AUTH`, `03-BOARDS`, `04-CARDS`, `13-API-CONVENTIONS`, `14-NON-FUNCTIONAL`, `15-TESTING`, `18-SHARE-LINKS`, `19-APP-HEADER-PROFILE`, `20-RATE-LIMITING`.

#### Breaking changes (relative to the V10 text above; nothing is released)
- `RATE_LIMIT_REGISTER_MAX` and the `register` limiter scope no longer exist; register never returns 429.
- `GET /api/boards/{id}/candidates` now returns `email` (the V10 text said it never would).
- `avatar_url` is no longer accepted on `PATCH /api/auth/me` or on the admin `POST /api/users` and `PATCH /api/users/{id}` (400); the `users.avatar_url` column becomes `avatar_path` (migration part 4 of revision `b7d2e4f6a801`, which drops existing URL values).
- New Token-free route: `GET /api/auth/avatars/{user_id}/file` (signature only).

#### Reason
- The product owner answered Open Questions 7, 8, 10, and 12: do not rate limit registration yet; let users upload an avatar; show full name and Email in the member search and assignee picker; send an invalid Token to `/login` on every request.

#### Impact
- Requirements: 1, 3, 4, 13, 14, 15, 18, 19, 20, Glossary, Decisions Q to T (L, M, O, P annotated), Open Questions 7, 8, 10, 12, 14 to 16. Design: sections above. Tasks: 33.5, 33.16, 33.18, 33.19 edited; 33.28 to 33.40 added; dependency graph waves 79 to 83.

#### Consistency check (round 2)
- Resolved by the owner's answers, no action: Open Questions 7, 8 (register), 10, 12; the V10 statements that register has its own limit, that avatar is an `https` URL, and that candidates never return `email` are superseded and marked "amended in V10 round 2" in the Decisions Log.
- Decision needing confirmation: the availability limiter was kept by the specifier (Open Question 14). Without a register limit, the 409 on `POST /api/auth/register` answers the same question, so the limiter alone does not stop enumeration.
- Decision needing confirmation: avatar images are visible only to their owner and to Admins, because only the `user` shape carries `avatar_url`; Comments, Board members, and Cards show initials (Open Question 15).
- Risk: name search plus Email in the response lets a Board_Owner read the Email of any account by searching short names (Open Question 16; recommendation: minimum search length 2).
- Deviation from the owner's wording: the avatar endpoints sit under `/api/auth/me/avatar` (next to `GET|PATCH /api/auth/me`), not `/api/users/me/avatar`; the owner gave the path as an example.
- Ordering: checkpoint 33.27 sits before the round 2 tasks (33.28 to 33.38) in the file, and 33.40 re-runs the checks; 33.27 also mentions the suite, which gains SO-11 and SO-12 only in 33.38.
- Risk: avatar files keep EXIF data (no re-encoding); Werkzeug buffers the multipart body, so the reverse proxy must cap it near 3 MB. A file URL works for 15 minutes without a Token once issued (the Decision D trade-off).
- Old ticked tasks and the V8 to V9 snapshots keep their earlier wording by design.
