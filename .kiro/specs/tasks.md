# Implementation Plan

## Overview

Version V5. Derived from `requirements.md` and `design.md` in this folder. Backend first (Flask + SQLAlchemy blueprints), then the Next.js frontend, then end-to-end tests and stretch features.

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
    - Create `app/common/responses.py` (`ok(data, status=200)`) and `app/common/errors.py` (`ValidationError` 400, `Unauthorized` 401, `Forbidden` 403, `NotFound` 404, `Conflict` 409, generic 500 handler) rendering `{ "error": { "code", "message" } }`.
    - Register one error handler in the factory; routes contain no try/except.
    - _Requirements: 13.2, 13.3, 13.4_
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
    - `Board`: `name`, `visibility` enum (public, private; default private), nullable `owner_id` FK User, `deleted_at`, `archived_at`.
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
    - `POST /api/auth/logout` returns `{ "data": null }` and revokes nothing.
    - Defer rate limiting; add no Google OAuth route.
    - _Requirements: 1.1, 1.2, 1.14, 1.15, 1.16, 1.18, 1.11_
  - [ ]* 3.3 Write property test for registration and login round trip
    - **Property 1: Registration and login round trip**
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.13**
  - [ ]* 3.4 Write property test for registration validation and unique identifier
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
  - [ ]* 4.2 Write property test for Board_Access
    - **Property 4: Board_Access function**
    - **Validates: Requirements 3.4, 6.5, 7.1, 8.3, 8.4, 11.6, 11.11, 12.1, 12.7**
  - [ ]* 4.3 Write property test for the permission matrix
    - **Property 3: Permission matrix and role source**
    - **Validates: Requirements 1.8, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 3.3, 3.4, 3.5, 3.7, 4.1, 4.4, 4.7, 6.1, 6.4, 7.3, 7.8, 10.4, 11.3, 11.9**
  - [x] 4.4 Implement board creation, listing, and retrieval
    - `POST /api/boards` (manager, admin) inserts the Board and five Default_Columns (`Todo, In Progress, Review, Revision, Done`, `order` 0 to 4) in one transaction.
    - `GET /api/boards` uses `list_visible` (Guest: public non-deleted; signed-in: public plus accessible); `GET /api/boards/{id}` calls `require_access` and `serialize_board` omits `comments` and `activity_log` for a Guest.
    - _Requirements: 2.1, 3.1, 3.3, 3.9, 3.10, 11.4, 11.7, 11.12_
  - [ ]* 4.5 Write property test for default column seeding
    - **Property 6: Board creation seeds default columns**
    - **Validates: Requirements 3.1**
  - [ ]* 4.6 Write property test for board list visibility
    - **Property 34: Board list visibility**
    - **Validates: Requirements 11.4, 11.6, 11.12**
  - [x] 4.7 Implement board update, owner reassignment, visibility, archive, soft delete
    - `PATCH /api/boards/{id}`: `owner_id` change by Manager or Admin only, new owner must have role `supervisor` (400 otherwise), `null` clears; visibility change by Manager, Admin, or owner/BoardMember Supervisor; log `board.owner_changed` and visibility changes in the same transaction.
    - `POST /api/boards/{id}/archive`, `POST /api/boards/{id}/unarchive`, `DELETE /api/boards/{id}` (soft, sets `deleted_at`), all Manager and Admin only; never hard-delete a Board.
    - _Requirements: 3.2, 3.6, 3.7, 3.8, 3.16, 3.17, 3.18, 3.19, 11.2, 11.3, 11.8, 11.9_
  - [ ]* 4.8 Write property test for owner reassignment
    - **Property 19: Owner reassignment validation**
    - **Validates: Requirements 3.2, 3.16, 3.17, 3.18, 3.19**
  - [ ]* 4.9 Write property test for soft delete and archive round trip
    - **Property 8: Soft delete hides without removing** (Board part; the card children part is completed in task 5.7)
    - **Property 9: Archive round trip** (Board part)
    - **Validates: Requirements 3.6, 3.8, 11.8, 11.10**
  - [x] 4.10 Implement board members endpoints
    - `GET /api/boards/{id}/members` (requires `can_access`), `POST /api/boards/{id}/members` body `{ "user_id" }` (owner, Manager, Admin; 409 when the pair exists; 404 when the user does not exist), `DELETE /api/boards/{id}/members/{user_id}` (404 when the pair does not exist); write one `board.member_added` or `board.member_removed` Activity_Log row in the same transaction.
    - _Requirements: 3.11, 3.12, 3.13, 3.14, 3.15_
  - [ ]* 4.11 Write property test for BoardMember add and remove
    - **Property 18: BoardMember add and remove**
    - **Validates: Requirements 3.11, 3.12, 3.13, 3.14, 3.15**
  - [x] 4.12 Implement column creation
    - `POST /api/boards/{board_id}/columns` guarded by `require_access` then `can_write_staff`; new Column gets `order = max + 1`.
    - _Requirements: 2.6, 3.4, 3.5_
  - [ ]* 4.13 Write property test for column append order
    - **Property 7: Column append order**
    - **Validates: Requirements 3.4**

- [x] 5. Cards, subtasks, attachments, assignment
  - [x] 5.1 Implement signing and clock-injectable file URL helpers
    - `app/common/signing.py`: `sign_file_url(attachment_id, now)` returns `/api/attachments/{id}/file?exp=&sig=` with `exp = now + 900 s` and HMAC-SHA256 over `"{id}.{exp}"` using `FILE_URL_SECRET`; `verify_file_signature(...)` uses `hmac.compare_digest` and rejects missing, tampered, or expired values.
    - _Requirements: 4.18, 4.24, 4.25_
  - [ ]* 5.2 Write property test for signed URL validity and expiry
    - **Property 20: Signed file URL validity and expiry**
    - **Validates: Requirements 4.18, 4.24, 4.25**
  - [x] 5.3 Implement card CRUD, archive, soft delete
    - `card_repository` and `card_service`: `POST /api/columns/{column_id}/cards`, `GET /api/cards/{id}`, `PATCH /api/cards/{id}`, `DELETE /api/cards/{id}` (soft), `POST /api/cards/{id}/archive`, `POST /api/cards/{id}/unarchive`.
    - Validate priority (high, medium, low) and `end_date >= start_date` (400 `VALIDATION_ERROR`); creation, delete, and archive need `require_access` then `can_write_staff` (Members get 403); edits by a Member only when `assignee_id` equals the Member, by Supervisor/Manager/Admin only with Board_Staff_Access; write one Activity_Log row per change.
    - Child rows (subtasks, attachments, comments) are hidden by joining `Card.deleted_at`; never hard-delete a Card.
    - _Requirements: 2.6, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10, 4.23, 4.29, 11.10_
  - [ ]* 5.4 Write property tests for card validation and edit scope
    - **Property 10: Card field validation**
    - **Validates: Requirements 4.1, 4.2, 4.3**
    - **Property 11: Member edit and move scope** (edit part; move part is completed in task 6.4)
    - **Validates: Requirements 4.8, 4.9, 4.10**
  - [ ]* 5.5 Write property tests for soft delete of cards and archive round trip
    - **Property 8: Soft delete hides without removing** (card and children part)
    - **Validates: Requirements 4.5, 4.23, 4.29, 12.3**
    - **Property 9: Archive round trip** (card part)
    - **Validates: Requirements 4.6, 11.10**
  - [x] 5.6 Implement assignment and unassignment
    - `card_service.assign_card`: non-null `assignee_id` inserts an `assigned` Notification (`notify_date` = today in `APP_TIMEZONE`, conflict ignored) and a `card.assigned` Activity_Log row in the same commit; `null` clears the assignee, writes `card.unassigned`, creates no Notification.
    - _Requirements: 4.11, 4.28, 9.1_
  - [ ]* 5.7 Write property test for assignment effects
    - **Property 12: Assignment and unassignment effects**
    - **Validates: Requirements 4.11, 4.28, 9.1**
  - [x] 5.8 Implement subtasks
    - `card_service.add_subtask`, `toggle_subtask`, `reorder_subtasks`, `delete_subtask` with `POST /api/cards/{id}/subtasks`, `PATCH /api/subtasks/{id}` (`title`, `is_done`, `order`), `DELETE /api/subtasks/{id}`; `is_done` defaults to false; edit rights as in task 5.3. Reorder uses `app/common/ordering.py` (created in task 6.1; stub the import here with the same interface or implement 6.1 first).
    - _Requirements: 4.12, 4.13, 4.14_
  - [ ]* 5.9 Write property test for subtasks
    - **Property 13: Subtask toggle round trip and deletion**
    - **Validates: Requirements 4.12, 4.13, 4.14**
  - [x] 5.10 Implement attachments and signed file URL endpoints
    - `POST /api/cards/{id}/attachments` (JSON link or multipart upload; accept only PDF, Word, RAR; 400 for neither `url` nor file or a disallowed type before writing storage), `DELETE /api/attachments/{id}`.
    - Store uploads under the private `UPLOAD_DIR`, not mounted as a static route.
    - `GET /api/attachments/{id}/url` (open to Guests on public boards) re-runs `require_access` and returns `{ file_url, expires_at }`; `GET /api/attachments/{id}/file?exp=&sig=` takes no Token and returns 403 for a bad, tampered, missing, or expired signature, and 404 when the card or board is soft-deleted.
    - `serialize_card(card, viewer)` embeds a fresh signed `file_url` per uploaded attachment, returns link `url` as stored, and omits `comments` and `activity` for a Guest.
    - _Requirements: 4.15, 4.16, 4.17, 4.18, 4.24, 4.25, 4.26, 4.27, 8.5_
  - [ ]* 5.11 Write property tests for attachments
    - **Property 14: Attachment validity**
    - **Validates: Requirements 4.15, 4.16, 4.17, 4.27**
    - **Property 21: Attachment access gating**
    - **Validates: Requirements 4.18, 4.26, 15.7**
  - [x]* 5.12 Write pytest tests for attachment access
    - Cover a permitted viewer, an unrelated Member (403), a Guest on a private board (401), a Guest on a public board (URL issued), an expired signature (403), and a modified `sig` or `exp` (403).
    - _Requirements: 15.7_

- [ ] 6. Ordering and card move
  - [x] 6.1 Implement ordering helpers
    - `app/common/ordering.py`: `position_for(prev, next, siblings)` (empty list `1.0`, first `min - 1`, last `max + 1`, otherwise average), `needs_rebalance(prev, next)` (gap below `1e-6`), `rebalance(siblings)` renumbering `1.0, 2.0, ...` preserving order.
    - _Requirements: 4.13, 5.1, 5.10, 5.11_
  - [ ]* 6.2 Write property test for ordering and rebalance
    - **Property 15: Drop order and rebalance (cards and subtasks)**
    - **Validates: Requirements 4.13, 5.1, 5.10, 5.11**
  - [x] 6.3 Implement move card
    - `PATCH /api/cards/{id}/move` with `column_id`, `prev`, `next` neighbour ids; `card_service.move_card`: `require_access`; Member only when assigned; Supervisor, Manager, Admin only with `can_write_staff`; 400 when the target column belongs to another board; recompute order server-side (ignore client `order`), renumber the column in the same transaction when the gap is below `1e-6`; write exactly one `card.moved` row with source and target column; commit once.
    - Return 401 without a Token.
    - _Requirements: 5.1, 5.2, 5.4, 5.5, 5.6, 5.7, 5.8, 5.10, 5.11, 5.12_
  - [ ]* 6.4 Write property tests for move
    - **Property 16: Move persists, logs once, and stays on the board**
    - **Validates: Requirements 5.2, 5.8, 5.9, 5.12**
    - **Property 11: Member edit and move scope** (move part)
    - **Validates: Requirements 4.8, 4.9, 4.10, 5.4, 5.5, 5.6**
  - [ ] 6.5 Checkpoint - Ensure all tests pass, ask the user if questions arise

- [x] 7. Categories
  - [x] 7.1 Implement the categories blueprint
    - `GET /api/boards/{board_id}/categories` (`require_access` only, no role check, Guests on public boards allowed, only that board's categories), `POST /api/boards/{board_id}/categories`, `PATCH /api/categories/{id}`, `DELETE /api/categories/{id}` (the last three need `can_write_staff`).
    - Case-insensitive duplicate name on a board returns 409 `CONFLICT` on create and rename; deleting a category nulls `Card.category_id`; categories of a soft-deleted board stay stored and are unreachable.
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.12_
  - [ ]* 7.2 Write property test for categories
    - **Property 17: Categories are board-scoped and name-unique**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.12**

- [x] 8. Comments
  - [x] 8.1 Implement comment creation and replies
    - `POST /api/cards/{id}/comments` (Member, Supervisor, Manager with `can_access`; Admin 403; blank body 400 with message `content is required`) and `POST /api/comments/{id}/replies` (400 when the target has a non-null `parent_id`; increments the parent's `reply_count` in the same transaction). Provide no like or vote endpoint.
    - A Guest calling any comment endpoint gets 403 on a public board and 401 on a private board, with no `comments` field.
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.16, 14.3_
  - [ ]* 8.2 Write property tests for comment creation
    - **Property 22: Blank comments rejected**
    - **Validates: Requirements 7.1, 7.2**
    - **Property 23: Reply count invariant and depth cap**
    - **Validates: Requirements 7.4, 7.5**
  - [x] 8.3 Implement priority flag and listing
    - `PATCH /api/comments/{id}/priority` (Manager only toggles `is_priority`; others 403, no Token 401).
    - `GET /api/cards/{id}/comments?sort=latest|popular`: priority comments first (newest first), then others by `created_at DESC` (latest or omitted) or `(reply_count DESC, created_at DESC)` (popular); replies nested oldest-first regardless of sort; each comment has `reply_count`, `is_priority`, `can_create_card = viewer.role in (supervisor, manager, admin) and author.role == "manager"`.
    - _Requirements: 7.7, 7.8, 7.9, 7.10, 7.11, 7.12, 7.13, 7.14, 7.15_
  - [ ]* 8.4 Write property tests for comment listing
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
  - [ ]* 9.2 Write property tests for activity
    - **Property 29: One activity row per state change**
    - **Validates: Requirements 1.7, 8.1, 8.2**
    - **Property 30: Activity queries return the right rows**
    - **Validates: Requirements 8.3, 8.4**
  - [ ]* 9.3 Write property test for guest privacy
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
  - [ ]* 10.3 Write property tests for notifications
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
  - [ ]* 11.2 Write property test for analytics
    - **Property 33: Analytics access and correctness**
    - **Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5, 10.7**

- [x] 12. Card search and filter
  - [x] 12.1 Implement the board cards list
    - `GET /api/boards/{id}/cards?search=&filter[priority]=&filter[assignee]=&filter[category]=`: `require_access` first (403 signed-in, 401 Guest on private); case-insensitive substring match on `title` or `description`; filters combine with AND; unsupported filter key returns 400 `VALIDATION_ERROR`; always exclude soft-deleted cards; Guest results contain card data only.
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.6, 12.7_
  - [ ]* 12.2 Write property test for search and filter
    - **Property 35: Search and filter correctness**
    - **Validates: Requirements 12.1, 12.2, 12.3, 12.4**

- [x] 13. User administration
  - [x] 13.1 Implement admin user management
    - `GET /api/users`, `POST /api/users`, `PATCH /api/users/{id}` (edit, assign role), Admin only; each mutation writes `user.created`, `user.updated`, or `user.role_changed` to the Activity_Log in the same transaction; non-Admin gets 403, no Token 401.
    - _Requirements: 1.7, 1.8, 2.4_
  - [x]* 13.2 Write unit tests for user administration
    - Cover Admin success, Member, Supervisor, and Manager 403, no Token 401, and the activity row.
    - _Requirements: 1.7, 1.8_

- [ ] 14. Backend checkpoint and cross-cutting tests
  - [x]* 14.1 Write the 401/403 sweep test for every mutating endpoint
    - Enumerate registered POST, PATCH, PUT, DELETE routes; assert 401 with no Token and 403 with an insufficient-role Token, excluding the public auth routes and the signature-gated file route; fail when a mutating route is missing from the list.
    - _Requirements: 2.8, 2.9, 2.10, 15.5_
  - [ ]* 14.2 Write property test for 401 versus 403 versus 404
    - **Property 5: 401 versus 403 versus 404**
    - **Validates: Requirements 2.8, 2.9, 11.5, 12.7, 13.10**
  - [ ]* 14.3 Write the Board_Access matrix and private board tests
    - Cover {guest, member, supervisor owner, supervisor BoardMember, supervisor unrelated, manager, admin} against {public, private} for columns, cards, categories, comments, activity, search, and attachments, including an unrelated Supervisor getting 403 on public-board writes and an unrelated Member getting 403 on a private board.
    - _Requirements: 15.4, 15.6_
  - [x]* 14.4 Write property test for the response envelope
    - Run against the Flask test client for every registered `/api` route (excluding the documentation routes and the successful bytes of the signed file route), including unknown routes and wrong methods; requires group 24.
    - Assert success bodies are exactly `{ status, message, data }` and error bodies are exactly `{ status, message, error: { code, message } }`, with `status` equal to the HTTP status, `error.message` equal to `message`, and validation failures returning 400 `VALIDATION_ERROR`, never 422.
    - **Property 36: Response envelope**
    - **Validates: Requirements 13.2, 13.3, 13.4, 13.11, 13.13**
  - [x]* 14.5 Write static checks
    - Assert no `.query` call outside a `repository.py` file, and that `.env.example` files list the required variables and no real `.env` is tracked.
    - _Requirements: 13.7, 13.9, 15.4_
  - [ ] 14.6 Checkpoint - Ensure all tests pass, ask the user if questions arise

- [ ] 15. Frontend scaffold, tokens, shared components, API client, auth pages
  - [ ] 15.1 Scaffold the Next.js app and design tokens
    - Initialize Next.js (App Router, TypeScript) in `frontend/`; confirm `frontend/.env.example` lists `NEXT_PUBLIC_API_URL`.
    - Create `styles/tokens.css` copying the prototype's `:root` custom properties (`--brand`, `--surface-*`, `--ink*`, `--space-*`, `--radius-*`, `--label-*`) from `design/kanban-prototype.html`; use only these variables for colors, spacing, and radii, with mobile-first base styles and `min-width` queries (960px breakpoint).
    - _Requirements: 14.5, 14.9_
  - [ ] 15.2 Create shared components
    - `BaseButton`, `BaseBadge`, `BaseModal` in `frontend/components/shared/`, styled only from `tokens.css`; all pages import these instead of raw `<button>`, badges, or modals.
    - _Requirements: 14.9, 14.10_
  - [ ] 15.3 Create the API client and session handling
    - `lib/api.ts`: adds the Bearer token, unwraps `{ data }`, throws a typed `ApiError(code, message, status)`; a 401 clears the stored Token and redirects to login; logout calls `POST /api/auth/logout` then discards the Token.
    - _Requirements: 1.15, 1.16, 13.2, 13.3_
  - [ ] 15.4 Build login and register pages
    - `app/(auth)/login/page.tsx` and `register/page.tsx` using an `AuthSplitLayout` Server Component: brand panel beside an elevated rounded form card on desktop; brand panel hidden at mobile width.
    - Forms submit `login_identifier` and password through the API client and store the returned Token.
    - _Requirements: 1.1, 1.2, 1.9, 1.10, 14.4, 14.5_
  - [ ]* 15.5 Write component tests for shared components and auth pages
    - Test that the auth form renders and shows server errors; test `BaseButton`, `BaseBadge`, `BaseModal` basics with React Testing Library.
    - _Requirements: 1.9, 14.10_

- [ ] 16. App shell, sidebar, side panel
  - [ ] 16.1 Build the app shell
    - `app/(app)/layout.tsx` (Server Component) with `Sidebar` (Client): brand, nav with Inbox and Activity links, Boards list from `GET /api/boards` as the board switcher, team members, profile; Categories entry only for supervisor, manager, admin.
    - Below 960px the sidebar is an off-canvas drawer behind a scrim with its toggle in a persistent header; at 960px and above it stays visible.
    - Place primary actions (add card, open Inbox, switch Board) in the persistent header or bottom third on mobile.
    - _Requirements: 3.9, 6.11, 14.6, 14.7, 14.8, 14.11_
  - [ ] 16.2 Build the side panel host
    - `SidePanel` (Client) sliding in from the right with one shared `toggleSidePanel("inbox" | "activity")` called by the sidebar items and the header bell; render a view only when the API returned its data.
    - _Requirements: 8.6, 9.6, 9.7_

- [ ] 17. Board view, filters, drag-and-drop
  - [ ] 17.1 Build the board page and filter row
    - `app/(app)/boards/[id]/page.tsx` (Server Component) fetches columns and cards; `FilterRow` (Client) renders category chips from `GET /api/boards/{id}/categories` (no hard-coded list), re-fetches on board switch, and a search input; chip selection and search call `GET /api/boards/{id}/cards`.
    - _Requirements: 3.10, 6.9, 6.10, 12.5_
  - [ ] 17.2 Implement drag-and-drop
    - `lib/ordering.ts` with pure `computeDropOrder` mirroring the backend rules (first `min - 1`, last `max + 1`, empty `1.0`, average otherwise).
    - `Board` (Client): placeholder at the drop target, FLIP animation of siblings, `PATCH /api/cards/{id}/move` on `dragend`, reconcile with the response, revert the card on failure; after refresh the card renders at its moved position.
    - Add a per-column "+ Add a card" action inside the thumb-reach rule.
    - _Requirements: 5.2, 5.3, 5.9, 14.8_
  - [ ]* 17.3 Write fast-check test for drop order
    - Mirror Property 15 for `computeDropOrder`.
    - **Property 15: Drop order and rebalance (cards and subtasks)**
    - **Validates: Requirements 4.13, 5.1, 5.10, 5.11**

- [ ] 18. Card modal, subtasks, attachments, comments
  - [ ] 18.1 Build the two-pane card modal
    - `CardModal` (Client) using `BaseModal`: left pane has title, description (`CardDescription` Server Component), priority, dates, attachments, subtask checklist, and `ActivityList` (Server Component); right pane has the comment thread and composer.
    - "Save changes" commits the left pane without closing the modal or affecting the composer; omit the activity section and comment thread when the response omits `activity` or `comments`.
    - _Requirements: 4.20, 4.21, 7.20, 8.7, 14.11_
  - [ ] 18.2 Build the subtask checklist and attachment list
    - `SubtaskChecklist` (Client): flat checkbox list, inline-editable titles, drag handle reorder, one-click toggle calling `PATCH /api/subtasks/{id}`.
    - `AttachmentList` (Client): links open with `target="_blank" rel="noopener noreferrer"`, no in-app preview; before opening, request a fresh URL from `GET /api/attachments/{id}/url` when the `exp` query value has passed or a request returns 403.
    - _Requirements: 4.14, 4.19, 4.22_
  - [ ] 18.3 Build the comment thread and composer
    - `CommentThread` (Client): priority comments first with a priority indicator, remaining top-level comments under a Latest/Popular toggle with a reply-count badge, replies nested, Reply action only where `parentId === null`, no like button, "Create card" button only where `comment.canCreateCard`, a Manager-only "Mark as priority" action.
    - `CommentComposer` posts independently without closing the modal.
    - _Requirements: 7.17, 7.18, 7.19, 7.20_
  - [ ]* 18.4 Write component tests for card modal pieces
    - Reply only on top-level comments; create-card button only when `canCreateCard`; thread, activity, and inbox omitted when the data is absent; `AttachmentList` renders `target="_blank" rel="noopener noreferrer"` and requests a fresh URL when expired.
    - _Requirements: 4.19, 7.18, 7.19, 7.20, 8.7, 9.7_

- [ ] 19. Inbox, activity panel, categories screen, members screen
  - [ ] 19.1 Build inbox and activity panel contents
    - Inbox view lists `GET /api/notifications` with unread count and mark-read / read-all actions; Activity view lists the board feed from `GET /api/boards/{id}/activity`; neither polls or computes notifications client-side.
    - _Requirements: 8.6, 9.4, 9.5, 9.6, 9.8, 9.9_
  - [ ] 19.2 Build categories and members screens
    - `app/(app)/boards/[id]/categories/page.tsx` with `CategoriesScreen` (add, rename, recolor, delete) for supervisor, manager, admin, scoped to the current board.
    - `app/(app)/boards/[id]/members/page.tsx` with `BoardMembersScreen` (add and remove) for the owner, Manager, Admin; `app/(app)/admin/users/page.tsx` for Admin user management.
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
    - Cover the envelope (`status`, `message`), error codes, authentication, the role matrix, signed file URLs, ordering and move semantics, then one table plus an example request and response per blueprint group; state that the generated `openapi.json` is the source of truth and how to enable Swagger locally (`APP_ENV=development`), and that it is off in production.
    - _Requirements: 17.2_
  - [x]* 23.4 Write the drift and production-gate tests
    - **Property 37: Every route is documented** (iterate `app.url_map` under `/api`, excluding `static` and the documentation routes, and assert each method and path has an operation in `api.spec.to_dict()["paths"]`, and the reverse)
    - **Property 38: Documentation hidden outside development and testing** (`/api/docs` and `/api/openapi.json` return 200 for `development` and `testing`, and the 404 envelope for `production`, unset, or any other value)
    - **Validates: Requirements 17.1, 17.4, 17.5, 17.6, 17.8, 17.9**

- [x] 24. Migrate the implemented backend to flask-smorest and the status/message envelope
  - [x] 24.1 Add flask-smorest, the envelope, and the error mapping
    - Add `flask-smorest` and `marshmallow` to `backend/requirements.txt`.
    - Create `backend/app/api.py` with `EnvelopeApi(flask_smorest.Api)`: register every blueprint on it, declare the `bearerAuth` scheme once, and map errors to `{ status, message, error: { code, message } }`: `AppError` to its status and code, smorest/webargs 422 to 400 `VALIDATION_ERROR` (first field message), 404 `NOT_FOUND`, 405 `METHOD_NOT_ALLOWED`, any other exception to 500 `INTERNAL_ERROR` with a generic message, and the JWT missing, invalid, and expired callbacks to the 401 envelope. Set `Api.ERROR_SCHEMA` to the error envelope schema. Remove the old app-level error handler.
    - In `api.py`, set `API_TITLE`, `API_VERSION`, `OPENAPI_VERSION`, and, only when `APP_ENV` is `development` or `testing`, the `OPENAPI_*` keys for `/api/openapi.json` and `/api/docs`; add the `flask export-openapi` command that writes `backend/openapi.json` from `api.spec.to_dict()` under any `APP_ENV`.
    - Create `backend/app/common/envelope.py` with `envelope(DataSchema, many=False)` (cached `<Name>Envelope` / `<Name>ListEnvelope` schema with `status`, `message`, `data`), `NullEnvelopeSchema`, and `ErrorEnvelopeSchema`.
    - Change `ok(data, message=None, status=200)` in `app/common/responses.py` to return `{ status, message, data }` with the HTTP reason phrase as the default message; update error rendering in `app/common/errors.py` handling to emit `status` and `message`.
    - Keep `AppError` classes free of Flask imports; keep all URLs, status codes, and role rules unchanged.
    - _Requirements: 13.2, 13.3, 13.4, 13.11, 13.12, 13.13, 13.15, 17.3, 17.4, 17.5, 17.6, 17.10_
  - [x] 24.2 Convert each blueprint to flask-smorest with marshmallow schemas
    - For each of `auth, boards (including members), columns, cards (including subtasks, attachments, and the board cards search/filter), categories, comments, notifications, analytics, users, activity (card and board activity reads)`: replace `flask.Blueprint` with `flask_smorest.Blueprint`; turn `schema.py` into marshmallow request, query, and payload schemas; validate with `@blp.arguments(Schema)` or `@blp.arguments(Schema, location="query")`; declare each success response with `@blp.response(status, envelope(PayloadSchema))` (`NullEnvelopeSchema` for logout); mark protected operations with `@blp.doc(security=[{"bearerAuth": []}])`; return `ok(dto, "<descriptive message>", status)` with the same status as the declaration.
    - Keep data-dependent rules (uniqueness, access, ordering, ownership) in the service; `service.py` and `repository.py` import none of `flask`, `flask_smorest`, or `marshmallow`. Keep `filter[<field>]` parsing and the `400` for an unsupported filter key, and the signed file route returning raw bytes on success and the error envelope on failure.
    - Keep every URL, HTTP status code, and role rule unchanged.
    - _Requirements: 13.2, 13.3, 13.12, 13.13, 13.14, 13.15_
  - [x] 24.3 Update the existing tests and add envelope tests
    - Update the 36 existing pytest tests that assert `{ "data": ... }` or `{ "error": ... }` bodies to the new `{ status, message, data }` and `{ status, message, error }` shapes; change no expected HTTP status.
    - Add tests that: every success body carries `status` equal to the HTTP status and a non-empty `message`; every error body carries `status`, `message`, and `error.message` equal to `message`; body and query validation failures return 400 `VALIDATION_ERROR` and never 422; an unknown route returns the 404 envelope, a wrong method returns the 405 envelope, a forced unhandled exception returns the 500 envelope with a generic message, and a missing or invalid JWT returns the 401 envelope; the signed file route returns the error envelope on failure.
    - _Requirements: 13.2, 13.3, 13.4, 13.11, 13.13_
  - [x] 24.4 Checkpoint - Run the full pytest suite
    - Run the full backend `pytest` suite and ensure all tests pass, ask the user if questions arise.

- [ ] 25. Add model relationships and eager loading
  - [ ] 25.1 Add the five relationships to the models
    - Declare `Board.columns`, `Board.members`, `Card.subtasks`, `Card.attachments`, and `Comment.replies`, each with its inverse (`Column.board`, `BoardMember.board`, `Subtask.card`, `Attachment.card`, `Comment.parent` with `remote_side`) through `back_populates` (never `backref`), `lazy="raise"`, the `order_by` from the design's relationship table, and no `cascade`.
    - Declare no other relationships; `Card.assignee_id`, `Card.category_id`, `Comment.author_id`, `Board.owner_id`, and `Card.column_id` stay plain foreign-key columns.
    - Remove any `to_dict` or other serialization method still on a model; serialization stays in the marshmallow schemas.
    - Add no migration: this is a mapper-level change only.
    - _Requirements: 13.16, 13.17_
  - [ ] 25.2 Load related rows in the repositories
    - Per the design's repository loading table: `board_repository.get_detail` uses `selectinload(Board.columns)`; `card_repository.list_for_board` and `get_detail` use `selectinload(Card.subtasks)` and `selectinload(Card.attachments)`; `comment_repository.list_for_card` uses `selectinload(Comment.replies)` and selects the author role in the same joined query.
    - Fix every service, schema, and route that now raises because it read an unloaded relationship; services and schemas must trigger no lazy load, and the board cards list must run a constant number of queries.
    - _Requirements: 13.18, 14.12_
  - [ ]* 25.3 Write tests for relationships and constant query count
    - **Property 39: Constant query count for list endpoints**: count SQL statements with a `before_cursor_execute` listener for a board with 5 cards and a board with 50 cards (each with subtasks and attachments), and assert the counts are equal; repeat for the comment listing.
    - Add the `lazy="raise"` test: access an unloaded `Card.subtasks`, `Board.columns`, `Board.members`, `Card.attachments`, and `Comment.replies` and assert `sqlalchemy.exc.InvalidRequestError`, then assert the access succeeds when the repository loads it.
    - Add a static check: no model defines `to_dict`, and each of the five relationships has `lazy="raise"`, `back_populates`, and no `cascade`.
    - **Validates: Requirements 13.16, 13.17, 13.18, 14.12, 15.8, 15.9**
  - [ ] 25.4 Checkpoint - Run the full pytest suite
    - Run the full backend `pytest` suite and ensure all tests pass, ask the user if questions arise.

## Notes

- Google OAuth is out of scope and has no task.
- Group 24 (flask-smorest and envelope migration) must be done before the frontend group 15, before group 23 (generated documentation), and before test 14.4 (envelope property test). The frontend `lib/api.ts` (task 15.3) unwraps the new `{ status, message, data }` envelope.
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
    { "id": 25, "tasks": ["16.1"] },
    { "id": 26, "tasks": ["16.2", "17.1"] },
    { "id": 27, "tasks": ["17.2"] },
    { "id": 28, "tasks": ["17.3", "18.1"] },
    { "id": 29, "tasks": ["18.2", "18.3"] },
    { "id": 30, "tasks": ["18.4", "19.1", "19.2"] },
    { "id": 31, "tasks": ["19.3"] },
    { "id": 32, "tasks": ["20.1", "20.2"] },
    { "id": 33, "tasks": ["21.1"] },
    { "id": 34, "tasks": ["22.1"] },
    { "id": 35, "tasks": ["22.2"] },
    { "id": 36, "tasks": ["23.1"] },
    { "id": 37, "tasks": ["23.2"] },
    { "id": 38, "tasks": ["23.3", "23.4"] }
  ]
}
```
