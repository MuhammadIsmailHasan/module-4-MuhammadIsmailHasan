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
