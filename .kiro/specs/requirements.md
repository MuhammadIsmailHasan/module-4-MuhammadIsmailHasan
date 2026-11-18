# Requirements Document

## Introduction

This document specifies the Kanban Task Management application (Version V5). It is a role-based web app with a Flask REST API backend and a mobile-first Next.js frontend. Teams run day-to-day work on boards, columns, and cards, and supervisors and managers oversee progress through analytics without opening every board.

The requirements translate decisions already recorded in `specs/project-brief.md` and the steering documents in `.kiro/steering/`. V5 revises V4 and adds no scope beyond the decisions in the Decisions Log. Eleven decisions that resolved gaps in the brief are recorded there: Decisions 1 to 5 (carried from V1), Decisions A to D (carried from V2), Decision E (carried from V4: every response carries `status` and `message`, and the Backend uses flask-smorest with marshmallow schemas and a generated OpenAPI document), and Decision F (new in V5: models declare SQLAlchemy relationships only for real cross-table reads, repositories load related rows explicitly, and serialization belongs to marshmallow schemas). Criteria affected by a decision carry an inline label such as "(Decision A)".

Out of scope for V2: Google OAuth login (post-MVP, added only after login_identifier and password auth is verified end-to-end), rate limiting and server-side token revocation (deferred past MVP), custom per-board workflow templates beyond the five default columns, and subtasks with their own assignee or date. Stretch features (card `progress` meter, `views_count`, decorative Overview/Notes/Questions tabs) are covered in Requirement 16 and are built only after all other requirements work end-to-end.

This feature requires three data-model additions beyond the current `data-model.md` steering: a nullable `Board.owner_id` (Decision 1), a `BoardMember` entity (Decision A), and a single unique, case-insensitive `login_identifier` column on User in place of separate email and username columns (Decision C).

## Glossary

- **System**: The Kanban Task Management application, consisting of the Backend and the Frontend.
- **Backend**: The Flask REST API, organized as one blueprint per domain, each layered `routes.py → service.py → repository.py → schema.py`.
- **Frontend**: The mobile-first Next.js (App Router, TypeScript) application.
- **Guest**: A visitor without an account or Token. Can view the columns and cards of public boards only.
- **Member**: A signed-in user with the member role.
- **Supervisor**: A signed-in user with the supervisor role. Includes everything a Member can do.
- **Manager**: A signed-in user with the manager role. Includes everything a Supervisor can do.
- **Admin**: A signed-in user with the admin role, a separate administrative track and not a superset of Manager (see Requirement 2 and Decision B).
- **Card_Creator**: A Supervisor, Manager, or Admin. Card creation additionally requires Board_Access to the target Board.
- **login_identifier**: The single unique, case-insensitive string column on User used for registration and login. Its value may have an email shape or a username shape.
- **Board**: A project container holding Columns, Cards, and Categories. Has `visibility` (`public` or `private`) and a nullable `owner_id`.
- **Board_Owner**: The Supervisor referenced by a Board's `owner_id`.
- **BoardMember**: A join record `(board_id, user_id)`, unique per pair, that attaches a user to a Board beyond the Board's `owner_id`.
- **Board_Access**: A user has Board_Access to a Board when the Board is public, or the user is its Board_Owner, a BoardMember, a Manager, or an Admin. For a private Board, a Supervisor has Board_Access only as owner or BoardMember, and a Member only as BoardMember. Card, Comment, Attachment, Activity_Log, and Category access always resolves through the owning Board's Board_Access.
- **Board_Staff_Access**: Write access to a Board's content. A user has Board_Staff_Access when the user is a Manager, an Admin, or a Supervisor who is the Board's Board_Owner or a BoardMember. A Supervisor who is neither owner nor BoardMember has no Board_Staff_Access, even on a public Board. Board_Access remains the read-access term and is also the access a Member needs (as BoardMember on a private Board).
- **Column**: An ordered list within a Board that contains Cards.
- **Default_Columns**: The five Columns `Todo`, `In Progress`, `Review`, `Revision`, `Done`, in that order, seeded on every new Board.
- **Card**: A unit of work with a title, description, priority, optional start and end dates, optional Category, optional assignee, Subtasks, and Attachments.
- **Assigned_Member**: The user referenced by a Card's `assignee_id`.
- **Priority**: A Card attribute that is exactly one of `high`, `medium`, or `low`.
- **Subtask**: A checklist item of a Card with a title, `is_done` flag, and Float `order`. Has no assignee and no dates.
- **Attachment**: A link (`url`) or an uploaded file (`file_path` and `mime_type`) belonging to a Card. Never has both empty.
- **Signed_File_URL**: A time-limited, signature-bearing URL for an uploaded Attachment file, valid for 15 minutes.
- **Category**: A per-Board label with a name and nullable color, shown as a filter chip.
- **Comment**: A message on a Card. A top-level Comment has a null `parent_id`. A Reply has a non-null `parent_id`.
- **Reply**: A Comment whose `parent_id` references a top-level Comment.
- **Priority_Comment**: A Comment with `is_priority` set to true.
- **Reply_Count**: The denormalized `reply_count` integer on a top-level Comment.
- **Activity_Log**: The append-only `ActivityLog` table recording state-changing actions.
- **Notification**: A server-created record targeting one user, of type `assigned` or `deadline`.
- **Inbox**: The side panel listing the signed-in user's Notifications.
- **Side_Panel**: The right-side sliding panel shared by Inbox and Activity.
- **Sidebar**: The left navigation holding brand, nav (including Inbox, Activity, and Categories where permitted), the Boards list, team members, and profile.
- **Analytics_Summary**: A pre-aggregated payload of counts, deltas, and overdue totals for a Board.
- **Overdue_Card**: A non-soft-deleted Card whose `end_date` is before today and whose Column is not `Done`.
- **Envelope**: The response shape `{ "status", "message", "data" }` for success and `{ "status", "message", "error": { "code", "message" } }` for failure, where `status` is the HTTP status code as an integer and `message` is a non-empty string.
- **flask-smorest**: The Flask extension through which every blueprint declares request, query, and response marshmallow schemas and from which the OpenAPI 3 document is generated.
- **Soft_Delete**: Setting `deleted_at` on a row instead of removing the row.
- **Token**: The JWT returned by register and login, identifying the acting user and role, with a fixed 24-hour expiry.
- **APP_TIMEZONE**: The environment variable holding the application's configured server timezone.

## Decisions Log

| ID | Decision | Rationale | Where applied |
|----|----------|-----------|---------------|
| 1 | `Board.owner_id` is nullable and references the owning Supervisor. | Supervisor ownership and analytics scope need a real column. | Req 3.2, 3.16 to 3.19, 10.1, 10.2 |
| 2 | Members move and edit only Cards assigned to them. | Keeps Member authority narrow. | Req 4.8, 4.9, 5.4, 5.5 |
| 3 | The create-card action shows to Supervisor, Manager, and Admin on Manager-authored Comments. | Matches the "create from a manager's comment" workflow. | Req 7.14, 7.15 |

Note on Decision 3: Req 7.14 stands as written (viewer is a Supervisor, Manager, or Admin and the Comment's author is a Manager). The backend, product, and frontend steering documents were aligned to it.
| 4 | Board soft-delete and archive are Manager and Admin only. | Boards are records of real work. | Req 3.6, 3.7, 11.8, 11.9 |
| 5 | Admin permission set: view all, manage users and Boards, create and delete Cards, create Columns; no Comments or priority flags. | Defines the Admin track. | Req 2.4 to 2.6 |
| A | Private Boards require Board_Access (owner, BoardMember, Manager, or Admin). Public Boards stay readable by every signed-in user. | "Private" must gate unrelated signed-in users, not only Guests. Interpretation: the request's wording omitted "private", but the stated problem concerns private Boards, so public Boards remain open to signed-in users. **Pending confirmation by the product owner.** | Req 3.4, 3.11 to 3.19, 4, 5, 6, 7, 8, 11.2, 11.6, 11.11, 11.12, 12 |

Clarification to Decision A (V2): Req 3.4 and 11.2 grant Supervisor writes only as owner or BoardMember, while Req 4 and 6 said "Board_Access", which a Supervisor also holds on any public Board. That wording gap is resolved by the Board_Staff_Access term (Glossary). Supervisor, Manager, and Admin writes (Card create, delete, archive, assign, unassign, edit, move; Subtask and Attachment writes by staff; Category create, rename, delete) require Board_Staff_Access, so an unrelated Supervisor cannot write on a public Board. Members keep Board_Access plus the assignee rule (Decision 2). Reads and Comments keep Board_Access.
| B | Admin is deliberately excluded from commenting and priority flagging (Req 2.5) and from analytics (Req 10.4). Admin is a separate administration track, not a superset of Manager. This is a recorded decision, not an oversight. Future editors must not "fix" it. | Changing it would quietly alter the permission model. | Req 2.5, Req 2 note, 7.3, 10.4 |
| C | One unified `login_identifier` field replaces separate email and username. Uniqueness and login matching are case-insensitive. | One column means one uniqueness check and one login lookup. | Req 1.1 to 1.5, 1.17, Glossary |
| D | Uploaded Attachment files are access-gated through an authenticated endpoint or a Signed_File_URL. No permanent public URL. | A permanent public URL bypasses Board_Access and role checks. | Req 4.18, 4.19, 4.24 to 4.27 |
| E | Every response carries top-level `status` (HTTP status integer) and `message`; the Backend uses flask-smorest with marshmallow schemas, validation failures stay HTTP 400 `VALIDATION_ERROR` (not 422), and the OpenAPI document is generated instead of hand-written. | One declaration per endpoint drives validation, serialization, and documentation, so they cannot drift; the body alone states the outcome. | Req 13.2 to 13.4, 13.11 to 13.15, 17 |
| F | Models declare SQLAlchemy relationships only for real cross-table reads (`Board.columns`, `Board.members`, `Card.subtasks`, `Card.attachments`, `Comment.replies`), each with `back_populates` (not `backref`), `lazy="raise"`, and no cascade delete. Repositories load related rows explicitly with `selectinload` or `joinedload`. Models have no `to_dict`; marshmallow schemas serialize, because output depends on the viewer. | An accidental lazy load fails loudly instead of becoming a hidden N+1 query, and viewer-dependent serialization stays in one place. | Req 13.16 to 13.18, 14.12, 15.8, 15.9 |

Notes on status codes: V2 standardizes "no Token returns 401; valid Token with insufficient role or access returns 403". This changes Req 11.5 (a Guest requesting a private Board) from 403 in V1 to 401 in V2. Guests may still read public Boards without a Token.

## Open Questions

1. **login_identifier format validation:** Should a login_identifier be email-shaped, username-shaped, or an arbitrary string? Not decided. Provisional V2 behavior: trim, non-empty, maximum 255 characters, case-insensitive uniqueness, no further format validation, until the product owner decides.
2. **Attachment delivery cost:** Signed time-limited URLs or an authenticated proxy cost more to implement than a public URL. Flagged for the timeline and estimate owner.
3. **Decision A interpretation:** Confirm that public Boards stay readable by every signed-in user (see Decisions Log).
4. **Swagger UI assets from a CDN:** Under flask-smorest, Swagger UI loads its assets from a CDN by default. This is acceptable in development and testing, where the docs routes exist. Flag if offline documentation is required.

## Requirements

### Requirement 1: Authentication and Accounts

**User Story:** As a visitor, I want to register and sign in with an email or username and password, so that I can access boards according to my role.

#### Acceptance Criteria

1. WHEN a visitor submits a registration with full name, login_identifier, and password, THE Backend SHALL create a user account with a hashed password and return `{ "status": 201, "message": "...", "data": { "user": { id, full_name, login_identifier, avatar_url }, "token": "..." } }` (Decisions C and E).
2. WHEN a registered user submits a valid login_identifier and password to login, THE Backend SHALL return the same `user` and `token` shape as registration, matching the login_identifier case-insensitively (Decision C).
3. IF login credentials are invalid, THEN THE Backend SHALL return HTTP 401 with an error Envelope.
4. IF a registration uses a login_identifier that already exists when compared case-insensitively, THEN THE Backend SHALL return HTTP 409 with an error Envelope (Decision C).
5. IF a registration omits full name, login_identifier, or password, or the login_identifier is empty after trimming, or longer than 255 characters, THEN THE Backend SHALL return HTTP 400 with the code `VALIDATION_ERROR` (Decision C).
6. THE Backend SHALL store the user's `avatar_url` as nullable.
7. WHEN an Admin creates, edits, or assigns a role to a user account, THE Backend SHALL apply the change and record it in the Activity_Log.
8. IF an authenticated user who is not an Admin requests user account management, THEN THE Backend SHALL return HTTP 403, or HTTP 401 when no Token is present.
9. THE Frontend SHALL present the login and register pages as a split-panel layout with a brand panel beside an elevated rounded form card on desktop widths.
10. WHILE the viewport is at mobile width, THE Frontend SHALL hide the brand panel on the login and register pages and show only the form.
11. THE System SHALL exclude Google OAuth login from V2 until login_identifier and password authentication is verified end-to-end.
12. IF a registration password is shorter than 8 characters, THEN THE Backend SHALL return HTTP 400 with the code `VALIDATION_ERROR`.
13. THE Backend SHALL hash passwords with bcrypt or argon2.
14. WHEN the Backend issues a Token, THE Backend SHALL set a fixed expiry of 24 hours and keep no server-side revocation list.
15. WHEN a user calls `POST /api/auth/logout`, THE Backend SHALL return `{ "status": 200, "message": "...", "data": null }`.
16. WHEN a user logs out, THE Frontend SHALL discard the stored Token, and the issued Token SHALL remain valid until its expiry.
17. THE Backend SHALL apply no login_identifier format validation beyond trimming, a non-empty value, a maximum of 255 characters, and case-insensitive uniqueness (provisional, see Open Question 1).
18. THE System SHALL defer rate limiting past the MVP.

### Requirement 2: Roles and Permissions

**User Story:** As a system owner, I want strictly layered roles enforced on the server, so that each user can reach only the actions their role allows.

Note (Decision B): Admin is a separate administration track and is deliberately not a superset of Manager. The Admin exclusions in criteria 5 and in Requirement 10 criterion 4 are intentional and must not be changed as a "fix".

#### Acceptance Criteria

1. THE Backend SHALL support exactly five roles: guest, member, supervisor, manager, and admin.
2. THE Backend SHALL treat Manager permissions as a superset of Supervisor permissions, Supervisor permissions as a superset of Member permissions, and Member view access as a superset of Guest view access.
3. THE Backend SHALL treat Admin as a separate administration track with the permissions listed in criteria 4 to 6.
4. THE Backend SHALL permit an Admin to view all Boards, Cards, Comments, and Activity_Log entries, manage user accounts, create and assign Boards, archive and Soft_Delete Boards, set Board visibility, manage Categories, and move and edit any Card (Decision 5).
5. THE Backend SHALL deny an Admin the actions of creating a Comment and flagging a Comment as priority (Decision B).
6. THE Backend SHALL permit an Admin to create Cards, delete Cards, archive Cards, and create Columns.
7. WHEN any mutating endpoint is called, THE Backend SHALL determine the acting role from the Token and ignore any role value in the request body.
8. IF a mutating request has no valid Token, THEN THE Backend SHALL return HTTP 401 with an error Envelope.
9. IF an authenticated user calls a mutating endpoint that the user's role or Board_Access does not permit, THEN THE Backend SHALL return HTTP 403 with an error Envelope.
10. THE Backend SHALL re-validate the caller's role on 100 percent of mutating endpoints.

### Requirement 3: Boards and Columns

**User Story:** As a Manager or Admin, I want to create boards and assign them to supervisors, so that each project has an owner and a consistent workflow.

#### Acceptance Criteria

1. WHEN a Manager or Admin creates a Board, THE Backend SHALL insert the Board and the five Default_Columns with `order` values 0 to 4 in that sequence, in a single transaction.
2. WHEN a Manager or Admin assigns a Board to a Supervisor, THE Backend SHALL store that Supervisor's id in the Board's nullable `owner_id` (Decision 1).
3. IF an authenticated Member or Supervisor attempts to create a Board, THEN THE Backend SHALL return HTTP 403, or HTTP 401 when no Token is present.
4. WHEN a Manager or Admin, or a Supervisor who is the Board_Owner or a BoardMember of the Board, creates a Column on that Board, THE Backend SHALL append the Column with the next `order` value (Decision A).
5. IF an authenticated Member, or a Supervisor without Board_Access as owner or BoardMember, attempts to create a Column, THEN THE Backend SHALL return HTTP 403, or HTTP 401 when no Token is present (Decision A).
6. WHEN a Manager or Admin soft-deletes a Board, THE Backend SHALL set the Board's `deleted_at` and exclude the Board from default queries (Decision 4).
7. IF an authenticated Member or Supervisor attempts to soft-delete a Board, THEN THE Backend SHALL return HTTP 403, or HTTP 401 when no Token is present (Decision 4).
8. THE Backend SHALL never hard-delete a row from the Board table.
9. THE Frontend SHALL list the Boards the viewer may see in the Sidebar and use that list as the Board switcher.
10. WHILE a Board is open, THE Frontend SHALL render the Board's Columns and Cards in the main area.
11. WHEN the Board_Owner, a Manager, or an Admin adds a user to a Board through `POST /api/boards/{id}/members`, THE Backend SHALL create a BoardMember for that Board and user (Decision A).
12. IF an authenticated user who is not the Board_Owner, a Manager, or an Admin attempts to add or remove a BoardMember, THEN THE Backend SHALL return HTTP 403, or HTTP 401 when no Token is present (Decision A).
13. IF a BoardMember add targets a user who is already a BoardMember of that Board, THEN THE Backend SHALL return HTTP 409 with an error Envelope (Decision A).
14. WHEN the Board_Owner, a Manager, or an Admin removes a BoardMember through `DELETE /api/boards/{id}/members/{user_id}`, THE Backend SHALL delete that BoardMember record (Decision A).
15. WHEN a BoardMember is added or removed, THE Backend SHALL write one Activity_Log row for the change in the same transaction (Decision A).
16. WHEN a Manager or Admin reassigns a Board's `owner_id` to a user who has the supervisor role, THE Backend SHALL store the new `owner_id` (Decision 1).
17. IF a Board `owner_id` reassignment names a user who does not have the supervisor role, THEN THE Backend SHALL return HTTP 400 with the code `VALIDATION_ERROR`.
18. WHEN a Manager or Admin clears a Board's `owner_id`, THE Backend SHALL set `owner_id` to null.
19. WHEN a Board's `owner_id` is reassigned or cleared, THE Backend SHALL write one Activity_Log row in the same transaction.

### Requirement 4: Cards

**User Story:** As a team member, I want cards with description, subtasks, priority, dates, and attachments, so that I can capture and track a piece of work in one place.

#### Acceptance Criteria

1. WHEN a Card_Creator with Board_Staff_Access to a Board creates a Card in a Column of that Board, THE Backend SHALL store the Card with a title, a description, a Priority of `high`, `medium`, or `low`, a Float `order`, and nullable `start_date`, `end_date`, `category_id`, and `assignee_id` (Decision A).
2. IF a Card is submitted with a Priority other than `high`, `medium`, or `low`, THEN THE Backend SHALL return HTTP 400 with the code `VALIDATION_ERROR`.
3. IF a Card is submitted with an `end_date` earlier than its `start_date`, THEN THE Backend SHALL return HTTP 400 with the code `VALIDATION_ERROR`.
4. IF an authenticated user who is not a Card_Creator with Board_Staff_Access attempts to create a Card, THEN THE Backend SHALL return HTTP 403, or HTTP 401 when no Token is present (Decision A).
5. WHEN a Card_Creator with Board_Staff_Access deletes a Card, THE Backend SHALL Soft_Delete the Card by setting `deleted_at`.
6. WHEN a Card_Creator with Board_Staff_Access archives a Card, THE Backend SHALL set the Card's `archived_at` and allow the archive to be reversed.
7. IF an authenticated Member attempts to create, delete, or archive a Card, THEN THE Backend SHALL return HTTP 403, or HTTP 401 when no Token is present.
8. WHEN a Member with Board_Access edits a Card assigned to that Member, THE Backend SHALL apply the edit (Decisions 2 and A).
9. IF a Member edits a Card whose `assignee_id` is not that Member, THEN THE Backend SHALL return HTTP 403 (Decision 2).
10. WHEN a Supervisor, Manager, or Admin with Board_Staff_Access to the Card's Board edits any Card on that Board, THE Backend SHALL apply the edit (Decision A).
11. WHEN a Supervisor, Manager, or Admin with Board_Staff_Access assigns a Card to a user, THE Backend SHALL set the Card's `assignee_id` and create an `assigned` Notification for that user in the same transaction.
12. WHEN a user with edit rights on a Card (Board_Staff_Access for a Supervisor, Manager, or Admin; Board_Access as the Assigned_Member for a Member) adds a Subtask to that Card, THE Backend SHALL store the Subtask with a title, `is_done` defaulting to false, and a Float `order`.
13. WHEN a user with edit rights on a Card toggles a Subtask's `is_done` or reorders it, THE Backend SHALL persist the change through `PATCH /api/subtasks/{id}`, setting a Subtask dropped between two siblings to the average of their `order` values, the first position to `min_order - 1`, the last position to `max_order + 1`, an empty checklist's first Subtask to 1.0, and renumbering the whole checklist as 1.0, 2.0, ... in the same transaction when the gap between adjacent `order` values falls below 1e-6.
14. WHEN a user with edit rights on a Card (Board_Staff_Access for a Supervisor, Manager, or Admin; Board_Access as the Assigned_Member for a Member) deletes a Subtask, THE Backend SHALL remove the Subtask through `DELETE /api/subtasks/{id}`.
15. WHEN a user with edit rights on a Card (Board_Staff_Access for a Supervisor, Manager, or Admin; Board_Access as the Assigned_Member for a Member) adds an Attachment, THE Backend SHALL store either a `url` or a `file_path` with `mime_type`.
16. IF an Attachment has neither a `url` nor a `file_path`, THEN THE Backend SHALL return HTTP 400 with the code `VALIDATION_ERROR`.
17. IF an uploaded Attachment file type is not PDF, Word, or RAR, THEN THE Backend SHALL return HTTP 400 with the code `VALIDATION_ERROR`.
18. THE Backend SHALL serve each uploaded Attachment file through an authenticated endpoint or a Signed_File_URL that enforces the same Board_Access and role rules as the owning Card, and SHALL NOT expose a permanently public, unauthenticated URL (Decision D).
19. WHEN a user clicks an Attachment, THE Frontend SHALL open it with `target="_blank"` and `rel="noopener noreferrer"` and provide no in-app preview, and for a file Attachment whose Signed_File_URL has expired, THE Frontend SHALL request a fresh URL from `GET /api/attachments/{id}/url` before opening it (Decision D).
20. WHEN a user opens a Card, THE Frontend SHALL show one two-pane modal used for both viewing and editing, with title, description, Priority, dates, Attachments, the Subtask checklist, and the Card's Activity_Log in the left pane and the Comment thread and composer in the right pane.
21. WHEN a user saves the left pane, THE Frontend SHALL commit the Card changes without closing the modal and without affecting the Comment composer.
22. THE Frontend SHALL render the Subtask checklist as a flat list of checkboxes with inline-editable titles and a drag handle for reordering.
23. THE Backend SHALL never hard-delete a row from the Card table.
24. THE Backend SHALL set each Signed_File_URL to expire 15 minutes after issue (Decision D).
25. IF a request to the file route carries a bad, modified, or expired file signature, THEN THE Backend SHALL return HTTP 403, because the file route takes no Token (Decision D).
26. WHEN a viewer with Board_Access to the Card, including a Guest on a public Board, requests `GET /api/attachments/{id}/url`, THE Backend SHALL return a fresh Signed_File_URL (Decision D).
27. THE Backend SHALL return a link-type Attachment's `url` as stored (Decision D).
28. WHEN a Supervisor, Manager, or Admin with Board_Staff_Access sets a Card's `assignee_id` to null, THE Backend SHALL clear the assignment, write one `card.unassigned` Activity_Log row in the same transaction, and create no Notification.
29. THE Backend SHALL carry no `deleted_at` on Subtask, Attachment, or Comment rows and SHALL hide them by joining the parent Card's `deleted_at`.

### Requirement 5: Drag-and-Drop Card Movement

**User Story:** As a team member, I want to drag cards between columns, so that a card's new position persists after a page refresh.

#### Acceptance Criteria

1. WHEN a user drops a Card between two siblings with `order` values a and b, THE Backend SHALL set the moved Card's Float `order` to the average of a and b without rewriting sibling rows, except for the renumbering defined in criterion 11.
2. WHEN a user drops a Card, THE Frontend SHALL call `PATCH /api/cards/{id}/move` with the target Column and computed Float `order` on `dragend` and reconcile local state with the response.
3. WHEN a drag is in progress, THE Frontend SHALL insert a placeholder at the drop target and animate sibling Cards into place with a FLIP transform.
4. WHEN a Member with Board_Access moves a Card assigned to that Member, THE Backend SHALL apply the move (Decisions 2 and A).
5. IF a Member moves a Card whose `assignee_id` is not that Member, THEN THE Backend SHALL return HTTP 403 (Decision 2).
6. WHEN a Supervisor, Manager, or Admin with Board_Staff_Access to the Card's Board moves any Card on that Board, THE Backend SHALL apply the move (Decision A).
7. IF a request to move a Card carries no Token, THEN THE Backend SHALL return HTTP 401.
8. WHEN a Card move succeeds, THE Backend SHALL write exactly one Activity_Log row with action `card.moved` and the source and target Column in the same transaction.
9. WHEN a page is refreshed after a successful move, THE Frontend SHALL render the Card in the moved position.
10. WHEN a user drops a Card at the first position of a Column, THE Backend SHALL set the Card's `order` to `min_order - 1`, WHEN at the last position, to `max_order + 1`, and WHEN into an empty Column, to 1.0.
11. IF the gap between two adjacent `order` values in a Column falls below 1e-6, THEN THE Backend SHALL renumber that whole Column as 1.0, 2.0, ... in the same transaction as the move.
12. IF the target Column's `board_id` does not match the Card's current `board_id`, THEN THE Backend SHALL return HTTP 400 with the code `VALIDATION_ERROR`.

### Requirement 6: Categories

**User Story:** As a Supervisor, Manager, or Admin, I want to manage each board's own categories, so that viewers can filter cards by the kinds of work that board runs.

#### Acceptance Criteria

1. WHEN a Manager, an Admin, or a Supervisor with Board_Staff_Access creates a Category on a Board, THE Backend SHALL store the Category with the Board's id, a name, and a nullable color (Decision A).
2. WHEN a Manager, an Admin, or a Supervisor with Board_Staff_Access renames or recolors a Category, THE Backend SHALL apply the change through `PATCH /api/categories/{id}`.
3. WHEN a Manager, an Admin, or a Supervisor with Board_Staff_Access deletes a Category, THE Backend SHALL remove it through `DELETE /api/categories/{id}`.
4. IF an authenticated Member, or a Supervisor without Board_Staff_Access, attempts to create, edit, or delete a Category, THEN THE Backend SHALL return HTTP 403, or HTTP 401 when no Token is present.
5. WHEN a user with Board_Access to a Board requests `GET /api/boards/{board_id}/categories`, THE Backend SHALL return that Board's Categories without a role check (Decision A).
6. WHEN a Guest requests the Categories of a public Board, THE Backend SHALL return them.
7. THE Backend SHALL return only the Categories owned by the requested Board.
8. WHEN a Board is soft-deleted, THE Backend SHALL keep that Board's Categories stored and make them unreachable.
9. THE Frontend SHALL render the Board's filter-row chips from the `GET /api/boards/{board_id}/categories` response and use no hard-coded chip list.
10. WHEN the viewer switches Boards, THE Frontend SHALL re-fetch and re-render the filter-row chips.
11. WHERE the viewer is a Supervisor, Manager, or Admin, THE Frontend SHALL show a Categories entry in the Sidebar that opens an add, rename, recolor, and delete screen scoped to the current Board.
12. IF a Category create or rename uses a name that already exists on the same Board when compared case-insensitively, THEN THE Backend SHALL return HTTP 409 with the code `CONFLICT`.

### Requirement 7: Comments

**User Story:** As a team member, I want threaded comments with manager priority flags, so that important discussion stays on top and managers can turn their own comments into cards.

#### Acceptance Criteria

1. WHEN a Member, Supervisor, or Manager posts to `POST /api/cards/{id}/comments` on a Card whose Board the user has Board_Access to, THE Backend SHALL create a top-level Comment (Decision A).
2. IF a Comment body is missing or empty, THEN THE Backend SHALL return HTTP 400 with the code `VALIDATION_ERROR` and the message `content is required` in both `message` and `error.message` (Decision E).
3. IF an authenticated Admin attempts to create a Comment, THEN THE Backend SHALL return HTTP 403, and IF no Token is present, THEN THE Backend SHALL return HTTP 401 (Decision B).
4. WHEN a Member, Supervisor, or Manager with Board_Access to the Card's Board posts to `POST /api/comments/{id}/replies` targeting a top-level Comment, THE Backend SHALL create the Reply and increment the parent's Reply_Count in the same transaction (Decision A).
5. IF the target of a reply request has a non-null `parent_id`, THEN THE Backend SHALL return HTTP 400.
6. THE Backend SHALL provide no like or vote endpoint in the comments domain.
7. WHEN a Manager calls `PATCH /api/comments/{id}/priority` on any Comment, THE Backend SHALL toggle that Comment's `is_priority`.
8. IF an authenticated user who is not a Manager calls `PATCH /api/comments/{id}/priority`, THEN THE Backend SHALL return HTTP 403, or HTTP 401 when no Token is present.
9. WHEN `GET /api/cards/{id}/comments` is called, THE Backend SHALL return Priority_Comments first, ordered newest priority first, followed by the remaining top-level Comments in the requested order.
10. WHEN the `sort` parameter is `latest` or omitted, THE Backend SHALL order the remaining top-level Comments newest first.
11. WHEN the `sort` parameter is `popular`, THE Backend SHALL order the remaining top-level Comments by Reply_Count descending, with ties broken by `created_at` descending.
12. THE Backend SHALL return each top-level Comment's Replies nested inline, ordered oldest first, regardless of the `sort` parameter.
13. THE Backend SHALL include `reply_count`, `is_priority`, and `can_create_card` on every returned Comment.
14. WHEN the viewer is a Supervisor, Manager, or Admin and the Comment's author role is manager, THE Backend SHALL set `can_create_card` to true regardless of `is_priority` (Decision 3).
15. IF the viewer is a Member or Guest, or the Comment's author role is not manager, THEN THE Backend SHALL set `can_create_card` to false (Decision 3).
16. IF a Guest calls a comment endpoint, THEN THE Backend SHALL return HTTP 403 when the Board is public and HTTP 401 when the Board is private, and SHALL return no `comments` field in either case.
17. THE Frontend SHALL render Priority_Comments first with a priority indicator, then the remaining top-level Comments under a visible Latest and Popular toggle that shows the Reply_Count as a badge.
18. THE Frontend SHALL show a Reply action only on top-level Comments.
19. WHERE `can_create_card` is true on a Comment, THE Frontend SHALL show the "create new card" action on that Comment.
20. WHERE the Card response omits `comments`, THE Frontend SHALL omit the Comment thread.

### Requirement 8: Activity Log

**User Story:** As a team member, I want an append-only history of what happened on a card and a board, so that I can trust the record of changes.

#### Acceptance Criteria

1. WHEN a state-changing action succeeds, THE Backend SHALL insert exactly one Activity_Log row with `actor_id`, `action`, `target_type`, `target_id`, `metadata`, and `created_at` in the same transaction as the change.
2. THE Backend SHALL never update or delete an Activity_Log row after insertion.
3. WHEN a signed-in user with Board_Access to a Card's Board requests the Card's activity, THE Backend SHALL return the rows where `target_type` is `card` and `target_id` is that Card's id (Decision A).
4. WHEN a signed-in user with Board_Access to a Board requests the Board's activity feed, THE Backend SHALL return every row for the Cards and Columns belonging to that Board (Decision A).
5. IF a Guest requests Card activity or a Board activity feed, THEN THE Backend SHALL return no `activity` or `activity_log` field, including on direct calls and when the field is requested explicitly.
6. WHEN a user opens Activity from the Sidebar nav, THE Frontend SHALL open the Side_Panel on the Activity view.
7. WHERE the Card response omits `activity`, THE Frontend SHALL omit the Card activity section.

### Requirement 9: Notifications and Inbox

**User Story:** As a member, I want to be notified when a card is assigned to me or reaches its deadline, so that I do not miss work.

#### Acceptance Criteria

1. WHEN a Card is assigned to a user, THE Backend SHALL insert a Notification of type `assigned` for that user in the same transaction as the assignment.
2. WHEN the scheduled daily job runs, THE Backend SHALL create one `deadline` Notification for the Assigned_Member of each Card whose `end_date` equals today in the APP_TIMEZONE timezone and whose `deleted_at` is null, using no per-user timezone.
3. WHEN the scheduled daily job runs more than once on the same date, THE Backend SHALL create no duplicate `deadline` Notification for the same Card and assignee.
4. THE Backend SHALL create Notifications on the server and the Frontend SHALL not compute or poll them client-side.
5. WHEN a signed-in user requests the Inbox, THE Backend SHALL return only that user's Notifications and an unread count that reflects read-marking through criteria 8 and 9.
6. WHEN a user clicks Inbox in the Sidebar or clicks the header bell, THE Frontend SHALL open the Side_Panel on the Inbox view through the same toggle.
7. WHERE the API response omits Inbox data, THE Frontend SHALL omit the Inbox panel.
8. WHEN a signed-in user calls `PATCH /api/notifications/{id}/read` on one of the user's own Notifications, THE Backend SHALL mark that Notification read.
9. WHEN a signed-in user calls `PATCH /api/notifications/read-all`, THE Backend SHALL mark all of that user's own Notifications read.
10. IF a user calls `PATCH /api/notifications/{id}/read` on another user's Notification, THEN THE Backend SHALL return HTTP 404.

### Requirement 10: Analytics

**User Story:** As a Supervisor or Manager, I want pre-aggregated board analytics, so that I can judge progress without opening every board.

#### Acceptance Criteria

1. WHEN a Supervisor requests `GET /api/boards/{id}/analytics` for a Board whose `owner_id` is that Supervisor, THE Backend SHALL return an Analytics_Summary (Decision 1).
2. IF a Supervisor requests analytics for a Board whose `owner_id` is not that Supervisor, including a Board where that Supervisor is a BoardMember, THEN THE Backend SHALL return HTTP 403.
3. WHEN a Manager requests analytics for any Board, THE Backend SHALL return an Analytics_Summary.
4. IF an authenticated Member or Admin requests analytics, THEN THE Backend SHALL return HTTP 403, and IF no Token is present, THEN THE Backend SHALL return HTTP 401 (Decision B, intentional).
5. THE Backend SHALL return Analytics_Summary payloads of counts, deltas, and overdue totals, such as `{ "status": 200, "message": "...", "data": { "done": 12, "in_progress": 4, "overdue": 2 } }`, counting an Overdue_Card as a Card whose `end_date` is before today, whose Column is not `Done`, and which is not soft-deleted, and never a raw dump of every Card.
6. WHEN a Manager requests cross-board analytics, THE Backend SHALL return one Analytics_Summary per Board in a single pre-aggregated response.
7. THE Backend SHALL grant a Supervisor analytics access only through Board ownership and never through BoardMember (Decision A).

### Requirement 11: Board Visibility and Archiving

**User Story:** As a Supervisor, Manager, or Admin, I want to control board visibility and archive boards and cards, so that guests see only what is intended and finished work stays recoverable.

#### Acceptance Criteria

1. THE Backend SHALL store each Board's `visibility` as exactly `public` or `private`.
2. WHEN a Manager, an Admin, or a Supervisor who is the Board_Owner or a BoardMember sets a Board's visibility, THE Backend SHALL apply the change and record it in the Activity_Log (Decision A).
3. IF an authenticated Member, or a Supervisor who is neither owner nor BoardMember, attempts to set Board visibility, THEN THE Backend SHALL return HTTP 403, or HTTP 401 when no Token is present.
4. WHEN a Guest requests the Board list, THE Backend SHALL return only Boards where `visibility` is `public` and `deleted_at` is null.
5. IF a Guest requests a private Board, THEN THE Backend SHALL return HTTP 401 with an error Envelope.
6. WHEN a signed-in Member requests a private Board where the Member is neither the Board's owner, a BoardMember, a Manager, nor an Admin, THE Backend SHALL return HTTP 403 (Decision A).
7. WHEN a Guest requests a public Board, THE Backend SHALL return its Columns and Cards and omit `comments` and `activity_log`.
8. WHEN a Manager or Admin archives a Board, THE Backend SHALL set the Board's `archived_at` and allow the archive to be reversed (Decision 4).
9. IF an authenticated Member or Supervisor attempts to archive a Board, THEN THE Backend SHALL return HTTP 403, or HTTP 401 when no Token is present (Decision 4).
10. WHEN a Supervisor, Manager, or Admin with Board_Staff_Access archives a Card, THE Backend SHALL set the Card's `archived_at`.
11. IF a signed-in Supervisor who is neither the Board_Owner nor a BoardMember requests a private Board, THEN THE Backend SHALL return HTTP 403 (Decision A).
12. WHEN a signed-in user requests the Board list, THE Backend SHALL return the public non-deleted Boards plus the non-deleted Boards to which the user has Board_Access (Decision A).

### Requirement 12: Search and Filter

**User Story:** As a user viewing a board, I want to search and filter its cards, so that I can find work quickly.

#### Acceptance Criteria

1. WHEN a user with Board_Access calls `GET /api/boards/{id}/cards` with `search=<text>`, THE Backend SHALL return only Cards on that Board whose title or description contains the search value as a case-insensitive substring.
2. WHEN a user with Board_Access calls `GET /api/boards/{id}/cards` with `filter[priority]`, `filter[assignee]`, or `filter[category]`, THE Backend SHALL return only Cards matching every supplied filter.
3. THE Backend SHALL exclude Soft_Deleted Cards from search and filter results.
4. IF a filter field is not supported, THEN THE Backend SHALL return HTTP 400 with the code `VALIDATION_ERROR`.
5. WHEN a user selects a Category chip, THE Frontend SHALL request the Board's Cards with the matching category filter.
6. WHEN a Guest searches a public Board, THE Backend SHALL return Card data only and no Comment or Activity_Log fields.
7. IF a signed-in user without Board_Access calls the Cards endpoint of a private Board, THEN THE Backend SHALL return HTTP 403, and IF a Guest does so, THEN THE Backend SHALL return HTTP 401 (Decision A).

### Requirement 13: API Conventions and Data Integrity

**User Story:** As a frontend developer, I want one predictable API shape and consistent data rules, so that the client has a single place to unwrap responses and errors.

#### Acceptance Criteria

1. THE Backend SHALL serve all endpoints under `/api/...` without a version segment.
2. WHEN a request succeeds, THE Backend SHALL return `{ "status": <HTTP status integer>, "message": <non-empty string>, "data": <payload> }` with the payload as an object, a list, or null (Decision E).
3. IF a request fails, THEN THE Backend SHALL return `{ "status": <HTTP status integer>, "message": <non-empty string>, "error": { "code": string, "message": string } }` with the matching HTTP status of 400, 401, 403, 404, 405, 409, or 500, and `error.message` equal to the top-level `message` (Decision E).
4. THE Backend SHALL return the Envelope shape, including `status` and `message`, on every response except the Swagger UI HTML page, the raw OpenAPI document, and the successful file bytes of the signed file route; error responses of the signed file route SHALL still use the Envelope (Decision E).
5. THE Backend SHALL use a UUID primary key on every entity and include `created_at` and `updated_at` on every entity.
6. THE Backend SHALL include `deleted_at` and `archived_at` on Board and Card.
7. THE Backend SHALL access the database only through each blueprint's own `repository.py`.
8. THE Backend SHALL read CORS origins from an environment variable allow-list and never use the wildcard `*`.
9. THE System SHALL provide a `.env.example` for the Backend and the Frontend and commit no real `.env` file.
10. IF a request carries no Token on an endpoint that requires one, THEN THE Backend SHALL return HTTP 401, and IF a valid Token lacks the required role or Board_Access, THEN THE Backend SHALL return HTTP 403, except that Guests may read public Boards without a Token.
11. THE Backend SHALL set the Envelope `status` equal to the HTTP status code of the response on every Envelope response, including 401, 403, 404, 405, 409, and 500 responses and the errors of the signed file route, with the exceptions of the Swagger UI HTML page, the raw OpenAPI document, and the successful file bytes of the signed file route, which carry no Envelope (Decision E).
12. THE Backend SHALL use flask-smorest, registering every blueprint on one `Api` instance, and SHALL declare request bodies, query arguments, and responses of every endpoint with marshmallow schemas (Decision E).
13. IF request body or query validation fails, THEN THE Backend SHALL return HTTP 400 with the code `VALIDATION_ERROR` and the Envelope error shape, and SHALL NOT return HTTP 422 (Decision E).
14. THE Backend SHALL keep each blueprint layered `routes.py → service.py → repository.py` with the marshmallow schemas in `schema.py` (Decision E).
15. THE Backend SHALL declare each success response with a schema that wraps the blueprint's payload schema in the Envelope (Decision E).
16. THE Backend SHALL declare the SQLAlchemy relationships `Board.columns`, `Board.members`, `Card.subtasks`, `Card.attachments`, and `Comment.replies`, each paired with its inverse through `back_populates`, declared with `lazy="raise"`, and without a delete cascade (Decision F).
17. THE Backend SHALL define no `to_dict` or other serialization method on any model (Decision F).
18. THE Backend SHALL ensure that services and schemas trigger no lazy load, by having each repository load the related rows it returns with `selectinload` or `joinedload` (Decision F).

### Requirement 14: Non-Functional Quality

**User Story:** As a product owner, I want measurable performance, security, and mobile usability targets, so that quality can be verified.

#### Acceptance Criteria

1. WHILE the Backend is under normal load, THE Backend SHALL respond within 300 ms at the 95th percentile.
2. WHEN a Board with 200 Cards loads over a throttled Fast 3G connection, THE Frontend SHALL reach first meaningful paint within 2 seconds.
3. THE Backend SHALL include no `comments` or `activity` field in any Guest-facing response, including direct calls to the comment and activity endpoints.
4. WHILE the viewport width is between 360 and 414 pixels, THE Frontend SHALL show every page without horizontal scroll or cut-off or overlapping content.
5. THE Frontend SHALL write base styles for a 360 to 414 pixel screen and add tablet and desktop layouts through `min-width` media queries.
6. WHILE the viewport is below 960 pixels, THE Frontend SHALL show the Sidebar as an off-canvas drawer behind a scrim with its toggle in a persistent header.
7. WHILE the viewport is 960 pixels or wider, THE Frontend SHALL keep the Sidebar visible.
8. THE Frontend SHALL place each primary action (add card, open Inbox, switch Board) within a persistent header or the bottom third of the screen on mobile.
9. THE Frontend SHALL use the prototype's CSS custom properties for all colors, spacing, and radii and no hard-coded hex or pixel values.
10. THE Frontend SHALL build shared buttons, badges, and modals only as `BaseButton`, `BaseBadge`, and `BaseModal` in `components/shared/`.
11. THE Frontend SHALL render components as Server Components unless a component needs state, an event handler, or a browser API.
12. WHEN a list endpoint returns rows, THE Backend SHALL execute a number of database queries that does not depend on the number of returned rows, so that the board cards list with Subtasks and Attachments loads in at most a fixed number of queries instead of one query per Card (Decision F).

### Requirement 15: Automated Testing

**User Story:** As a developer, I want automated tests for the API and the main user journey, so that regressions are caught.

#### Acceptance Criteria

1. THE System SHALL include `pytest` tests for comment creation covering success, validation failure, unauthenticated, and unauthorized cases.
2. THE System SHALL include a Playwright end-to-end test of the Kanban journey that runs against the deployed URL.
3. THE System SHALL contain no `waitForTimeout` call in any Playwright test file.
4. THE System SHALL unit-test each `service.py` against a fake repository without a real database.
5. THE System SHALL include `pytest` tests covering the HTTP 401 (no Token) and HTTP 403 (insufficient role or access) cases for every mutating endpoint.
6. THE System SHALL include a `pytest` test that an unrelated Member receives HTTP 403 on a private Board (Decision A).
7. THE System SHALL include `pytest` tests for Attachment access covering a permitted viewer, an unrelated Member, a Guest on a private Board, and an expired signature (Decision D).
8. THE System SHALL include a `pytest` test that counts the database queries of the board cards list with 5 Cards and with 50 Cards, each with Subtasks and Attachments, and asserts that the two counts are equal (Decision F).
9. THE System SHALL include a `pytest` test that asserts accessing an unloaded relationship raises an error (Decision F).

### Requirement 16: Stretch Features

**User Story:** As a product owner, I want the prototype's extra card features tracked as stretch work, so that they do not delay the core paths.

#### Acceptance Criteria

1. WHERE the stretch features are enabled, THE Backend SHALL store a nullable 0 to 10 integer `progress` and an integer `views_count` defaulting to 0 on Card.
2. WHERE the stretch features are enabled, THE Frontend SHALL show the per-card progress meter, views counter, and the decorative Overview, Notes, and Questions tabs as in the prototype.
3. THE System SHALL build the stretch features only after Requirements 1 to 15 work end-to-end.

### Requirement 17: API Documentation

**User Story:** As a frontend developer and reviewer, I want a generated OpenAPI document, an interactive Swagger page, and a written API reference, so that I can learn every endpoint without reading the backend code, while the public production server exposes no extra surface.

#### Acceptance Criteria

1. THE Backend SHALL generate its OpenAPI 3 document with flask-smorest, describing every registered `/api` route with its method, path, path and query parameters, request schema, Envelope response schema, Token requirement, and error responses 400, 401, 403, 404, and 409 (Decision E).
2. THE System SHALL keep a hand-written `backend/API.md` that lists the same endpoints grouped by blueprint, with the Envelope shape, the error codes, the role-to-endpoint matrix, and one example request and response for each group.
3. WHEN a developer runs `flask export-openapi`, THE Backend SHALL write the generated document to `backend/openapi.json`.
4. WHEN `APP_ENV` is `development` or `testing`, THE Backend SHALL serve Swagger UI at `/api/docs` and the generated document at `/api/openapi.json`.
5. WHEN `APP_ENV` is anything other than `development` or `testing` (including `production` and unset), THE Backend SHALL NOT register the Swagger UI route or the `/api/openapi.json` route, so both return the 404 Envelope.
6. THE Backend SHALL read `APP_ENV` from the environment, default it to `production`, list it in `backend/.env.example`, and not refuse to start when it is missing.
7. THE Backend SHALL treat the documentation routes as read-only and public, SHALL NOT return secrets, and SHALL exclude them from the 401/403 mutating-route sweep.
8. THE System SHALL include an automated test that fails when a registered `/api` route has no operation in the generated OpenAPI document.
9. THE System SHALL include an automated test that confirms the documentation routes return 404 when `APP_ENV` is `production`.
10. THE System SHALL NOT depend on a hand-written `openapi.yaml`, `flask-swagger-ui`, or `pyyaml` for documentation (Decision E).
