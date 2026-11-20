# Implementation Plan

## Overview

Version V10. Derived from `requirements.md` and `design.md` in this folder. Backend first (Flask + SQLAlchemy blueprints), then the Next.js frontend, then end-to-end tests and stretch features.

V10 adds group 33 (Decisions K to P): the V10 migration (username, email, share token, rate-limit table), identity changes, the Rate_Limiter, share links and the shared routes, the Guest change (no public browsing), the profile endpoints, the App_Header with the User_Menu, the Profile_Page and Email_Prompt, the route guard `proxy.ts`, the Share button and Shared_View, and the update of the V9 Playwright suite. No existing task is renumbered, and no ticked box changes: ticked tasks describe what was built under V9 (for example `login_identifier`, Guest access to public Boards, the Sidebar Log out item) and group 33 changes that behaviour.
V6 applies Decision G to the envelope. `status` is a boolean, true exactly when the HTTP status is 2xx; the numeric HTTP status travels on the HTTP line only. A success body is `{ "status": true, "message", "data" }`. An error body is `{ "status": false, "message", "error": { "code", "details"? } }`: the message text appears once at the top level, `error` has no `message` field, and `error.details` (field name to list of messages) appears only for `VALIDATION_ERROR`. Mutating endpoints pass a short descriptive message (for example "Card moved"); reads default to "OK". V6 edits tasks 1.2, 3.2, 8.1, 14.4, 15.3, 23.3, 24.1, 24.2, and 24.3 and the Notes. Existing checkbox states are unchanged; tasks already ticked that quote the old envelope are brought to the V6 shape by group 24.

V5 adds group 25, which adds the five SQLAlchemy relationships with `lazy="raise"` and moves related-row loading into the repositories with `selectinload` (Decision F). Group 25 runs after group 24 (the marshmallow schemas replace the DTO functions) and before the checkpoint 14.6 and the frontend group 15. It needs no database migration. Existing checkbox states are unchanged.

V4 adds group 24, which migrates the already-implemented backend (tasks 1 to 13, plain `flask.Blueprint`, `{ "data": ... }` bodies) to flask-smorest with marshmallow schemas and the `status`/`message` envelope (Decision E). Group 24 runs before the envelope property test 14.4, before the frontend (group 15 onward), and before the API documentation group 23. Group 23 is rewritten to document the generated OpenAPI instead of a hand-written `openapi.yaml`. Existing checkbox states are unchanged.

## Tasks

- [x] 1. Backend scaffold, app factory, config, envelope, error handling, CORS, auth decorators
  - [x] 1.1 Create the Flask app factory and configuration
    - Add `backend/requirements.txt` (flask, flask-sqlalchemy, flask-migrate, flask-cors, flask-jwt-extended, argon2-cffi, psycopg, pytest, hypothesis) and `backend/app/__init__.py` with `create_app()`, `backend/app/extensions.py` (`db`, `migrate`).
    - Read `DATABASE_URL`, `JWT_SECRET`, `ALLOWED_ORIGINS`, `FILE_URL_SECRET`, `APP_TIMEZONE`, `UPLOAD_DIR` from the environment; refuse to start when `ALLOWED_ORIGINS`, `JWT_SECRET`, `FILE_URL_SECRET`, or `APP_TIMEZONE` is missing, when `ALLOWED_ORIGINS` contains `*`, or when `APP_TIMEZONE` is not a valid IANA name.
    - Configure CORS once, app-wide, from the allow-list, with `supports_credentials` off.
    - Confirm `backend/.env.example` lists all six variables with empty or placeholder values.
    - _Requirements: 13.1, 13.8, 13.9_
  - [x] 1.2 Add the response envelope and error classes
    - Create `app/common/responses.py` (`ok(data, message=None, status=200)`, returning `{ "status": true, "message", "data" }`; `message` defaults to "OK"; the integer `status` only sets the HTTP status) and `app/common/errors.py` (`ValidationError` 400, `Unauthorized` 401, `Forbidden` 403, `NotFound` 404, `Conflict` 409, generic 500 handler) rendering `{ "status": false, "message", "error": { "code", "details"? } }` with no `error.message` (Decision G; group 24 brings the originally built shape to this one).
    - Register one error handler in the factory; routes contain no try/except.
    - _Requirements: 13.2, 13.3, 13.4, 13.11_
  - [x] 1.3 Add auth helpers, clock, and blueprint skeletons
    - Create `app/common/auth.py` with `ROLE_RANK`, `Actor(id, role)`, `current_actor()` (None for Guest), and `require_role(*roles)` that reads role only from JWT claims (401 without a valid Token, 403 when the role is not listed).
    - Create `app/common/clock.py` (injectable `now()` and `today(tz)` using `APP_TIMEZONE`).
    - Create `routes.py`, `service.py`, `repository.py`, `schema.py` stubs in each of `auth, boards, columns, cards, categories, comments, notifications, analytics, users` and register every blueprint under `/api`.
    - Set up `backend/tests/conftest.py` with an app fixture and fake-repository helpers.
    - _Requirements: 2.7, 2.8, 2.9, 13.1, 13.7_
  - [x]* 1.4 Write unit tests for configuration and CORS
    - Assert startup fails for each missing variable, for `*` in `ALLOWED_ORIGINS`, and for a bad `APP_TIMEZONE`; assert origins are parsed from the comma-separated list.
    - _Requirements: 13.8, 13.9_

- [x] 2. Data models and migrations
  - [x] 2.1 Create shared model base and the User, Board, BoardMember, Column models
    - Add `app/models/` modules with UUID primary keys (`default=uuid.uuid4`) and a `TimestampMixin` (`created_at`, `updated_at`).
    - `User`: `full_name`, `login_identifier` String(255) with a unique index on `lower(login_identifier)`, `password_hash`, `role` enum (member, supervisor, manager, admin), nullable `avatar_url`.
    - `Board`: `name`, `visibility` enum (public, private; default private), nullable `owner_id` FK User, `deleted_at`, `archived_at`. (V8 round 5 adds a nullable `description`, task 31.1.)
    - `BoardMember`: `board_id`, `user_id`, unique `(board_id, user_id)`.
    - `Column`: `board_id`, `name`, Float `order`.
    - _Requirements: 1.6, 3.8, 11.1, 13.5, 13.6_
  - [x] 2.2 Create Card, Category, Subtask, Attachment models
    - `Card`: `column_id`, nullable `category_id` (`ON DELETE SET NULL`), nullable `assignee_id`, `title`, `description`, `priority` enum (high, medium, low), nullable `start_date`/`end_date` Dates, Float `order`, `deleted_at`, `archived_at`; check constraint `end_date >= start_date` when both set.
    - `Category`: `board_id`, `name`, nullable `color`, unique index on `(board_id, lower(name))`.
    - `Subtask`: `card_id`, `title`, `is_done` default false, Float `order`; no assignee, dates, or `deleted_at`.
    - `Attachment`: `card_id`, `name`, nullable `url`, `file_path`, `mime_type`; check `url IS NOT NULL OR file_path IS NOT NULL`; no `deleted_at`.
    - _Requirements: 4.1, 4.2, 4.3, 4.12, 4.15, 4.16, 4.23, 4.29, 6.1, 13.5, 13.6_
  - [x] 2.3 Create Comment, ActivityLog, Notification models
    - `Comment`: `card_id`, `author_id`, nullable self-FK `parent_id`, `content`, `is_priority` default false, `reply_count` default 0; no `deleted_at`.
    - `ActivityLog`: `actor_id`, `action`, `target_type`, `target_id`, JSON `metadata`, `created_at` only.
    - `Notification`: `user_id`, `type` enum (assigned, deadline), `card_id`, `is_read` default false, `notify_date` Date, unique `(user_id, card_id, type, notify_date)`.
    - Use default `RESTRICT` foreign keys; no `ON DELETE CASCADE`.
    - _Requirements: 7.4, 8.1, 8.2, 9.1, 9.3, 13.5_
  - [x] 2.4 Generate the initial migration and a seed helper
    - Create the Flask-Migrate migration for all tables, functional indexes, and check constraints; leave `progress` and `views_count` out of it.
    - Add a CLI or fixture helper that creates users of each role for tests.
    - _Requirements: 13.5, 13.6, 16.3_
  - [x]* 2.5 Write integration tests for database constraints
    - Test case-insensitive uniqueness on `login_identifier` and `(board_id, name)`, the attachment check, the date check, the notification unique constraint, and `SET NULL` on category deletion.
    - _Requirements: 1.4, 4.3, 4.16, 6.12, 9.3_

- [x] 3. Authentication
  - [x] 3.1 Implement auth repository, schema, and service
    - `auth_repository` (`get_by_login`, `create_user`), `schema.py` validation (trim, non-empty full name, identifier at most 255 characters, password at least 8 characters), `auth_service.register` (argon2 hash, role `member`, 409 on case-insensitive duplicate) and `login` (case-insensitive match, 401 on bad credentials).
    - Apply no identifier format validation beyond trimming, non-empty, 255 maximum, and uniqueness.
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.12, 1.13, 1.17_
  - [x] 3.2 Implement routes, JWT issuing, and logout
    - `POST /api/auth/register` and `POST /api/auth/login` return `{ user: {id, full_name, login_identifier, avatar_url}, token }`; Token carries user id and role, fixed 24-hour expiry, no revocation list.
    - `POST /api/auth/logout` returns `{ "status": true, "message": "Logged out", "data": null }` and revokes nothing.
    - Defer rate limiting; add no Google OAuth route.
    - _Requirements: 1.1, 1.2, 1.14, 1.15, 1.16, 1.18, 1.11_
  - [x]* 3.3 Write property test for registration and login round trip
    - **Property 1: Registration and login round trip**
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.13**
  - [x]* 3.4 Write property test for registration validation and unique identifier
    - **Property 2: Registration validation and unique login identifier**
    - **Validates: Requirements 1.4, 1.5, 1.12, 1.17**
  - [x]* 3.5 Write unit tests for Token expiry and logout
    - Token expires 24 hours after issue; after logout the Token still validates until expiry.
    - _Requirements: 1.14, 1.15, 1.16_

- [x] 4. Board access, boards, columns, members, visibility, archive
  - [x] 4.1 Implement board access functions
    - In `board_service`, add `can_access(user, board)`, `can_write_staff(user, board)`, `is_owner(user, board)`, and `require_access(user, board)` (404 for soft-deleted, 401 for Guest on private, 403 for signed-in without access).
    - Add `board_repository` functions `get_by_id`, `is_member`, `list_visible(user)`; all queries exclude `deleted_at IS NOT NULL` by default.
    - _Requirements: 2.2, 3.4, 3.5, 11.5, 11.6, 11.11, 13.10_
  - [x]* 4.2 Write property test for Board_Access
    - **Property 4: Board_Access function**
    - **Validates: Requirements 3.4, 6.5, 7.1, 8.3, 8.4, 11.6, 11.11, 12.1, 12.7**
  - [x]* 4.3 Write property test for the permission matrix
    - **Property 3: Permission matrix and role source**
    - **Validates: Requirements 1.8, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 3.3, 3.4, 3.5, 3.7, 4.1, 4.4, 4.7, 6.1, 6.4, 7.3, 7.8, 10.4, 11.3, 11.9**
  - [x] 4.4 Implement board creation, listing, and retrieval
    - `POST /api/boards` (manager, admin) inserts the Board and five Default_Columns (`Todo, In Progress, Review, Revision, Done`, `order` 0 to 4) in one transaction.
    - `GET /api/boards` uses `list_visible` (Guest: public non-deleted; signed-in: public plus accessible); `GET /api/boards/{id}` calls `require_access` and `serialize_board` omits `comments` and `activity_log` for a Guest.
    - _Requirements: 2.1, 3.1, 3.3, 3.9, 3.10, 11.4, 11.7, 11.12_
  - [x]* 4.5 Write property test for default column seeding
    - **Property 6: Board creation seeds default columns**
    - **Validates: Requirements 3.1**
  - [x]* 4.6 Write property test for board list visibility
    - **Property 34: Board list visibility**
    - **Validates: Requirements 11.4, 11.6, 11.12**
  - [x] 4.7 Implement board update, owner reassignment, visibility, archive, soft delete
    - `PATCH /api/boards/{id}`: `owner_id` change by Manager or Admin only, new owner must have role `supervisor` (400 otherwise), `null` clears; visibility change by Manager, Admin, or owner/BoardMember Supervisor; log `board.owner_changed` and visibility changes in the same transaction.
    - `POST /api/boards/{id}/archive`, `POST /api/boards/{id}/unarchive`, `DELETE /api/boards/{id}` (soft, sets `deleted_at`), all Manager and Admin only; never hard-delete a Board.
    - _Requirements: 3.2, 3.6, 3.7, 3.8, 3.16, 3.17, 3.18, 3.19, 11.2, 11.3, 11.8, 11.9_
  - [x]* 4.8 Write property test for owner reassignment
    - **Property 19: Owner reassignment validation**
    - **Validates: Requirements 3.2, 3.16, 3.17, 3.18, 3.19**
  - [x]* 4.9 Write property test for soft delete and archive round trip
    - **Property 8: Soft delete hides without removing** (Board part; the card children part is completed in task 5.7)
    - **Property 9: Archive round trip** (Board part)
    - **Validates: Requirements 3.6, 3.8, 11.8, 11.10**
  - [x] 4.10 Implement board members endpoints
    - `GET /api/boards/{id}/members` (requires `can_access`), `POST /api/boards/{id}/members` body `{ "user_id" }` (owner, Manager, Admin; 409 when the pair exists; 404 when the user does not exist), `DELETE /api/boards/{id}/members/{user_id}` (404 when the pair does not exist); write one `board.member_added` or `board.member_removed` Activity_Log row in the same transaction.
    - _Requirements: 3.11, 3.12, 3.13, 3.14, 3.15_
  - [x]* 4.11 Write property test for BoardMember add and remove
    - **Property 18: BoardMember add and remove**
    - **Validates: Requirements 3.11, 3.12, 3.13, 3.14, 3.15**
  - [x] 4.12 Implement column creation
    - `POST /api/boards/{board_id}/columns` guarded by `require_access` then `can_write_staff`; new Column gets `order = max + 1`.
    - _Requirements: 2.6, 3.4, 3.5_
  - [x]* 4.13 Write property test for column append order
    - **Property 7: Column append order**
    - **Validates: Requirements 3.4**

- [x] 5. Cards, subtasks, attachments, assignment
  - [x] 5.1 Implement signing and clock-injectable file URL helpers
    - `app/common/signing.py`: `sign_file_url(attachment_id, now)` returns `/api/attachments/{id}/file?exp=&sig=` with `exp = now + 900 s` and HMAC-SHA256 over `"{id}.{exp}"` using `FILE_URL_SECRET`; `verify_file_signature(...)` uses `hmac.compare_digest` and rejects missing, tampered, or expired values.
    - _Requirements: 4.18, 4.24, 4.25_
  - [x]* 5.2 Write property test for signed URL validity and expiry
    - **Property 20: Signed file URL validity and expiry**
    - **Validates: Requirements 4.18, 4.24, 4.25**
  - [x] 5.3 Implement card CRUD, archive, soft delete
    - `card_repository` and `card_service`: `POST /api/columns/{column_id}/cards`, `GET /api/cards/{id}`, `PATCH /api/cards/{id}`, `DELETE /api/cards/{id}` (soft), `POST /api/cards/{id}/archive`, `POST /api/cards/{id}/unarchive`.
    - Validate priority (high, medium, low) and `end_date >= start_date` (400 `VALIDATION_ERROR`); creation, delete, and archive need `require_access` then `can_write_staff` (Members get 403); edits by a Member only when `assignee_id` equals the Member, by Supervisor/Manager/Admin only with Board_Staff_Access; write one Activity_Log row per change.
    - Child rows (subtasks, attachments, comments) are hidden by joining `Card.deleted_at`; never hard-delete a Card.
    - _Requirements: 2.6, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10, 4.23, 4.29, 11.10_
  - [x]* 5.4 Write property tests for card validation and edit scope
    - **Property 10: Card field validation**
    - **Validates: Requirements 4.1, 4.2, 4.3**
    - **Property 11: Member edit and move scope** (edit part; move part is completed in task 6.4)
    - **Validates: Requirements 4.8, 4.9, 4.10**
  - [x]* 5.5 Write property tests for soft delete of cards and archive round trip
    - **Property 8: Soft delete hides without removing** (card and children part)
    - **Validates: Requirements 4.5, 4.23, 4.29, 12.3**
    - **Property 9: Archive round trip** (card part)
    - **Validates: Requirements 4.6, 11.10**
  - [x] 5.6 Implement assignment and unassignment
    - `card_service.assign_card`: non-null `assignee_id` inserts an `assigned` Notification (`notify_date` = today in `APP_TIMEZONE`, conflict ignored) and a `card.assigned` Activity_Log row in the same commit; `null` clears the assignee, writes `card.unassigned`, creates no Notification.
    - _Requirements: 4.11, 4.28, 9.1_
  - [x]* 5.7 Write property test for assignment effects
    - **Property 12: Assignment and unassignment effects**
    - **Validates: Requirements 4.11, 4.28, 9.1**
  - [x] 5.8 Implement subtasks
    - `card_service.add_subtask`, `toggle_subtask`, `reorder_subtasks`, `delete_subtask` with `POST /api/cards/{id}/subtasks`, `PATCH /api/subtasks/{id}` (`title`, `is_done`, `order`), `DELETE /api/subtasks/{id}`; `is_done` defaults to false; edit rights as in task 5.3. Reorder uses `app/common/ordering.py` (created in task 6.1; stub the import here with the same interface or implement 6.1 first).
    - _Requirements: 4.12, 4.13, 4.14_
  - [x]* 5.9 Write property test for subtasks
    - **Property 13: Subtask toggle round trip and deletion**
    - **Validates: Requirements 4.12, 4.13, 4.14**
  - [x] 5.10 Implement attachments and signed file URL endpoints
    - `POST /api/cards/{id}/attachments` (JSON link or multipart upload; accept only PDF, Word, RAR; 400 for neither `url` nor file or a disallowed type before writing storage), `DELETE /api/attachments/{id}`.
    - Store uploads under the private `UPLOAD_DIR`, not mounted as a static route.
    - `GET /api/attachments/{id}/url` (open to Guests on public boards) re-runs `require_access` and returns `{ file_url, expires_at }`; `GET /api/attachments/{id}/file?exp=&sig=` takes no Token and returns 403 for a bad, tampered, missing, or expired signature, and 404 when the card or board is soft-deleted.
    - `serialize_card(card, viewer)` embeds a fresh signed `file_url` per uploaded attachment, returns link `url` as stored, and omits `comments` and `activity` for a Guest.
    - _Requirements: 4.15, 4.16, 4.17, 4.18, 4.24, 4.25, 4.26, 4.27, 8.5_
  - [x]* 5.11 Write property tests for attachments
    - **Property 14: Attachment validity**
    - **Validates: Requirements 4.15, 4.16, 4.17, 4.27**
    - **Property 21: Attachment access gating**
    - **Validates: Requirements 4.18, 4.26, 15.7**
  - [x]* 5.12 Write pytest tests for attachment access
    - Cover a permitted viewer, an unrelated Member (403), a Guest on a private board (401), a Guest on a public board (URL issued), an expired signature (403), and a modified `sig` or `exp` (403).
    - _Requirements: 15.7_

- [x] 6. Ordering and card move
  - [x] 6.1 Implement ordering helpers
    - `app/common/ordering.py`: `position_for(prev, next, siblings)` (empty list `1.0`, first `min - 1`, last `max + 1`, otherwise average), `needs_rebalance(prev, next)` (gap below `1e-6`), `rebalance(siblings)` renumbering `1.0, 2.0, ...` preserving order.
    - _Requirements: 4.13, 5.1, 5.10, 5.11_
  - [x]* 6.2 Write property test for ordering and rebalance
    - **Property 15: Drop order and rebalance (cards and subtasks)**
    - **Validates: Requirements 4.13, 5.1, 5.10, 5.11**
  - [x] 6.3 Implement move card
    - `PATCH /api/cards/{id}/move` with `column_id`, `prev`, `next` neighbour ids; `card_service.move_card`: `require_access`; Member only when assigned; Supervisor, Manager, Admin only with `can_write_staff`; 400 when the target column belongs to another board; recompute order server-side (ignore client `order`), renumber the column in the same transaction when the gap is below `1e-6`; write exactly one `card.moved` row with source and target column; commit once.
    - Return 401 without a Token.
    - _Requirements: 5.1, 5.2, 5.4, 5.5, 5.6, 5.7, 5.8, 5.10, 5.11, 5.12_
  - [x]* 6.4 Write property tests for move
    - **Property 16: Move persists, logs once, and stays on the board**
    - **Validates: Requirements 5.2, 5.8, 5.9, 5.12**
    - **Property 11: Member edit and move scope** (move part)
    - **Validates: Requirements 4.8, 4.9, 4.10, 5.4, 5.5, 5.6**
  - [x] 6.5 Checkpoint - Ensure all tests pass, ask the user if questions arise

- [x] 7. Categories
  - [x] 7.1 Implement the categories blueprint
    - `GET /api/boards/{board_id}/categories` (`require_access` only, no role check, Guests on public boards allowed, only that board's categories), `POST /api/boards/{board_id}/categories`, `PATCH /api/categories/{id}`, `DELETE /api/categories/{id}` (the last three need `can_write_staff`).
    - Case-insensitive duplicate name on a board returns 409 `CONFLICT` on create and rename; deleting a category nulls `Card.category_id`; categories of a soft-deleted board stay stored and are unreachable.
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.12_
  - [x]* 7.2 Write property test for categories
    - **Property 17: Categories are board-scoped and name-unique**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.12**

- [x] 8. Comments
  - [x] 8.1 Implement comment creation and replies
    - `POST /api/cards/{id}/comments` (Member, Supervisor, Manager with `can_access`; Admin 403; blank body 400 `VALIDATION_ERROR` with `error.details.content` as a list whose first string is `content is required`) and `POST /api/comments/{id}/replies` (400 when the target has a non-null `parent_id`; increments the parent's `reply_count` in the same transaction). Provide no like or vote endpoint.
    - A Guest calling any comment endpoint gets 403 on a public board and 401 on a private board, with no `comments` field.
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.16, 14.3_
  - [x]* 8.2 Write property tests for comment creation
    - **Property 22: Blank comments rejected**
    - **Validates: Requirements 7.1, 7.2**
    - **Property 23: Reply count invariant and depth cap**
    - **Validates: Requirements 7.4, 7.5**
  - [x] 8.3 Implement priority flag and listing
    - `PATCH /api/comments/{id}/priority` (Manager only toggles `is_priority`; others 403, no Token 401).
    - `GET /api/cards/{id}/comments?sort=latest|popular`: priority comments first (newest first), then others by `created_at DESC` (latest or omitted) or `(reply_count DESC, created_at DESC)` (popular); replies nested oldest-first regardless of sort; each comment has `reply_count`, `is_priority`, `can_create_card = viewer.role in (supervisor, manager, admin) and author.role == "manager"`.
    - _Requirements: 7.7, 7.8, 7.9, 7.10, 7.11, 7.12, 7.13, 7.14, 7.15_
  - [x]* 8.4 Write property tests for comment listing
    - **Property 24: Priority flag toggle round trip**
    - **Validates: Requirements 7.7, 7.8**
    - **Property 25: Top-level comment ordering**
    - **Validates: Requirements 7.9, 7.10, 7.11**
    - **Property 26: Reply ordering independent of sort**
    - **Validates: Requirements 7.12**
    - **Property 27: Comment flags**
    - **Validates: Requirements 7.13, 7.14, 7.15**
  - [x]* 8.5 Write pytest tests for comment creation
    - Cover success, validation failure (blank body), unauthenticated (401), and unauthorized (Guest and Admin) cases against the Flask test client.
    - _Requirements: 15.1_

- [x] 9. Activity log
  - [x] 9.1 Implement the activity repository and read endpoints
    - `activity_repository.add(...)` is the only write function (no update or delete); each service calls it inside its own transaction, and a failed call inserts no row.
    - `GET /api/cards/{id}/activity` returns rows with `target_type = card` and that id; `GET /api/boards/{id}/activity` returns rows for the board's cards, columns, and board-level actions; both require `can_access` and return no `activity`/`activity_log` field to a Guest, even when requested explicitly.
    - Log user management actions (`user.created`, `user.updated`, `user.role_changed`) through the same repository (wired in task 13.1).
    - _Requirements: 1.7, 8.1, 8.2, 8.3, 8.4, 8.5_
  - [x]* 9.2 Write property tests for activity
    - **Property 29: One activity row per state change**
    - **Validates: Requirements 1.7, 8.1, 8.2**
    - **Property 30: Activity queries return the right rows**
    - **Validates: Requirements 8.3, 8.4**
  - [x]* 9.3 Write property test for guest privacy
    - **Property 28: Guest responses never include comments or activity**
    - **Validates: Requirements 7.16, 8.5, 11.7, 12.6, 14.3**

- [x] 10. Notifications and deadline job
  - [x] 10.1 Implement inbox and read endpoints
    - `GET /api/notifications` returns `{ items, unread_count }` for the caller only; `PATCH /api/notifications/{id}/read` and `PATCH /api/notifications/read-all` act only on the caller's rows; a foreign or unknown id returns 404.
    - Notifications are created server-side only.
    - _Requirements: 9.4, 9.5, 9.8, 9.9, 9.10_
  - [x] 10.2 Implement the deadline job
    - `app/jobs/deadlines.py` `run(now)`: compute `today` in `APP_TIMEZONE`, select cards with `end_date == today`, `deleted_at IS NULL`, and an assignee, insert `deadline` notifications with `INSERT ... ON CONFLICT DO NOTHING`; expose it as `flask notify-deadlines` and a daily schedule.
    - _Requirements: 9.2, 9.3_
  - [x]* 10.3 Write property tests for notifications
    - **Property 31: Deadline job notifies once, in APP_TIMEZONE**
    - **Validates: Requirements 9.2, 9.3**
    - **Property 32: Inbox isolation and read marking**
    - **Validates: Requirements 9.5, 9.8, 9.9, 9.10**

- [x] 11. Analytics
  - [x] 11.1 Implement analytics endpoints
    - `GET /api/boards/{id}/analytics`: Manager any board; Supervisor only when `owner_id == actor.id` (BoardMember Supervisor 403); Member and Admin 403; no Token 401.
    - `GET /api/analytics/boards` (Manager only) returns one summary per board in one response.
    - Use one grouped query per board returning `done`, `in_progress`, `overdue`, `total`, `done_delta` for the previous 7 days; overdue is a non-deleted card with `end_date < today` (in `APP_TIMEZONE`) not in the `Done` column; no per-card data in the payload.
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7_
  - [x]* 11.2 Write property test for analytics
    - **Property 33: Analytics access and correctness**
    - **Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5, 10.7**

- [x] 12. Card search and filter
  - [x] 12.1 Implement the board cards list
    - `GET /api/boards/{id}/cards?search=&filter[priority]=&filter[assignee]=&filter[category]=`: `require_access` first (403 signed-in, 401 Guest on private); case-insensitive substring match on `title` or `description`; filters combine with AND; unsupported filter key returns 400 `VALIDATION_ERROR`; always exclude soft-deleted cards; Guest results contain card data only.
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.6, 12.7_
  - [x]* 12.2 Write property test for search and filter
    - **Property 35: Search and filter correctness**
    - **Validates: Requirements 12.1, 12.2, 12.3, 12.4**

- [x] 13. User administration
  - [x] 13.1 Implement admin user management
    - `GET /api/users`, `POST /api/users`, `PATCH /api/users/{id}` (edit, assign role), Admin only; each mutation writes `user.created`, `user.updated`, or `user.role_changed` to the Activity_Log in the same transaction; non-Admin gets 403, no Token 401.
    - _Requirements: 1.7, 1.8, 2.4_
  - [x]* 13.2 Write unit tests for user administration
    - Cover Admin success, Member, Supervisor, and Manager 403, no Token 401, and the activity row.
    - _Requirements: 1.7, 1.8_

- [x] 14. Backend checkpoint and cross-cutting tests
  - [x]* 14.1 Write the 401/403 sweep test for every mutating endpoint
    - Enumerate registered POST, PATCH, PUT, DELETE routes; assert 401 with no Token and 403 with an insufficient-role Token, excluding the public auth routes and the signature-gated file route; fail when a mutating route is missing from the list.
    - _Requirements: 2.8, 2.9, 2.10, 15.5_
  - [x]* 14.2 Write property test for 401 versus 403 versus 404
    - **Property 5: 401 versus 403 versus 404**
    - **Validates: Requirements 2.8, 2.9, 11.5, 12.7, 13.10**
  - [x]* 14.3 Write the Board_Access matrix and private board tests
    - Cover {guest, member, supervisor owner, supervisor BoardMember, supervisor unrelated, manager, admin} against {public, private} for columns, cards, categories, comments, activity, search, and attachments, including an unrelated Supervisor getting 403 on public-board writes and an unrelated Member getting 403 on a private board.
    - _Requirements: 15.4, 15.6_
  - [x]* 14.4 Write property test for the response envelope
    - Run against the Flask test client for every registered `/api` route (excluding the documentation routes and the successful bytes of the signed file route), including unknown routes and wrong methods; requires group 24.
    - Assert success bodies are exactly `{ status: true, message, data }` and error bodies are exactly `{ status: false, message, error: { code, details? } }`, with `status` a boolean that is true exactly when the HTTP status is 2xx (never a number), `message` a non-empty string, no `error.message` field, and `error.details` present only for validation failures, which return 400 `VALIDATION_ERROR` (never 422) with every failing field mapped to a non-empty list of strings.
    - **Property 36: Response envelope**
    - **Validates: Requirements 13.2, 13.3, 13.4, 13.11, 13.13**
  - [x]* 14.5 Write static checks
    - Assert no `.query` call outside a `repository.py` file, and that `.env.example` files list the required variables and no real `.env` is tracked.
    - _Requirements: 13.7, 13.9, 15.4_
  - [x] 14.6 Checkpoint - Ensure all tests pass, ask the user if questions arise

- [x] 15. Frontend scaffold, tokens, shared components, API client, auth pages
  - [x] 15.1 Scaffold the Next.js app and design tokens
    - Initialize Next.js (App Router, TypeScript) in `frontend/`; confirm `frontend/.env.example` lists `NEXT_PUBLIC_API_URL`.
    - Create `styles/tokens.css` copying the prototype's `:root` custom properties (`--brand`, `--surface-*`, `--ink*`, `--space-*`, `--radius-*`, `--label-*`) from `design/kanban-prototype.html`; use only these variables for colors, spacing, and radii, with mobile-first base styles and `min-width` queries (960px breakpoint).
    - _Requirements: 14.5, 14.9_
  - [x] 15.2 Create shared components
    - `BaseButton`, `BaseBadge`, `BaseModal` in `frontend/components/shared/`, styled only from `tokens.css`; all pages import these instead of raw `<button>`, badges, or modals.
    - _Requirements: 14.9, 14.10_
  - [x] 15.3 Create the API client and session handling
    - `lib/api.ts`: adds the Bearer token, reads the boolean `status` of `{ status, message, data }` and returns `data` when it is true; when it is false, throws a typed `ApiError(httpStatus, code, message, details)` where `httpStatus` comes from the `Response`, `code` from `error.code`, `message` from the top-level `message`, and `details` from `error.details` (field to list of messages, present for `VALIDATION_ERROR`; forms map it onto their fields). A 401 clears the stored Token and redirects to login; logout calls `POST /api/auth/logout` then discards the Token.
    - _Requirements: 1.15, 1.16, 13.2, 13.3, 13.13_
  - [x] 15.4 Build login and register pages
    - `app/(auth)/login/page.tsx` and `register/page.tsx` using an `AuthSplitLayout` Server Component: brand panel beside an elevated rounded form card on desktop; brand panel hidden at mobile width.
    - Forms submit `login_identifier` and password through the API client and store the returned Token.
    - _Requirements: 1.1, 1.2, 1.9, 1.10, 14.4, 14.5_
  - [x]* 15.5 Write component tests for shared components and auth pages
    - Test that the auth form renders and shows server errors; test `BaseButton`, `BaseBadge`, `BaseModal` basics with React Testing Library.
    - _Requirements: 1.9, 14.10_

- [x] 16. App shell, sidebar, side panel
  - [x] 16.1 Build the app shell
    - `app/(app)/layout.tsx` (Server Component) with `Sidebar` (Client): brand, nav with Inbox and Activity links, Boards list from `GET /api/boards` as the board switcher, team members, profile; Categories entry only for supervisor, manager, admin.
    - Below 960px the sidebar is an off-canvas drawer behind a scrim with its toggle in a persistent header; at 960px and above it stays visible.
    - Place primary actions (add card, open Inbox, switch Board) in the persistent header or bottom third on mobile.
    - _Requirements: 3.9, 6.11, 14.6, 14.7, 14.8, 14.11_
  - [x] 16.2 Build the side panel host
    - `SidePanel` (Client) sliding in from the right with one shared `toggleSidePanel("inbox" | "activity")` called by the sidebar items and the header bell; render a view only when the API returned its data.
    - _Requirements: 8.6, 9.6, 9.7_

- [x] 17. Board view, filters, drag-and-drop
  - [x] 17.1 Build the board page and filter row
    - `app/(app)/boards/[id]/page.tsx` (Server Component) fetches columns and cards; `FilterRow` (Client) renders category chips from `GET /api/boards/{id}/categories` (no hard-coded list), re-fetches on board switch, and a search input; chip selection and search call `GET /api/boards/{id}/cards`.
    - _Requirements: 3.10, 6.9, 6.10, 12.5_
  - [x] 17.2 Implement drag-and-drop
    - `lib/ordering.ts` with pure `computeDropOrder` mirroring the backend rules (first `min - 1`, last `max + 1`, empty `1.0`, average otherwise).
    - `Board` (Client): placeholder at the drop target, FLIP animation of siblings, `PATCH /api/cards/{id}/move` on `dragend`, reconcile with the response, revert the card on failure; after refresh the card renders at its moved position.
    - Add a per-column "+ Add a card" action inside the thumb-reach rule.
    - _Requirements: 5.2, 5.3, 5.9, 14.8_
  - [x]* 17.3 Write fast-check test for drop order
    - Mirror Property 15 for `computeDropOrder`.
    - **Property 15: Drop order and rebalance (cards and subtasks)**
    - **Validates: Requirements 4.13, 5.1, 5.10, 5.11**

- [ ] 18. Card modal, subtasks, attachments, comments
  - [x] 18.1 Build the two-pane card modal
    - `CardModal` (Client) using `BaseModal`: left pane has title, description (`CardDescription` Server Component), priority, dates, attachments, subtask checklist, and `ActivityList` (Server Component); right pane has the comment thread and composer.
    - "Save changes" commits the left pane without closing the modal or affecting the composer; omit the activity section and comment thread when the response omits `activity` or `comments`.
    - _Requirements: 4.20, 4.21, 7.20, 8.7, 14.11_
  - [x] 18.2 Build the subtask checklist and attachment list
    - `SubtaskChecklist` (Client): flat checkbox list, inline-editable titles, drag handle reorder, one-click toggle calling `PATCH /api/subtasks/{id}`.
    - `AttachmentList` (Client): links open with `target="_blank" rel="noopener noreferrer"`, no in-app preview; before opening, request a fresh URL from `GET /api/attachments/{id}/url` when the `exp` query value has passed or a request returns 403.
    - _Requirements: 4.14, 4.19, 4.22_
  - [x] 18.3 Build the comment thread and composer
    - `CommentThread` (Client): priority comments first with a priority indicator, remaining top-level comments under a Latest/Popular toggle with a reply-count badge, replies nested, Reply action only where `parentId === null`, no like button, "Create card" button only where `comment.canCreateCard`, a Manager-only "Mark as priority" action.
    - `CommentComposer` posts independently without closing the modal.
    - _Requirements: 7.17, 7.18, 7.19, 7.20_
  - [ ]* 18.4 Write component tests for card modal pieces
    - Reply only on top-level comments; create-card button only when `canCreateCard`; thread, activity, and inbox omitted when the data is absent; `AttachmentList` renders `target="_blank" rel="noopener noreferrer"` and requests a fresh URL when expired.
    - _Requirements: 4.19, 7.18, 7.19, 7.20, 8.7, 9.7_

- [ ] 19. Inbox, activity panel, categories screen, members screen
  - [x] 19.1 Build inbox and activity panel contents
    - Inbox view lists `GET /api/notifications` with unread count and mark-read / read-all actions; Activity view lists the board feed from `GET /api/boards/{id}/activity`; neither polls or computes notifications client-side.
    - _Requirements: 8.6, 9.4, 9.5, 9.6, 9.8, 9.9_
  - [ ] 19.2 Build the admin users screen
    - `app/(app)/admin/users/page.tsx` for Admin user management. (V8 round 4: the Categories screen moved to task 30.8; the board members screen is replaced by the Sidebar Team members section, task 30.3.)
    - _Requirements: 1.7, 3.11, 3.14, 6.11_
  - [ ] 19.3 Checkpoint - Ensure all tests pass, ask the user if questions arise

- [ ] 20. End-to-end test
  - [ ] 20.1 Write the Playwright Kanban journey
    - Against the deployed URL: register, log in, open a board, add and drag a card, reload and confirm position, open the card modal, comment, reply, toggle Latest and Popular.
    - Use web-first assertions such as `expect(locator).toBeVisible()`; never use `waitForTimeout`.
    - _Requirements: 15.2, 15.3_
  - [ ]* 20.2 Write viewport and static checks
    - Playwright viewport tests at 360, 414, and 960 pixels (no horizontal scroll, drawer below 960, sidebar visible at 960); a CI grep step that fails if `waitForTimeout` appears in any Playwright test file.
    - _Requirements: 14.4, 14.6, 14.7, 15.3_

- [ ] 21. Final checkpoint
  - [ ] 21.1 Ensure all tests pass, ask the user if questions arise
    - Run backend `pytest` and frontend tests; confirm no `.env` file is committed and the 401/403 sweep passes.
    - _Requirements: 13.9, 15.1, 15.4, 15.5_

- [ ] 22. Stretch features (build only after tasks 1 to 21 work end-to-end)
  - [ ] 22.1 Add progress and views_count to the backend
    - Add a later migration with nullable 0 to 10 integer `Card.progress` and integer `Card.views_count` default 0; expose them in card serialization and edit validation; increment `views_count` on card open.
    - _Requirements: 16.1, 16.3_
  - [ ] 22.2 Add the progress meter, views counter, and decorative tabs
    - Render the per-card progress meter, views counter, and Overview, Notes, Questions tabs in `CardModal` as in the prototype, behind a feature flag, using only token variables.
    - _Requirements: 16.2, 16.3_

- [x] 23. API documentation (generated OpenAPI, Swagger UI, API.md)
  - [x] 23.1 Finish the `APP_ENV` gating and remove the hand-written documentation stack
    - Confirm `APP_ENV=` is listed in `backend/.env.example` and that `create_app()` defaults it to `production` without failing when it is missing.
    - Confirm `OPENAPI_URL_PREFIX`, `OPENAPI_JSON_PATH`, `OPENAPI_SWAGGER_UI_PATH`, and `OPENAPI_SWAGGER_UI_URL` are set only when `APP_ENV` is `development` or `testing`, so `/api/docs` and `/api/openapi.json` return the 404 envelope otherwise; use `APP_ENV=testing` in the default test app and `production` in the production test.
    - Ensure `backend/requirements.txt` has no `flask-swagger-ui` or `pyyaml`, and that no `backend/app/docs.py` or `backend/openapi.yaml` exists.
    - Exclude the documentation routes from the 401/403 sweep in task 14.1 (they are read-only, public, and carry no secrets).
    - _Requirements: 17.4, 17.5, 17.6, 17.7, 17.10_
  - [x] 23.2 Complete the generated OpenAPI metadata and export it
    - On every endpoint add `@blp.doc` summary and description (roles allowed, access rule), a tag per blueprint, request and response examples where useful, `security=[{"bearerAuth": []}]` on protected operations, and the 400/401/403/404/409 error responses (`@blp.alt_response` or `Api.ERROR_SCHEMA`); give every marshmallow field a description so the generated document is complete.
    - Run `flask export-openapi` and commit the generated `backend/openapi.json`; never edit it by hand.
    - _Requirements: 17.1, 17.3_
  - [x] 23.3 Write `backend/API.md`
    - Cover the envelope (boolean `status`, one top-level `message`, `data`; errors as `error: { code, details? }` with no `error.message`), error codes, authentication, the role matrix, signed file URLs, ordering and move semantics, then one table plus an example request and response per blueprint group. Examples show `{ "status": true, "message": "Card moved", "data": {...} }` for a mutating call, `"message": "OK"` for a read, and a 400 example `{ "status": false, "message": "Validation failed", "error": { "code": "VALIDATION_ERROR", "details": { "content": ["Missing data for required field."] } } }`; state that the generated `openapi.json` is the source of truth and how to enable Swagger locally (`APP_ENV=development`), and that it is off in production.
    - _Requirements: 17.2_
  - [x]* 23.4 Write the drift and production-gate tests
    - **Property 37: Every route is documented** (iterate `app.url_map` under `/api`, excluding `static` and the documentation routes, and assert each method and path has an operation in `api.spec.to_dict()["paths"]`, and the reverse)
    - **Property 38: Documentation hidden outside development and testing** (`/api/docs` and `/api/openapi.json` return 200 for `development` and `testing`, and the 404 envelope for `production`, unset, or any other value)
    - **Validates: Requirements 17.1, 17.4, 17.5, 17.6, 17.8, 17.9**

- [x] 24. Migrate the implemented backend to flask-smorest and the status/message envelope
  - [x] 24.1 Add flask-smorest, the envelope, and the error mapping
    - Add `flask-smorest` and `marshmallow` to `backend/requirements.txt`.
    - Create `backend/app/api.py` with `EnvelopeApi(flask_smorest.Api)`: register every blueprint on it, declare the `bearerAuth` scheme once, and map errors to `{ status: false, message, error: { code, details? } }` (no `error.message`; the text appears once at the top level, defaulting to the HTTP reason phrase when an error has no custom text): `AppError` to its status and code, smorest/webargs 422 to 400 `VALIDATION_ERROR` with top-level message "Validation failed" and `error.details` mapping each field to the list of marshmallow messages (location keys such as `json` or `query` unwrapped), 404 `NOT_FOUND`, 405 `METHOD_NOT_ALLOWED`, any other exception to 500 `INTERNAL_ERROR` with a generic message, and the JWT missing, invalid, and expired callbacks to the 401 envelope. Set `Api.ERROR_SCHEMA` to the error envelope schema. Remove the old app-level error handler.
    - In `api.py`, set `API_TITLE`, `API_VERSION`, `OPENAPI_VERSION`, and, only when `APP_ENV` is `development` or `testing`, the `OPENAPI_*` keys for `/api/openapi.json` and `/api/docs`; add the `flask export-openapi` command that writes `backend/openapi.json` from `api.spec.to_dict()` under any `APP_ENV`.
    - Create `backend/app/common/envelope.py` with `envelope(DataSchema, many=False)` (cached `<Name>Envelope` / `<Name>ListEnvelope` schema with `status` as a `Boolean`, `message`, `data`), `NullEnvelopeSchema`, and `ErrorEnvelopeSchema` (`status`, `message`, `error` with `code` and optional `details`, and no `error.message`).
    - Change `ok(data, message=None, status=200)` in `app/common/responses.py` to return `{ "status": true, "message", "data" }` with "OK" as the default message; the integer argument only sets the HTTP status and is not placed in the body. Update error rendering in `app/common/errors.py` and `EnvelopeApi` to emit `status: false`, the top-level `message`, and `error: { code, details? }`.
    - Keep `AppError` classes free of Flask imports; keep all URLs, status codes, and role rules unchanged.
    - _Requirements: 13.2, 13.3, 13.4, 13.11, 13.12, 13.13, 13.15, 17.3, 17.4, 17.5, 17.6, 17.10_
  - [x] 24.2 Convert each blueprint to flask-smorest with marshmallow schemas
    - For each of `auth, boards (including members), columns, cards (including subtasks, attachments, and the board cards search/filter), categories, comments, notifications, analytics, users, activity (card and board activity reads)`: replace `flask.Blueprint` with `flask_smorest.Blueprint`; turn `schema.py` into marshmallow request, query, and payload schemas; validate with `@blp.arguments(Schema)` or `@blp.arguments(Schema, location="query")`; declare each success response with `@blp.response(status, envelope(PayloadSchema))` (`NullEnvelopeSchema` for logout); mark protected operations with `@blp.doc(security=[{"bearerAuth": []}])`; return `ok(dto, "<descriptive message>", status)` with the same status as the declaration. Each mutating route (POST, PATCH, PUT, DELETE) passes its own short descriptive message (for example "Card created", "Card moved", "Logged out"); read routes pass none and get "OK".
    - Keep data-dependent rules (uniqueness, access, ordering, ownership) in the service; `service.py` and `repository.py` import none of `flask`, `flask_smorest`, or `marshmallow`. Keep `filter[<field>]` parsing and the `400` for an unsupported filter key, and the signed file route returning raw bytes on success and the error envelope on failure.
    - Keep every URL, HTTP status code, and role rule unchanged.
    - _Requirements: 13.2, 13.3, 13.12, 13.13, 13.14, 13.15_
  - [x] 24.3 Update the existing tests and add envelope tests
    - Update the 36 existing pytest tests that assert `{ "data": ... }`, `{ "error": ... }`, a numeric `body["status"]`, or `body["error"]["message"]` to the V6 shapes `{ status: true, message, data }` and `{ status: false, message, error: { code, details? } }`; read the HTTP status from `response.status_code` and the text from `body["message"]`; change no expected HTTP status.
    - Add tests that: every success body has boolean `status` `true` (never the number 200) and a non-empty `message`, with mutating endpoints returning a descriptive message and reads returning "OK"; every error body has boolean `status` `false`, a single non-empty top-level `message`, an `error.code`, and no `error.message`; `error.details` is absent on every error except `VALIDATION_ERROR`; body and query validation failures return 400 `VALIDATION_ERROR`, never 422, with `error.details` mapping every failing field to a non-empty list of strings (for example a blank comment gives `error.details.content`); an unknown route returns the 404 envelope, a wrong method returns the 405 envelope, a forced unhandled exception returns the 500 envelope with a generic message, and a missing or invalid JWT returns the 401 envelope; the signed file route returns the error envelope on failure.
    - _Requirements: 13.2, 13.3, 13.4, 13.11, 13.13_
  - [x] 24.4 Checkpoint - Run the full pytest suite
    - Run the full backend `pytest` suite and ensure all tests pass, ask the user if questions arise.

- [x] 25. Add model relationships and eager loading
  - [x] 25.1 Add the five relationships to the models
    - Declare `Board.columns`, `Board.members`, `Card.subtasks`, `Card.attachments`, and `Comment.replies`, each with its inverse (`Column.board`, `BoardMember.board`, `Subtask.card`, `Attachment.card`, `Comment.parent` with `remote_side`) through `back_populates` (never `backref`), `lazy="raise"`, the `order_by` from the design's relationship table, and no `cascade`.
    - Declare no other relationships; `Card.assignee_id`, `Card.category_id`, `Comment.author_id`, `Board.owner_id`, and `Card.column_id` stay plain foreign-key columns.
    - Remove any `to_dict` or other serialization method still on a model; serialization stays in the marshmallow schemas.
    - Add no migration: this is a mapper-level change only.
    - _Requirements: 13.16, 13.17_
  - [x] 25.2 Load related rows in the repositories
    - Per the design's repository loading table: `board_repository.get_detail` uses `selectinload(Board.columns)`; `card_repository.list_for_board` and `get_detail` use `selectinload(Card.subtasks)` and `selectinload(Card.attachments)`; `comment_repository.list_for_card` uses `selectinload(Comment.replies)` and selects the author role in the same joined query.
    - Fix every service, schema, and route that now raises because it read an unloaded relationship; services and schemas must trigger no lazy load, and the board cards list must run a constant number of queries.
    - _Requirements: 13.18, 14.12_
  - [x]* 25.3 Write tests for relationships and constant query count
    - **Property 39: Constant query count for list endpoints**: count SQL statements with a `before_cursor_execute` listener for a board with 5 cards and a board with 50 cards (each with subtasks and attachments), and assert the counts are equal; repeat for the comment listing.
    - Add the `lazy="raise"` test: access an unloaded `Card.subtasks`, `Board.columns`, `Board.members`, `Card.attachments`, and `Comment.replies` and assert `sqlalchemy.exc.InvalidRequestError`, then assert the access succeeds when the repository loads it.
    - Add a static check: no model defines `to_dict`, and each of the five relationships has `lazy="raise"`, `back_populates`, and no `cascade`.
    - **Validates: Requirements 13.16, 13.17, 13.18, 14.12, 15.8, 15.9**
  - [x] 25.4 Checkpoint - Run the full pytest suite
    - Run the full backend `pytest` suite and ensure all tests pass, ask the user if questions arise.

- [x] 26. Migrate the frontend styling to Tailwind CSS and shadcn/ui (Decision H)
  - [x] 26.1 Install Tailwind CSS v4 and map the theme to the design tokens
    - Install `tailwindcss`, `@tailwindcss/postcss`, `class-variance-authority`, `clsx`, `tailwind-merge`, `@radix-ui/react-dialog`, `@radix-ui/react-slot`, `tw-animate-css`; add `postcss.config.mjs` and `lib/utils.ts` (`cn`).
    - Rewrite `styles/globals.css`: `@import "tailwindcss"`, an `@theme` block that clears the default palette and maps utilities to the tokens in `styles/tokens.css` (colors, `--space-*`, `--radius-*`, `--shadow-*`, `--breakpoint-lg: 60rem`), and shadcn variable aliases. Keep `tokens.css` as the single source; delete `shell.css`.
    - _Requirements: 14.5, 14.9, 14.13, 14.14_
  - [x] 26.2 Add the shadcn/ui primitives and rewrite the Base components as wrappers
    - Add `components/ui/button.tsx`, `badge.tsx`, `dialog.tsx` themed from the tokens; rewrite `BaseButton`, `BaseBadge`, `BaseModal` as thin wrappers with unchanged props. Nothing outside `components/shared/` imports `components/ui/`.
    - _Requirements: 14.10, 14.13, 14.15_
  - [x] 26.3 Restyle the app with Tailwind utilities, following the prototype
    - Replace the hand-written class names in the auth pages, app shell, sidebar, side panel, board, card tile, card modal, subtask checklist, attachment list, and comment thread. Keep the prototype's palette, layout, and interaction patterns; refine type scale, elevation, spacing rhythm, and motion (honoring `prefers-reduced-motion`).
    - Base styles target 360 to 414 px; `lg:` adds the desktop layout; no `max-*` layout variants, no arbitrary values, no hex colors.
    - _Requirements: 14.4, 14.5, 14.6, 14.7, 14.9, 14.13_
  - [x] 26.4 Update tests and add the static styling check
    - Update component tests to assert roles, names, and attributes instead of class names; add a test that scans `components/**` and `app/**` for hex colors, arbitrary-value utilities, and imports of `components/ui/` outside `components/shared/`.
    - _Requirements: 14.9, 14.10_
  - [x] 26.5 Checkpoint - Run typecheck, tests, and `next build`
    - Ensure `tsc --noEmit`, `vitest run`, and `next build` pass, ask the user if questions arise.
  - [x] 26.6 Prototype fidelity pass and removal of magic numbers
    - Restyle the shell, header, columns, cards, side panel, and card modal to match `design/kanban-prototype.html` (frosted surfaces, accent bars, card layout, four-row board header, avatar stack); add `BaseAvatar` and `BaseChip` to `components/shared/`; move every size, layer, duration, and opacity into named tokens.
    - Add a static test that rejects `z-`, `duration-`, `opacity-`, `ring-`, `outline-`, and `border-` utilities with numeric suffixes and colour opacity modifiers.
    - _Requirements: 14.9, 14.13_
  - [x] 26.7 Look refresh to the product owner's reference
    - Retheme `styles/tokens.css` (white surfaces, navy brand, pastel tags, `--tone-*` hues); rebuild the sidebar as an icon rail plus boards panel; flatten the columns; restyle `CardTile`, `BoardHeader`, `BaseChip`, and `BaseBadge`; remove `BackgroundScene` and the `--glass-*`, glow, and column blur tokens.
    - Keep the static styling test green (no hex, no arbitrary values, no magic numbers).
    - _Requirements: 14.9, 14.13_

- [x] 27. Trello-style board and card modal (Decision I)
  - [x] 27.1 Install the new dependencies, set the font, and add the tokens
    - Install `@fontsource-variable/inter`, `@radix-ui/react-popover`, and `react-day-picker`; import the Inter font once in `app/layout.tsx` and put it first in `--font-stack`.
    - Add the tokens the new layout needs (modal margin, popover widths, calendar cell size, tooltip offset) and expose them in `globals.css`; keep the static styling test green.
    - _Requirements: 14.9, 14.17_
  - [x] 27.2 Add `BasePopover`, `BaseCalendar`, and the `BaseModal` footer slot
    - Add `components/ui/{popover,calendar}.tsx` and the thin wrappers `BasePopover` and `BaseCalendar`; give `BaseModal` a `footer` prop (bordered bar under a scrolling body) and a `full` size that fills the viewport minus a margin; use the footer in `NewBoardModal` (Cancel, Create).
    - Add shared-component tests (popover opens and closes with Escape; the footer renders its buttons).
    - _Requirements: 14.10, 4.35_
  - [x] 27.3 Rebuild the Sidebar and add the Home page
    - Remove the logo tile; make Home the first entry and the post-sign-in destination; add `hooks/useSidebarState.ts` and the collapse toggle (expanded with labels, collapsed with tooltips, kept in `localStorage`); show the lock or open lock on each board row with an accessible label; wrap long names with a title tooltip.
    - Replace the `/boards` redirect with a page that lists every visible board.
    - _Requirements: 3.20, 3.21, 3.22, 14.7, 14.16_
  - [x] 27.4 Rework the main panel and the card face
    - Lock the shell to the viewport; fixed `BoardHeader` with the visibility icon and a wrapping title; columns scroll sideways, each column scrolls inside itself, "Add a card" pinned at the column bottom; slimmer `CardTile` (label chips, a badge row, assignee avatar).
    - _Requirements: 3.20, 3.21, 14.18_
  - [x] 27.5 Keep HTML5 drag-and-drop in the scrolling columns
    - A pointer-event rewrite (`lib/drag.ts`, `hooks/useCardDrag.ts`) was built and then reverted at the product owner's request; `Board` and `CardTile` use the HTML5 API (draggable cards, `dragover` and `drop` on each column body, placeholder, FLIP, one `onMove` call on drop). `lib/ordering.ts` is unchanged.
    - _Requirements: 5.2, 5.13_
  - [x] 27.6 Add the date rules and `DateRangePicker`
    - Add `lib/dates.ts` (`normalizeRange`, `isRangeValid`) and `components/card/DateRangePicker.tsx`: one range calendar, optional Start date and End date fields with checkboxes, the range highlighted as a block, days before the start disabled while picking the end, an inline error for a typed invalid pair.
    - _Requirements: 4.31, 4.32_
  - [x]* 27.6.1 Write property tests for the date rules
    - Property: for any sequence of picks, `normalizeRange` returns a pair where the end is empty or not before the start; a start moved past the end clears the end; equal dates are valid.
    - _Requirements: 4.32_
  - [x] 27.7 Add `MemberPicker`
    - A popover with a search box (case-insensitive over name and login identifier), the board's members with avatars, single choice, and Remove; hidden for a Member.
    - Test search filtering, choosing, and removing by role and name.
    - _Requirements: 4.33_
  - [x] 27.8 Rebuild `CardModal`
    - Large modal; left pane: three cards, Details (title, `CardChips`, description with an Edit toggle), Attachments, and Subtasks; right pane: one card with the composer, the thread, and the Activity list below; a footer with Delete (second click confirms), Archive, Close, Save changes (disabled while the dates are invalid).
    - Delete the column select and `moveTo` from the modal.
    - `CardChips`: category pill, Priority flag chip, date-range chip with a red Overdue state, assignee avatar with an add button, each in a `BasePopover` that edits the draft.
    - _Requirements: 4.20, 4.21, 4.30, 4.31, 4.32, 4.33, 4.34, 4.35_
  - [x] 27.9 Checkpoint - Run typecheck, tests, and `next build`
    - Ensure `tsc --noEmit`, `vitest run`, and `next build` pass, then check the board, the modal, the dates popover, and the member popover in a browser at 1563px and 390px; ask the user if questions arise.

- [x] 28. Owner feedback on the Trello-style UI (Decision I)
  - [x] 28.1 Return author and actor names from the API
    - `activity_repository.serialize_many` and `comments_repository.author_names` load `User.full_name` in one query each, whatever the row count; add `actor_name` to `ActivitySchema` and every activity response, and `author_name` to `ReplySchema` and every comment response (list, create, reply, priority); no new relationship on a model.
    - Add a test that a manager who is not a board member shows by name (`test_comment_and_activity_names`), and update `backend/API.md` and `backend/openapi.json`.
    - _Requirements: 7.21, 8.8_
  - [x] 28.2 Frontend: names, brand, radii, and the logo toggle
    - Read `actor_name` and `author_name` before the member map; rename the app to RevoTask (Sidebar, page titles, sign-in layout); make the logo mark the Sidebar toggle (name beside it when expanded, tooltip when collapsed); set the radius tokens to 4 (small), 6 (medium and card), and 8 (large) pixels and flatten the column and card rounding.
    - _Requirements: 7.21, 8.8, 14.16, 14.19_
  - [x] 28.3 Frontend: modal scrolling, attachments, and subtasks
    - Add `lg:grid-rows-1` so each pane scrolls; split the Attachments and Subtasks cards; show the Attachments card in two columns with a Link or File selector; add a test for the selector and for the two cards.
    - _Requirements: 4.36, 4.37, 4.38_
  - [ ] 28.4 Checkpoint - Run backend and frontend tests and `next build`
    - Ensure `pytest`, `tsc --noEmit`, `vitest run`, and `next build` pass, then check the modal scroll, the logo toggle, drag-and-drop, and the names in a browser; ask the user if questions arise.

- [ ] 29. Modal balance, activity clarity, and board card sizes (Decision I)
  - [x] 29.1 Record names and changes in the Activity_Log metadata
    - In `cards/service.py` and `comments/service.py` pass the extra `metadata` keys of Req 8.9 to `activity.add`: `card_title` on every card event, `changes` (`{field: {from, to}}`) on `card.updated`, `from_column_name` and `to_column_name` on `card.moved`, `assignee_name` on `card.assigned`, subtask `title`, and attachment `name`.
    - Add tests that each action writes its keys (move, update with a priority and a date change, assign, subtask add, attachment add); update `backend/API.md` and regenerate `backend/openapi.json`.
    - _Requirements: 8.9_
  - [x] 29.2 Add the control, type, and spacing scale
    - Add the tokens of the design bullet "Control and type scale" and expose them in `globals.css`; apply `min-h-control` to `Input`, `NativeSelect`, `Button` default, `BaseChip`, and `CardChips`; set the card modal spacing; keep the static styling test green.
    - _Requirements: 14.20, 4.40_
  - [x] 29.3 Rework the card modal header, footer, attachments, and cards
    - Header "card title | board name" that follows the draft title, column badge beside it; footer Archive, Delete, Save changes (right-aligned, no Close); Attachments as bordered tiles with type icons and a small remove icon; Activity in its own card under Comments.
    - Update the modal tests (header text follows the title field, no Close button in the footer, an Activity region, attachment icons).
    - _Requirements: 4.20, 4.35, 4.36, 4.39_
  - [x] 29.4 Rewrite the activity wording
    - `describeActivity` returns parts; `ActivityList` and the side panel render the actor, action, object, and from-to with badges; generic fallback for old rows. Unit tests for move, change, assign, subtask, attachment, and a legacy row.
    - _Requirements: 8.10_
  - [x] 29.5 Fix the tooltip and size the board cards
    - Tooltip on hover and keyboard focus only; fluid column width; card padding and text tokens; two-line description; wide-screen step.
    - _Requirements: 14.21, 14.22_
  - [ ] 29.6 Checkpoint - Run backend and frontend tests and `next build`
    - Ensure `pytest`, `tsc --noEmit`, `vitest run`, and `next build` pass, then check the modal, the activity log, the tooltip, and the board cards in a browser; ask the user if questions arise.

- [ ] 30. Visual system, searchable selects, and paging (Decisions I and J)
  - [x] 30.1 Backend: paging and member candidates
    - `limit` and `before` on `GET /api/notifications`, `GET /api/boards/{id}/activity`, and `GET /api/cards/{id}/activity` (default 20, cap 100, 400 for a bad `limit` or a `before` outside the feed); `GET /api/boards/{id}/candidates?search=` (owner, Manager, Admin; at most 20 non-members; `id` and `full_name` only).
    - Tests for page sizes, the cursor, the last page, the 400 cases, the candidates filter, and the 403/401 cases; update `backend/API.md` (replace "There is no pagination") and regenerate `backend/openapi.json`.
    - _Requirements: 3.25, 8.11, 9.11, 13.19_
  - [x] 30.2 Shared components and tokens
    - Add `@radix-ui/react-tooltip` and `cmdk`; add `components/ui/{tooltip,command}.tsx`, `BaseTooltip`, `BaseCombobox`, and `BaseConfirm`; add the type and spacing tokens of the design section "Round 4"; tests for the combobox (search shown from six options, keyboard choice) and the confirmation popover.
    - _Requirements: 14.10, 14.20, 14.23, 14.24, 14.25_
  - [x] 30.3 Sidebar hierarchy and the Team members section
    - One `NavItem` for every entry; the type hierarchy; remove the Members nav entry; Team members add button with `MemberSearch` (popover, modal below 960px) and a remove button with confirmation; tooltips through `BaseTooltip`.
    - _Requirements: 3.24, 14.26_
  - [x] 30.4 Board header and board cards
    - One-row header without Add Member and the settings gear; search modal below 960px; bordered filter chips; avatar tooltip on the board Card.
    - _Requirements: 3.23, 6.13, 14.24_
  - [x] 30.5 Card modal
    - Attribute rows with icons and comboboxes; header with the title and close icon only; staged attachment additions and removals applied on Save with uploads at that moment and a "Discard changes?" prompt; confirmation popovers for Subtask, Attachment, and Card deletes; equal tile and button heights; button roles.
    - Update the modal tests (attribute rows, staged removal not sent before Save, discard prompt, confirmation before delete).
    - _Requirements: 4.21, 4.35, 4.41, 4.42, 4.43, 4.44, 4.45, 14.25_
  - [x] 30.6 Comment thread layout
    - Avatar, name and time, text, small text actions; replies indented with a vertical line; no box per comment.
    - _Requirements: 7.22_
  - [x] 30.7 Load more for the Inbox and the activity lists
    - First page sized to the visible area; Load more with `before`; hide on the last page; tests with a mocked API.
    - _Requirements: 8.12, 9.12_
  - [x] 30.8 Categories screen
    - `app/(app)/boards/[id]/categories/page.tsx` with `CategoriesScreen` (add, rename, recolor, delete) for Supervisor, Manager, Admin, scoped to the current board, using the round 4 components.
    - _Requirements: 6.11_
  - [ ] 30.9 Checkpoint - Run backend and frontend tests and `next build`
    - Ensure `pytest`, `tsc --noEmit`, `vitest run`, and `next build` pass, then check the sidebar, header, modal, comments, selects, and Load more in a browser at desktop and phone width; ask the user if questions arise.

- [ ] 31. Header, Home, and badges (Decision I)
  - [x] 31.1 Backend: board counts and description
    - `Board.description` (nullable `Text`, max 500 through the schemas) with an Alembic migration; accept it on `POST /boards` and `PATCH /boards/{id}`; return it on every board response.
    - `GET /boards` adds `card_count`, `done_count`, `overdue_count`, `member_count` with aggregate queries (one per count kind, independent of the number of boards).
    - Tests: counts with soft-deleted, archived, Done, and overdue cards; the description round trip and the 400 for 501 characters; the constant query count for the board list. Update `backend/API.md` and regenerate `backend/openapi.json`.
    - _Requirements: 3.26, 3.27_
  - [x] 31.2 Two-row board header
    - Row 1 title and lock, bell and user; row 2 bordered progress, `ChipStrip` with arrow buttons shown only on overflow, and search (modal below 960px).
    - Tests: the arrows appear only when the strip overflows (mock the sizes) and scroll it.
    - _Requirements: 3.23_
  - [x] 31.3 Card modal fixes and badges
    - Title as text with Edit; date rows on one grid; `FileDropZone` (drag and click) staging the file; close icon inside the header row; `BaseBadge` `outline` shape for Priority with a flag; lowercase Category names everywhere.
    - Tests: title Edit toggle; a dropped file is staged and not sent before Save; the two badge types render with different shapes.
    - _Requirements: 4.46, 4.47, 4.48, 4.49, 4.50, 6.14_
  - [x] 31.4 Home page tiles and the analytics strip
    - `BoardTile` (plain bordered tile, no cover band) with description, progress, counts, and avatars; the optional Description field in `NewBoardModal`; the analytics strip for Supervisor (owned boards) and Manager, absent for Member and Admin.
    - Tests: tile content from a board with counts; the strip renders for a Manager and not for an Admin or a Member.
    - _Requirements: 3.28, 3.29, 10.8_
  - [ ] 31.5 Checkpoint - Run backend and frontend tests and `next build`
    - Ensure `pytest`, `tsc --noEmit`, `vitest run`, and `next build` pass, run the migration on the dev database, then check the header, Home, and the card modal in a browser at desktop and phone width; ask the user if questions arise.

- [ ] 32. Auth end-to-end tests: sign-in and sign-out (V9)
  - [ ] 32.1 Set up Playwright for the deployed URL
    - Add `@playwright/test` as a dev dependency (skip if task 20.1 already did), `frontend/playwright.config.ts` (`testDir: "tests/e2e"`, `baseURL` from `E2E_BASE_URL`, no `webServer`), and a `test:e2e` script.
    - Add `E2E_BASE_URL=`, `E2E_USER_IDENTIFIER=`, and `E2E_USER_PASSWORD=` to `frontend/.env.example`; confirm no real `.env` is tracked.
    - _Requirements: 15.10, 15.11, 15.13_
  - [ ] 32.2 Write the Auth_Page_Object and the environment helper (V9 form; V10 revises it in 33.22)
    - `frontend/tests/e2e/auth/pages/AuthPage.ts` (locators and actions; `signOut()` opens the drawer below 960 pixels) and `frontend/tests/e2e/auth/env.ts` (throws an error naming the missing variable).
    - _Requirements: 15.10, 15.11, 15.12, 15.15_
  - [ ] 32.3 Write `signin.spec.ts` (V9 form; V10 revises it in 33.23)
    - One test per ID: SI-01 to SI-05 (happy) and SI-06 to SI-10 (negative), titles starting with the ID; the 256-character identifier and the password-hygiene checks included.
    - _Requirements: 1.19, 1.20, 1.21, 1.22, 1.23, 1.24, 1.25, 1.26, 1.27, 1.28, 1.37, 15.14_
  - [ ] 32.4 Write `signout.spec.ts` (V9 form; V10 revises it in 33.24)
    - One test per ID: SO-01, SO-02, SO-04 (happy), SO-06, SO-07, SO-08 (negative, with `page.route`), and SO-03, SO-05 as `test.fixme` until Open Question 5 is decided.
    - _Requirements: 1.29, 1.30, 1.31, 1.32, 1.33, 1.34, 1.35, 1.36, 1.37, 1.38, 15.14_
  - [ ]* 32.5 Write static checks for the suite
    - A CI step that fails when `waitForTimeout` appears under `frontend/tests/e2e/`, when a credential-like literal appears in `tests/e2e/auth/`, or when a criterion ID in Req 1.19 to 1.36 has no test title (extends 20.2).
    - _Requirements: 1.37, 15.3, 15.11, 15.14_
  - [ ] 32.6 Checkpoint - Run the suite against the deployed URL
    - Run `npm run test:e2e` with the three variables set; confirm all non-fixme tests pass and report the two `fixme` tests.
- [ ] 33. Share links, username and email, header menu, rate limiting, route guard (Decisions K to P, V10)
  - [x] 33.1 Update the models and write the V10 migration
    - Models: `User` gets `username` (String(30), lower-case) and `email` (String(255), lower-case, nullable in the database) and loses `login_identifier`; `Board` gets nullable `share_token` (String(64)); new `RateLimitAttempt` (`scope` in `login_pair`, `login_ip`, `availability`, with no `register` value; `key_hash`; `created_at`; index `(scope, key_hash, created_at)`). The avatar column change is part 4 of the same revision, written in 33.28.
    - One Alembic revision `b7d2e4f6a801` in three parts: users (add columns, Python backfill in `created_at, id` order with the two passes and `derive_username` of the design, unique indexes on `lower(username)` and `lower(email)`, `username` NOT NULL, drop the old index and `login_identifier`), boards (`share_token` plus partial unique index), and the table. Print one line per derived or sanitized Username. Write `downgrade()` as in the design.
    - Run it on a copy of the dev database first and keep a dump.
    - _Requirements: 1.43, 1.52, 18.1, 20.9, 20.12_
  - [ ]* 33.2 Write the migration and constraint tests
    - **Property 45: Migration backfill**
    - Generated legacy rows (email-shaped, username-shaped, other, in any order, with collisions); assert valid and unique Usernames, `email` rules, idempotence, and that downgrade restores a `login_identifier`; integration tests for the two functional unique indexes (case-insensitive, two null Emails allowed) and the unique `share_token`.
    - **Validates: Requirements 1.43, 1.52, 15.18**
  - [x] 33.3 Implement the identity changes in the auth and users blueprints
    - `common/validation.py`: `normalize_username`, `normalize_email`, `is_email_shape`, `classify_identifier`, `USERNAME_RE`.
    - `auth`: register with `username` and `email` (field-level 400, 409 with `details` per field, `IntegrityError` mapped to the same 409), login with `identifier` (classification, one generic 401, dummy hash for unknown users), `GET /auth/availability`, the `{ id, full_name, username, email, avatar_url }` user shape; `users` create and edit accept the two fields; `GET /boards/{id}/candidates` matches `full_name`, `username` prefix, `email` exact (the response carries `email` from round 2, built in 33.35); update `app/seed.py`.
    - Update the existing backend tests that used `login_identifier`.
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.44, 1.45, 1.46, 1.47, 1.48, 1.49, 1.54, 3.25_
  - [ ]* 33.4 Write the identity property tests
    - **Property 1: Registration and login round trip** (revised), **Property 2: Registration validation and unique username and email** (revised), **Property 42: Login identifier classification**, **Property 43: Username and Email normalisation and uniqueness**
    - **Validates: Requirements 1.1 to 1.5, 1.43 to 1.49**
  - [x] 33.5 Implement the Rate_Limiter and wire it into login and availability (not register, Decision Q)
    - `common/rate_limiter.py` (pure `blocked_until`, store with advisory lock and separate-commit failure record, `check_login`, `record_login_failure`, `reset_pair`, `hit` for availability only), `RateLimited` (429, `RATE_LIMITED`, `details.retry_after`), `Retry-After` header in `EnvelopeApi`, CORS `expose_headers`, `ProxyFix` from `TRUSTED_PROXY_COUNT`, the five settings in config (`RATE_LIMIT_WINDOW_SECONDS`, `RATE_LIMIT_LOGIN_PAIR_MAX`, `RATE_LIMIT_LOGIN_IP_MAX`, `RATE_LIMIT_AVAILABILITY_MAX`, `TRUSTED_PROXY_COUNT`; no `RATE_LIMIT_REGISTER_MAX`), `create_app(config_overrides)`, and `backend/.env.example` placeholders. `auth_service.register` makes no limiter call (Req 20.18).
    - Routes pass `client_ip` to the service; services stay free of Flask imports.
    - _Requirements: 20.1 to 20.14, 20.17, 13.3, 13.11_
  - [ ]* 33.6 Write the Rate_Limiter tests
    - **Property 44: Rate limit window** (fake clock, small thresholds through `create_app`, PostgreSQL, two app instances on one table); example tests for the 429 body and header, a blocked correct password, success reset, independent pairs, and that register is never answered with 429 (Req 20.18).
    - **Validates: Requirements 20.1 to 20.14, 15.16**
  - [x] 33.7 Implement the profile endpoints
    - `GET /auth/me`, `PATCH /auth/me` (`unknown=RAISE`, so `avatar_url` returns 400; email only while null, 409 `details.email`), `POST /auth/change-password` (400 `details.current_password`), one Activity_Log row per success with no secret in `metadata`.
    - _Requirements: 19.8 to 19.16_
  - [ ]* 33.8 Write the profile property test
    - **Property 46: Profile update rules**
    - **Validates: Requirements 19.9 to 19.16**
  - [x] 33.9 Remove Guest access to Boards
    - `can_access(None, board)` returns false; `GET /boards` without a Token returns 401; remove the Guest branches in board, card, column, category, comment, activity, search, and attachment services and serializers (a Guest gets 401 everywhere outside `/api/shared`; the comment endpoints return 401 instead of 403 on a public Board); update `list_visible`.
    - Update the existing tests that expected Guest access (tasks 4, 5, 7, 8, 9, 12, 14.1 fixtures).
    - _Requirements: 7.16, 8.5, 11.4, 11.5, 11.7, 11.12, 11.13, 12.6, 12.7, 13.10, 14.3_
  - [x] 33.10 Implement the share endpoints
    - `board_service.get_share`, `enable_share`, `regenerate_share`, `disable_share`; routes `GET`, `POST`, `POST .../regenerate`, `DELETE` under `/boards/{id}/share`; owner, Manager, Admin only; one activity row per change, no token in `metadata`.
    - _Requirements: 18.1 to 18.8_
  - [x] 33.11 Implement the `shared` blueprint and token-scoped file URLs
    - `blueprints/shared/` with `routes.py`, `service.py`, `repository.py`, `schema.py` (board, cards, categories, card detail, attachment URL; GET only; shared schemas without comments, activity, owner, members, token; `has_board_access` from an optional Bearer; `Cache-Control: private, no-store`); extend `common/signing.py` with the `scope` and `st` parameter and the file route check against the Board's current token.
    - _Requirements: 18.9 to 18.19, 12.6, 6.6, 4.26_
  - [ ]* 33.12 Write the share and guest tests
    - **Property 40: Share_Token lifecycle**, **Property 41: Shared routes stay inside the token's board**, **Property 28: Guest responses never include comments or activity** (revised), **Property 34: Board list visibility** (revised), **Property 4** and **Property 5** (revised); a static test that `/api/shared` has no non-GET route and no comment or activity route.
    - **Validates: Requirements 18.1 to 18.17, 7.16, 8.5, 11.4 to 11.7, 11.13, 15.17**
  - [x] 33.13 Update the generated OpenAPI document and `backend/API.md`
    - Document the new and changed endpoints, the 429 response, the `identifier` field, and the user shape; run `flask export-openapi`; keep the "every route is documented" test (Property 37) green.
    - _Requirements: 17.1, 17.2, 17.3_
  - [ ] 33.14 Update the Frontend API client and helpers
    - `lib/api.ts`: `ApiError.retryAfter`, no redirect on a 401 from `POST /auth/login`, `api.auth` (`login` with `identifier`, `register`, `availability`, `me`, `updateMe`, `changePassword`, `logout` that always clears the cookie and navigates), `api.shared`; `lib/validation.ts` (`classifyIdentifier`, `isUsername`, `isEmail`); `hooks/useCountdown.ts`; update the `User` type.
    - _Requirements: 1.50, 1.51, 19.4, 20.15_
  - [ ]* 33.15 Write the helper tests
    - fast-check parity of `classifyIdentifier` with the Backend cases (Property 42); `useCountdown` ticks to zero with fake timers.
    - **Validates: Requirements 1.51, 20.15**
  - [ ] 33.16 Rebuild the login and register forms
    - Login: one "Username or email" field, email-or-username validation by `@`, Generic_Login_Error, countdown and disabled submit on 429. Register: full name, Username, Email, password; availability on blur (silent when blocked); field errors from `error.details`; no 429 handling for register (Decision Q), and a 429 on the availability check silently stops the on-blur checks.
    - _Requirements: 1.50, 1.51, 20.15, 20.16, 1.9, 1.10_
  - [ ] 33.17 Build `BaseMenu`, the App_Header, and the User_Menu
    - Add `@radix-ui/react-dropdown-menu`, `components/ui/dropdown-menu.tsx`, and `components/shared/BaseMenu.tsx`; `AppHeader` and `UserMenu` in `(app)/layout.tsx`; move the Board header's first row into the App_Header slot; remove the profile entry and Log out item from the Sidebar; keep the Inbox bell and the Sidebar toggle.
    - _Requirements: 19.1 to 19.7, 14.10, 3.23_
  - [ ] 33.18 Build the Profile_Page and the Email_Prompt
    - `(app)/profile/page.tsx` with the full name field, the avatar section (`AvatarUploader`, built in 33.31), the read-only fields, and the change-password form; `EmailPrompt` mounted by the layout while `user.email` is null.
    - _Requirements: 19.8 to 19.17, 1.53_
  - [ ] 33.19 Add the route guard
    - `frontend/proxy.ts` with the matcher for `/boards`, `/profile`, `/admin`; leave `/login`, `/register`, `/shared` open; a unit test per path. Round 2 extends this file in 33.33 (unusable cookie, cookie removal, `x-return-path`).
    - _Requirements: 14.27_
  - [ ] 33.20 Build the Share button and the Shared_View
    - `ShareButton` popover (enable, link and Copy, Regenerate and Disable behind `BaseConfirm`); `app/shared/[token]/page.tsx` with `SharedBoard` and `SharedCardModal` (read-only, banner, Sign in link, invalid-link page); redirect when `has_board_access`; `no-referrer` and `noindex` headers in `next.config.ts`; remove any Guest-facing board browsing from `/boards`.
    - _Requirements: 18.19 to 18.23, 3.23_
  - [ ]* 33.21 Write the component tests
    - The V10 component tests listed in the design's Frontend tests section.
    - **Validates: Requirements 14.27, 18.21, 18.22, 19.2, 19.5, 19.13**
  - [ ] 33.22 Update the Auth_Page_Object and the environment helper for V10
    - New locators (`Username or email`, `User menu`, Profile and Log out menu items, Sidebar), `openUserMenu()`, `signOut()` through the menu with no drawer step, `waitTimeText`; `env.ts` unchanged apart from comments.
    - _Requirements: 15.10, 15.11, 15.12, 15.15_
  - [ ] 33.23 Update `signin.spec.ts` for V10
    - Signed-in indicator is the User_Menu_Trigger; SI-07 uses a Throwaway_Identifier; SI-08, SI-09 assert no request is sent; add SI-11 (rate limit, up to 10 attempts, Throwaway_Identifier, never the Test_Account) and SI-12 (email shape).
    - _Requirements: 1.19 to 1.28, 1.39, 1.40, 1.37, 15.14, 15.19_
  - [ ] 33.24 Update `signout.spec.ts` for V10
    - Sign-out through the menu; SO-03 and SO-05 become real tests (no `test.fixme`); SO-04 ends on `/login`; add SO-09 (menu order) and SO-10 (no Sidebar Log out or Profile).
    - _Requirements: 1.29 to 1.36, 1.41, 1.42, 1.37, 1.38, 15.14_
  - [ ]* 33.25 Update the static checks for the suite
    - The CI step covers IDs in criteria 19 to 36, 39 to 42, 55, and 56, no `waitForTimeout`, no credential-like literal, and no `test.fixme` left in `tests/e2e/auth/`.
    - _Requirements: 1.37, 15.3, 15.11, 15.14_
  - [x] 33.26 Sync steering and guidelines to V10
    - Updated in this revision: `product.md`, `data-model.md`, `api-conventions.md`, `backend.md`, `frontend.md`, `structure.md`, `tech.md`, and `guidelines/` where they contradicted V10 (see CHANGELOG V10, "Steering and guidelines").
    - _Requirements: 14.10, 13.3, 11.4_
  - [ ] 33.27 Checkpoint - Run backend and frontend tests, the build, and the suite
    - Ensure `pytest`, `tsc --noEmit`, `vitest run`, and `next build` pass, run the migration on a copy of the dev database, run `npm run test:e2e` against the deployed URL with the three variables set, and check the risk recorded for SI-11: set `RATE_LIMIT_LOGIN_IP_MAX` above 20 on the test environment or run the suite once per window. Ask the user if questions arise.
- [ ] 33.28 Extract the file store, add `detect_image_type`, and write migration part 4 (avatar) (Decision R)
  - `common/file_store.py` (`FileStore(upload_dir)`: `save`, `delete`, `path`, bare-name check) extracted from the inline code in `cards/service.py` (write, `os.remove`, file route path); attachments call it with `subdir=""`, behaviour unchanged. `common/images.py` with `MAX_AVATAR_BYTES` and `detect_image_type`. `common/signing.py` takes `scope` and a route name (shared with 33.11) so the avatar scope reuses the one signing and verification code. `User.avatar_path` (String(64), nullable) replaces `avatar_url`; add part 4 to revision `b7d2e4f6a801` (add column, print and drop the old non-null `avatar_url` values, drop the column; `downgrade()` re-adds `avatar_url` empty). Create `UPLOAD_DIR/avatars/` on first write.
  - Risks to record in the PR: Werkzeug buffers the multipart body (cap the body at the reverse proxy, about 3 MB); the file keeps EXIF data and no image library re-encodes it.
  - _Requirements: 19.21, 19.24, 13.14, 1.6_
- [x] 33.29 Implement the avatar endpoints (Decision R)
  - `auth_service.set_avatar`, `clear_avatar`, `open_avatar`; routes `POST` and `DELETE /auth/me/avatar` and `GET /auth/avatars/{user_id}/file`; `user_repository.get_for_update`; write-commit-delete order with cleanup on failure; `UserSchema.avatar_url` as a signed-URL method that is null without a file; one `user.profile_updated` row with `{ "fields": ["avatar"] }`; remove `avatar_url` from the `PATCH /auth/me` and admin `POST|PATCH /users` schemas (400); response headers `nosniff`, `inline`, `Cache-Control: private, max-age=300`; update the OpenAPI document and `backend/API.md`.
  - _Requirements: 19.18, 19.19, 19.20, 19.21, 19.22, 19.23, 19.24, 19.25, 19.26, 19.27, 19.32, 19.33, 13.10_
- [ ]* 33.30 Write the avatar tests
  - **Property 47: Avatar image type and size**
  - API tests of Req 15.20 (happy: PNG, JPEG, WebP, renamed extension, replace, delete, idempotent delete; negative: no Token, text renamed `.png`, SVG, GIF, empty, 2,097,153 bytes, missing part, traversal name, bad or expired or cross-user signature, no avatar 404, `avatar_url` in PATCH, no `avatar_url` in shared payloads); a test that two parallel uploads leave one file.
  - **Validates: Requirements 19.19, 19.20, 19.21, 19.22, 19.25, 19.26, 19.27, 19.33, 15.20**
- [ ] 33.31 Build the avatar section of the Profile_Page
  - `AvatarUploader` (choose, preview with a revoked object URL, Upload, Cancel, Remove behind `BaseConfirm`, client-side type and size messages, `details.file` and network messages), `api.auth.uploadAvatar` (existing `form` option) and `removeAvatar`, `BaseAvatar` initials fallback with one refresh through `api.auth.me()`, header and stored-user update without reload.
  - _Requirements: 19.28, 19.29, 19.30, 19.31_
- [ ]* 33.32 Write the avatar component tests
  - The tests of Req 15.21 (preview, Upload, Remove with confirmation, wrong type, too large, server `details.file`, initials fallback after one refresh). Add the manual smoke check (upload, preview, replace, remove) to the release checklist; the auth e2e suite has no avatar test (Req 15.22).
  - **Validates: Requirements 15.21, 15.22, 19.28, 19.29, 19.30**
- [ ] 33.33 Implement the invalid-Token redirect (Decision T)
  - `lib/session-token.ts` (`isUsableToken`), `lib/return-path.ts` (`safeReturnPath`), `frontend/proxy.ts` (redirect with `next`, cookie removal, `x-return-path` request header), `serverGet` redirecting to `/session-expired`, `app/session-expired/route.ts` (delete the cookie, redirect only to `/login`), `LoginForm` reading `next`. Backend: the shared routes use optional JWT verification that treats any JWT error as a Guest (never 401).
  - _Requirements: 1.57, 1.58, 1.59, 1.60, 1.61, 14.28, 18.24_
- [ ]* 33.34 Write the invalid-Token tests
  - **Property 48: Safe return path and usable Token** (fast-check); vitest for `proxy.ts` (no cookie, malformed, expired, valid, public paths, cookie removed on redirect); pytest that a malformed or expired Bearer Token on each shared route returns the Guest response.
  - **Validates: Requirements 1.57, 1.59, 1.60, 15.23, 18.24**
- [x] 33.35 Return the Email to staff in candidates and in the members list (Decision S)
  - `CandidateSchema` gains `email`; `GET /boards/{id}/members` accepts `include=email` (403 without Board_Staff_Access, 401 without a Token) and the default path never reads `User.email`; confirm no Comment, activity, Notification, shared, or default member schema declares `email`; update the OpenAPI document.
  - _Requirements: 3.25, 3.30, 3.31_
- [ ] 33.36 Show the Email in `MemberSearch` and `MemberPicker`
  - `MemberSearch` rows show full name with the Username and Email beneath; `MemberPicker` loads `?include=email`, shows full name and Email, and searches all three fields; the Sidebar member rows and every other component keep showing no Email; the picker stays hidden from a Member.
  - _Requirements: 3.31, 3.32, 4.33_
- [ ]* 33.37 Write the Email exposure tests
  - **Property 49: Email exposure**
  - The tests of Req 15.24, and component tests that `MemberSearch` and `MemberPicker` render the Email and the Sidebar and `CommentThread` render none.
  - **Validates: Requirements 3.25, 3.30, 3.31, 3.32, 15.24**
- [ ] 33.38 Add SO-11 and SO-12 to `signout.spec.ts`
  - `AuthPage.setSessionCookie(value)` and `buildForgedToken()` (header, payload with `exp` one hour ahead, the text `invalid` as signature; no secret); SO-11 uses the value `bogus`; both assert the URL path `/login`, the login form, and no `kanban_token` cookie, and neither touches the Test_Account.
  - _Requirements: 1.55, 1.56, 1.62, 15.14_
- [x] 33.39 Sync steering and guidelines to round 2
  - Updated in this revision: `product.md`, `data-model.md`, `api-conventions.md`, `backend.md`, `frontend.md`, `tech.md`, `guidelines/backend.md`, `guidelines/database.md`, and `guidelines/frontend.md` (see CHANGELOG V10, "Round 2 within V10").
  - _Requirements: 20.18, 19.24, 3.31, 1.57_
- [ ] 33.40 Checkpoint - Run the round 2 checks
  - Ensure `pytest`, `tsc --noEmit`, `vitest run`, and `next build` pass with 33.28 to 33.38 in place; run migration part 4 on a copy of the dev database; run the suite against the deployed URL, including SO-11 and SO-12; do the manual avatar smoke check. Ask the user if questions arise.
## Notes
- Round 2 within V10 (33.28 to 33.40, Decisions Q to T) amends unimplemented V10 work and is not a new version; 33.5, 33.16, 33.18, and 33.19 were edited in place for it. 33.35 builds on 33.3, 33.28 on 33.1 and 33.11, and 33.33 on 33.11 and 33.19.
- Group 33 (V10) must deploy the Backend and the Frontend together: the login request field, the `user` shape, and Guest access change on both sides. 33.9 (Guest access) and 33.10 to 33.11 (share links) land before the Frontend tasks 33.14 to 33.20, and the e2e update 33.22 to 33.25 runs last. If group 33 reaches the Frontend before group 32 is executed, write 32.2 to 32.4 directly in their V10 form (33.22 to 33.24) and skip the V9 variants.
- The ticked tasks of groups 1 to 19 that mention `login_identifier`, Guest access to public Boards, or the Sidebar Log out item describe the V9 build; group 33 supersedes those behaviours.
- Group 32 (V9, auth end-to-end tests) adds tests only and changes no application code. It needs the login page (15.4) and the Sidebar Log out item (16.1), and shares the Playwright setup with 20.1. Tests SO-03 and SO-05 wait for Open Question 5.

- Group 27 (Trello-style board and card modal, Decision I) runs after 26.7 and before the remaining frontend tasks; it changes components built in tasks 16 to 18 without changing the API client. Task 18.4 tests the new modal, and 19.2 adds the Categories, Members, and Users screens on the new shell.
- Group 26 (Tailwind CSS and shadcn/ui restyle, Decision H) runs after task 15 and before the app shell tasks 16 to 19; the components written before it are restyled in 26.3, with their props, logic, `lib/`, and API client unchanged. It touches no backend code.
- Google OAuth is out of scope and has no task.
- Group 24 (flask-smorest and envelope migration) must be done before the frontend group 15, before group 23 (generated documentation), and before test 14.4 (envelope property test). The frontend `lib/api.ts` (task 15.3) reads the boolean `status` and unwraps `data` from the V6 envelope `{ status, message, data }`, and throws `ApiError(httpStatus, code, message, details)` from `{ status: false, message, error: { code, details? } }`.
- V6 (Decision G) envelope rule for every task: `status` is a boolean true exactly when the HTTP status is 2xx; the message text appears once at the top level; `error` has only `code` and, for `VALIDATION_ERROR`, `details`; mutating endpoints send a descriptive message and reads send "OK".
- Tasks 1 to 13 were built as plain `flask.Blueprint` code with `{ "data": ... }` bodies; their checkboxes stay ticked, and group 24 changes the implementation without changing URLs, status codes, or role rules.
- Group 25 (relationships and eager loading) runs after group 24, because the marshmallow schemas replace the DTO functions, and before the checkpoint 14.6 and the frontend group 15. It needs no migration. The cross-cutting tests in group 14 run after it.
- Property 39 (constant query count) is covered by optional task 25.3; Properties 1 to 38 keep their existing tasks.
- Task 23 depends on group 24 (it documents the generated OpenAPI); it is listed last only for numbering.
- Tasks marked with `*` are optional test tasks.
- Services are tested against fake repositories; no `Model.query` call appears outside a `repository.py`.
- Task 5.8 uses `app/common/ordering.py`, which task 6.1 creates; implement 6.1 before 5.8.
- Property 8, 9, and 11 are split across two tasks each (board/card, edit/move); both parts reference the same property.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2"] },
    { "id": 1, "tasks": ["1.3", "1.4"] },
    { "id": 2, "tasks": ["2.1", "2.2", "2.3"] },
    { "id": 3, "tasks": ["2.4", "2.5"] },
    { "id": 4, "tasks": ["3.1", "6.1", "5.1"] },
    { "id": 5, "tasks": ["3.2", "3.3", "3.4", "6.2", "5.2"] },
    { "id": 6, "tasks": ["3.5", "4.1"] },
    { "id": 7, "tasks": ["4.2", "4.3", "4.4", "4.7", "4.10", "4.12"] },
    { "id": 8, "tasks": ["4.5", "4.6", "4.8", "4.9", "4.11", "4.13", "5.3", "7.1"] },
    { "id": 9, "tasks": ["5.4", "5.5", "5.6", "5.8", "5.10", "6.3", "7.2", "8.1", "9.1", "12.1"] },
    { "id": 10, "tasks": ["5.7", "5.9", "5.11", "5.12", "6.4", "8.2", "8.3", "9.2", "9.3", "10.1", "10.2", "11.1", "12.2", "13.1"] },
    { "id": 11, "tasks": ["6.5", "8.4", "8.5", "10.3", "11.2", "13.2"] },
    { "id": 12, "tasks": ["24.1"] },
    { "id": 13, "tasks": ["24.2"] },
    { "id": 14, "tasks": ["24.3"] },
    { "id": 15, "tasks": ["24.4"] },
    { "id": 16, "tasks": ["25.1"] },
    { "id": 17, "tasks": ["25.2"] },
    { "id": 18, "tasks": ["25.3"] },
    { "id": 19, "tasks": ["25.4"] },
    { "id": 20, "tasks": ["14.1", "14.2", "14.3", "14.4", "14.5"] },
    { "id": 21, "tasks": ["14.6"] },
    { "id": 22, "tasks": ["15.1"] },
    { "id": 23, "tasks": ["15.2", "15.3"] },
    { "id": 24, "tasks": ["15.4", "15.5"] },
    { "id": 25, "tasks": ["26.1"] },
    { "id": 26, "tasks": ["26.2"] },
    { "id": 27, "tasks": ["26.3"] },
    { "id": 28, "tasks": ["26.4"] },
    { "id": 29, "tasks": ["26.5"] },
    { "id": 30, "tasks": ["26.6"] },
    { "id": 31, "tasks": ["26.7"] },
    { "id": 32, "tasks": ["27.1"] },
    { "id": 33, "tasks": ["27.2", "27.3", "27.6"] },
    { "id": 34, "tasks": ["27.4", "27.6.1", "27.7"] },
    { "id": 35, "tasks": ["27.5", "27.8"] },
    { "id": 36, "tasks": ["27.9"] },
    { "id": 37, "tasks": ["28.1"] },
    { "id": 38, "tasks": ["28.2", "28.3"] },
    { "id": 39, "tasks": ["28.4"] },
    { "id": 40, "tasks": ["29.1", "29.2"] },
    { "id": 41, "tasks": ["29.3", "29.4", "29.5"] },
    { "id": 42, "tasks": ["29.6"] },
    { "id": 43, "tasks": ["30.1", "30.2"] },
    { "id": 44, "tasks": ["30.3", "30.4", "30.6", "30.7", "30.8"] },
    { "id": 45, "tasks": ["30.5"] },
    { "id": 46, "tasks": ["30.9"] },
    { "id": 47, "tasks": ["31.1"] },
    { "id": 48, "tasks": ["31.2", "31.3", "31.4"] },
    { "id": 49, "tasks": ["31.5"] },
    { "id": 50, "tasks": ["16.1"] },
    { "id": 51, "tasks": ["16.2", "17.1"] },
    { "id": 52, "tasks": ["17.2"] },
    { "id": 53, "tasks": ["17.3", "18.1"] },
    { "id": 54, "tasks": ["18.2", "18.3"] },
    { "id": 55, "tasks": ["18.4", "19.1", "19.2"] },
    { "id": 56, "tasks": ["19.3"] },
    { "id": 57, "tasks": ["20.1", "20.2"] },
    { "id": 58, "tasks": ["21.1"] },
    { "id": 59, "tasks": ["22.1"] },
    { "id": 60, "tasks": ["22.2"] },
    { "id": 61, "tasks": ["23.1"] },
    { "id": 62, "tasks": ["23.2"] },
    { "id": 63, "tasks": ["23.3", "23.4"] },
    { "id": 64, "tasks": ["32.1"] },
    { "id": 65, "tasks": ["32.2"] },
    { "id": 66, "tasks": ["32.3", "32.4", "32.5"] },
    { "id": 67, "tasks": ["32.6"] },
    { "id": 68, "tasks": ["33.1", "33.26"] },
    { "id": 69, "tasks": ["33.2", "33.3", "33.9"] },
    { "id": 70, "tasks": ["33.4", "33.5", "33.7", "33.10"] },
    { "id": 71, "tasks": ["33.6", "33.8", "33.11"] },
    { "id": 72, "tasks": ["33.12", "33.13"] },
    { "id": 73, "tasks": ["33.14"] },
    { "id": 74, "tasks": ["33.15", "33.16", "33.17", "33.19"] },
    { "id": 75, "tasks": ["33.18", "33.20"] },
    { "id": 76, "tasks": ["33.21", "33.22"] },
    { "id": 77, "tasks": ["33.23", "33.24", "33.25"] },
    { "id": 78, "tasks": ["33.27"] },
    { "id": 79, "tasks": ["33.28", "33.33", "33.35", "33.39"] },
    { "id": 80, "tasks": ["33.29", "33.34", "33.36"] },
    { "id": 81, "tasks": ["33.30", "33.31", "33.37"] },
    { "id": 82, "tasks": ["33.32", "33.38"] },
    { "id": 83, "tasks": ["33.40"] }
  ]
}
```
