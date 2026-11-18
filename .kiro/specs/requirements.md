# Requirements Document

## Introduction

This document specifies the Kanban Task Management application (Version V1). It is a role-based web app with a Flask REST API backend and a mobile-first Next.js frontend. Teams run day-to-day work on boards, columns, and cards, and supervisors and managers oversee progress through analytics without opening every board.

The requirements translate decisions already recorded in `specs/project-brief.md` and the steering documents in `.kiro/steering/`. They add no new scope. Five user decisions that resolved gaps in the brief are included and marked "Decision N" where they apply.

Out of scope for V1: Google OAuth login (post-MVP, added only after email/username and password auth is verified end-to-end), custom per-board workflow templates beyond the five default columns, and subtasks with their own assignee or date. Stretch features (card `progress` meter, `views_count`, decorative Overview/Notes/Questions tabs) are covered in Requirement 16 and are built only after all other requirements work end-to-end.

This feature requires one data-model addition beyond the current `data-model.md` steering: a nullable `Board.owner_id` (Decision 1).

## Glossary

- **System**: The Kanban Task Management application, consisting of the Backend and the Frontend.
- **Backend**: The Flask REST API, organized as one blueprint per domain, each layered `routes.py → service.py → repository.py → schema.py`.
- **Frontend**: The mobile-first Next.js (App Router, TypeScript) application.
- **Guest**: A visitor without an account. Can view the columns and cards of public boards only.
- **Member**: A signed-in user with the member role.
- **Supervisor**: A signed-in user with the supervisor role. Includes everything a Member can do.
- **Manager**: A signed-in user with the manager role. Includes everything a Supervisor can do.
- **Admin**: A signed-in user with the admin role, a separate administrative track (see Requirement 2).
- **Card_Creator**: A Supervisor, Manager, or Admin.
- **Board**: A project container holding Columns, Cards, and Categories. Has `visibility` (`public` or `private`) and a nullable `owner_id`.
- **Board_Owner**: The Supervisor referenced by a Board's `owner_id`.
- **Column**: An ordered list within a Board that contains Cards.
- **Default_Columns**: The five Columns `Todo`, `In Progress`, `Review`, `Revision`, `Done`, in that order, seeded on every new Board.
- **Card**: A unit of work with a title, description, priority, optional start and end dates, optional Category, optional assignee, Subtasks, and Attachments.
- **Assigned_Member**: The user referenced by a Card's `assignee_id`.
- **Priority**: A Card attribute that is exactly one of `high`, `medium`, or `low`.
- **Subtask**: A checklist item of a Card with a title, `is_done` flag, and Float `order`. Has no assignee and no dates.
- **Attachment**: A link (`url`) or an uploaded file (`file_path` and `mime_type`) belonging to a Card. Never has both empty.
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
- **Envelope**: The response shape `{ "data": ... }` for success and `{ "error": { "code", "message" } }` for failure.
- **Soft_Delete**: Setting `deleted_at` on a row instead of removing the row.
- **Token**: The authentication token returned by register and login, identifying the acting user and role.

## Requirements

### Requirement 1: Authentication and Accounts

**User Story:** As a visitor, I want to register and sign in with an email or username and password, so that I can access boards according to my role.

#### Acceptance Criteria

1. WHEN a visitor submits a registration with full name, email or username, and password, THE Backend SHALL create a user account with a hashed password and return `{ "data": { "user": { id, full_name, email_or_username, avatar_url }, "token": "..." } }`.
2. WHEN a registered user submits valid credentials to login, THE Backend SHALL return the same `user` and `token` shape as registration.
3. IF login credentials are invalid, THEN THE Backend SHALL return HTTP 401 with an error Envelope.
4. IF a registration uses an email or username that already exists, THEN THE Backend SHALL return HTTP 409 with an error Envelope.
5. IF a registration omits full name, email or username, or password, THEN THE Backend SHALL return HTTP 400 with the code `VALIDATION_ERROR`.
6. THE Backend SHALL store the user's `avatar_url` as nullable.
7. WHEN an Admin creates, edits, or assigns a role to a user account, THE Backend SHALL apply the change and record it in the Activity_Log.
8. IF a user who is not an Admin requests user account management, THEN THE Backend SHALL return HTTP 403.
9. THE Frontend SHALL present the login and register pages as a split-panel layout with a brand panel beside an elevated rounded form card on desktop widths.
10. WHILE the viewport is at mobile width, THE Frontend SHALL hide the brand panel on the login and register pages and show only the form.
11. THE System SHALL exclude Google OAuth login from V1 until email or username and password authentication is verified end-to-end.

### Requirement 2: Roles and Permissions

**User Story:** As a system owner, I want strictly layered roles enforced on the server, so that each user can reach only the actions their role allows.

#### Acceptance Criteria

1. THE Backend SHALL support exactly five roles: guest, member, supervisor, manager, and admin.
2. THE Backend SHALL treat Manager permissions as a superset of Supervisor permissions, Supervisor permissions as a superset of Member permissions, and Member view access as a superset of Guest view access.
3. THE Backend SHALL treat Admin as a separate administration track with the permissions listed in criteria 4 to 6.
4. THE Backend SHALL permit an Admin to view all Boards, Cards, Comments, and Activity_Log entries, manage user accounts, create and assign Boards, archive and Soft_Delete Boards, set Board visibility, manage Categories, and move and edit any Card.
5. THE Backend SHALL deny an Admin the actions of creating a Comment and flagging a Comment as priority.
6. THE Backend SHALL permit an Admin to create Cards, delete Cards, archive Cards, and create Columns.
7. WHEN any mutating endpoint is called, THE Backend SHALL determine the acting role from the Token and ignore any role value in the request body.
8. IF a mutating request has no valid Token, THEN THE Backend SHALL return HTTP 401 with an error Envelope.
9. IF an authenticated user calls a mutating endpoint that the user's role does not permit, THEN THE Backend SHALL return HTTP 403 with an error Envelope.
10. THE Backend SHALL re-validate the caller's role on 100 percent of mutating endpoints.

### Requirement 3: Boards and Columns

**User Story:** As a Manager or Admin, I want to create boards and assign them to supervisors, so that each project has an owner and a consistent workflow.

#### Acceptance Criteria

1. WHEN a Manager or Admin creates a Board, THE Backend SHALL insert the Board and the five Default_Columns with `order` values 0 to 4 in that sequence, in a single transaction.
2. WHEN a Manager or Admin assigns a Board to a Supervisor, THE Backend SHALL store that Supervisor's id in the Board's nullable `owner_id`.
3. IF a Member or Supervisor attempts to create a Board, THEN THE Backend SHALL return HTTP 403.
4. WHEN a Supervisor, Manager, or Admin creates a Column on a Board, THE Backend SHALL append the Column with the next `order` value.
5. IF a Member or Guest attempts to create a Column, THEN THE Backend SHALL return HTTP 403.
6. WHEN a Manager or Admin soft-deletes a Board, THE Backend SHALL set the Board's `deleted_at` and exclude the Board from default queries.
7. IF a Member, Supervisor, or Guest attempts to soft-delete a Board, THEN THE Backend SHALL return HTTP 403.
8. THE Backend SHALL never hard-delete a row from the Board table.
9. THE Frontend SHALL list the Boards the viewer may see in the Sidebar and use that list as the Board switcher.
10. WHILE a Board is open, THE Frontend SHALL render the Board's Columns and Cards in the main area.

### Requirement 4: Cards

**User Story:** As a team member, I want cards with description, subtasks, priority, dates, and attachments, so that I can capture and track a piece of work in one place.

#### Acceptance Criteria

1. WHEN a Card_Creator creates a Card in a Column, THE Backend SHALL store the Card with a title, a description, a Priority of `high`, `medium`, or `low`, a Float `order`, and nullable `start_date`, `end_date`, `category_id`, and `assignee_id`.
2. IF a Card is submitted with a Priority other than `high`, `medium`, or `low`, THEN THE Backend SHALL return HTTP 400 with the code `VALIDATION_ERROR`.
3. IF a Card is submitted with an `end_date` earlier than its `start_date`, THEN THE Backend SHALL return HTTP 400 with the code `VALIDATION_ERROR`.
4. IF a Member, Supervisor, or Guest attempts to create a Card and the user is not a Card_Creator, THEN THE Backend SHALL return HTTP 403.
5. WHEN a Card_Creator deletes a Card, THE Backend SHALL Soft_Delete the Card by setting `deleted_at`.
6. WHEN a Card_Creator archives a Card, THE Backend SHALL set the Card's `archived_at` and allow the archive to be reversed.
7. IF a Member attempts to create, delete, or archive a Card, THEN THE Backend SHALL return HTTP 403.
8. WHEN a Member edits a Card assigned to that Member, THE Backend SHALL apply the edit.
9. IF a Member edits a Card whose `assignee_id` is not that Member, THEN THE Backend SHALL return HTTP 403.
10. WHEN a Supervisor, Manager, or Admin edits any Card on a Board visible to that user, THE Backend SHALL apply the edit.
11. WHEN a Supervisor, Manager, or Admin assigns a Card to a user, THE Backend SHALL set the Card's `assignee_id` and create an `assigned` Notification for that user in the same transaction.
12. WHEN a user adds a Subtask to a Card the user may edit, THE Backend SHALL store the Subtask with a title, `is_done` defaulting to false, and a Float `order`.
13. WHEN a user toggles a Subtask's `is_done` or reorders it, THE Backend SHALL persist the change through `PATCH /api/subtasks/{id}`.
14. WHEN a user deletes a Subtask on a Card the user may edit, THE Backend SHALL remove the Subtask through `DELETE /api/subtasks/{id}`.
15. WHEN a user adds an Attachment to a Card the user may edit, THE Backend SHALL store either a `url` or a `file_path` with `mime_type`.
16. IF an Attachment has neither a `url` nor a `file_path`, THEN THE Backend SHALL return HTTP 400 with the code `VALIDATION_ERROR`.
17. IF an uploaded Attachment file type is not PDF, Word, or RAR, THEN THE Backend SHALL return HTTP 400 with the code `VALIDATION_ERROR`.
18. THE Backend SHALL return each uploaded Attachment as a stable, directly fetchable `file_url` that the Backend does not stream through an API endpoint.
19. WHEN a user clicks an Attachment, THE Frontend SHALL open it with `target="_blank"` and `rel="noopener noreferrer"` and SHALL provide no in-app preview.
20. WHEN a user opens a Card, THE Frontend SHALL show one two-pane modal used for both viewing and editing, with title, description, Priority, dates, Attachments, the Subtask checklist, and the Card's Activity_Log in the left pane and the Comment thread and composer in the right pane.
21. WHEN a user saves the left pane, THE Frontend SHALL commit the Card changes without closing the modal and without affecting the Comment composer.
22. THE Frontend SHALL render the Subtask checklist as a flat list of checkboxes with inline-editable titles and a drag handle for reordering.
23. THE Backend SHALL never hard-delete a row from the Card table.

### Requirement 5: Drag-and-Drop Card Movement

**User Story:** As a team member, I want to drag cards between columns, so that a card's new position persists after a page refresh.

#### Acceptance Criteria

1. WHEN a user drops a Card between two siblings with `order` values a and b, THE Backend SHALL set the moved Card's Float `order` to the average of a and b without rewriting sibling rows.
2. WHEN a user drops a Card, THE Frontend SHALL call `PATCH /api/cards/{id}/move` with the target Column and computed Float `order` on `dragend` and reconcile local state with the response.
3. WHEN a drag is in progress, THE Frontend SHALL insert a placeholder at the drop target and animate sibling Cards into place with a FLIP transform.
4. WHEN a Member moves a Card assigned to that Member, THE Backend SHALL apply the move.
5. IF a Member moves a Card whose `assignee_id` is not that Member, THEN THE Backend SHALL return HTTP 403.
6. WHEN a Supervisor, Manager, or Admin moves any Card on a visible Board, THE Backend SHALL apply the move.
7. IF a Guest attempts to move a Card, THEN THE Backend SHALL return HTTP 401 when no Token is present.
8. WHEN a Card move succeeds, THE Backend SHALL write exactly one Activity_Log row with action `card.moved` and the source and target Column in the same transaction.
9. WHEN a page is refreshed after a successful move, THE Frontend SHALL render the Card in the moved position.

### Requirement 6: Categories

**User Story:** As a Supervisor, Manager, or Admin, I want to manage each board's own categories, so that viewers can filter cards by the kinds of work that board runs.

#### Acceptance Criteria

1. WHEN a Supervisor, Manager, or Admin creates a Category on a Board, THE Backend SHALL store the Category with the Board's id, a name, and a nullable color.
2. WHEN a Supervisor, Manager, or Admin renames or recolors a Category, THE Backend SHALL apply the change through `PATCH /api/categories/{id}`.
3. WHEN a Supervisor, Manager, or Admin deletes a Category, THE Backend SHALL remove it through `DELETE /api/categories/{id}`.
4. IF a Member or Guest attempts to create, edit, or delete a Category, THEN THE Backend SHALL return HTTP 403.
5. WHEN any user with access to a Board requests `GET /api/boards/{board_id}/categories`, THE Backend SHALL return that Board's Categories without a role check.
6. WHEN a Guest requests the Categories of a public Board, THE Backend SHALL return them.
7. THE Backend SHALL return only the Categories owned by the requested Board.
8. WHEN a Board row is removed from the database, THE Backend SHALL cascade-delete that Board's Categories.
9. THE Frontend SHALL render the Board's filter-row chips from the `GET /api/boards/{board_id}/categories` response and use no hard-coded chip list.
10. WHEN the viewer switches Boards, THE Frontend SHALL re-fetch and re-render the filter-row chips.
11. WHERE the viewer is a Supervisor, Manager, or Admin, THE Frontend SHALL show a Categories entry in the Sidebar that opens an add, rename, recolor, and delete screen scoped to the current Board.

### Requirement 7: Comments

**User Story:** As a team member, I want threaded comments with manager priority flags, so that important discussion stays on top and managers can turn their own comments into cards.

#### Acceptance Criteria

1. WHEN a Member, Supervisor, or Manager posts to `POST /api/cards/{id}/comments` on a Card the user can view, THE Backend SHALL create a top-level Comment.
2. IF a Comment body is missing or empty, THEN THE Backend SHALL return HTTP 400 with the code `VALIDATION_ERROR` and the message `content is required`.
3. IF a Guest or an Admin attempts to create a Comment, THEN THE Backend SHALL return HTTP 403, or HTTP 401 when no Token is present.
4. WHEN a Member, Supervisor, or Manager posts to `POST /api/comments/{id}/replies` targeting a top-level Comment, THE Backend SHALL create the Reply and increment the parent's Reply_Count in the same transaction.
5. IF the target of a reply request has a non-null `parent_id`, THEN THE Backend SHALL return HTTP 400.
6. THE Backend SHALL provide no like or vote endpoint in the comments domain.
7. WHEN a Manager calls `PATCH /api/comments/{id}/priority` on any Comment, THE Backend SHALL toggle that Comment's `is_priority`.
8. IF a user who is not a Manager calls `PATCH /api/comments/{id}/priority`, THEN THE Backend SHALL return HTTP 403.
9. WHEN `GET /api/cards/{id}/comments` is called, THE Backend SHALL return Priority_Comments first, ordered newest priority first, followed by the remaining top-level Comments in the requested order.
10. WHEN the `sort` parameter is `latest` or omitted, THE Backend SHALL order the remaining top-level Comments newest first.
11. WHEN the `sort` parameter is `popular`, THE Backend SHALL order the remaining top-level Comments by Reply_Count descending, with ties broken by `created_at` descending.
12. THE Backend SHALL return each top-level Comment's Replies nested inline, ordered oldest first, regardless of the `sort` parameter.
13. THE Backend SHALL include `reply_count`, `is_priority`, and `can_create_card` on every returned Comment.
14. WHEN the viewer is a Supervisor, Manager, or Admin and the Comment's author role is manager, THE Backend SHALL set `can_create_card` to true regardless of `is_priority`.
15. IF the viewer is a Member or Guest, or the Comment's author role is not manager, THEN THE Backend SHALL set `can_create_card` to false.
16. IF a Guest requests a Card's Comments, THEN THE Backend SHALL return no `comments` field, including on direct calls to the comment endpoints.
17. THE Frontend SHALL render Priority_Comments first with a priority indicator, then the remaining top-level Comments under a visible Latest and Popular toggle that shows the Reply_Count as a badge.
18. THE Frontend SHALL show a Reply action only on top-level Comments.
19. WHERE `can_create_card` is true on a Comment, THE Frontend SHALL show the "create new card" action on that Comment.
20. WHERE the Card response omits `comments`, THE Frontend SHALL omit the Comment thread.

### Requirement 8: Activity Log

**User Story:** As a team member, I want an append-only history of what happened on a card and a board, so that I can trust the record of changes.

#### Acceptance Criteria

1. WHEN a state-changing action succeeds, THE Backend SHALL insert exactly one Activity_Log row with `actor_id`, `action`, `target_type`, `target_id`, `metadata`, and `created_at` in the same transaction as the change.
2. THE Backend SHALL never update or delete an Activity_Log row after insertion.
3. WHEN a Member, Supervisor, Manager, or Admin requests a Card's activity, THE Backend SHALL return the rows where `target_type` is `card` and `target_id` is that Card's id.
4. WHEN a Member, Supervisor, Manager, or Admin requests a Board's activity feed, THE Backend SHALL return every row for the Cards and Columns belonging to that Board.
5. IF a Guest requests Card activity or a Board activity feed, THEN THE Backend SHALL return no `activity` or `activity_log` field, including on direct calls and when the field is requested explicitly.
6. WHEN a user opens Activity from the Sidebar nav, THE Frontend SHALL open the Side_Panel on the Activity view.
7. WHERE the Card response omits `activity`, THE Frontend SHALL omit the Card activity section.

### Requirement 9: Notifications and Inbox

**User Story:** As a member, I want to be notified when a card is assigned to me or reaches its deadline, so that I do not miss work.

#### Acceptance Criteria

1. WHEN a Card is assigned to a user, THE Backend SHALL insert a Notification of type `assigned` for that user in the same transaction as the assignment.
2. WHEN the scheduled daily job runs, THE Backend SHALL create one `deadline` Notification for the Assigned_Member of each Card whose `end_date` equals today and whose `deleted_at` is null.
3. WHEN the scheduled daily job runs more than once on the same date, THE Backend SHALL create no duplicate `deadline` Notification for the same Card and assignee.
4. THE Backend SHALL create Notifications on the server and the Frontend SHALL not compute or poll them client-side.
5. WHEN a signed-in user requests the Inbox, THE Backend SHALL return only that user's Notifications and an unread count.
6. WHEN a user clicks Inbox in the Sidebar or clicks the header bell, THE Frontend SHALL open the Side_Panel on the Inbox view through the same toggle.
7. WHERE the API response omits Inbox data, THE Frontend SHALL omit the Inbox panel.

### Requirement 10: Analytics

**User Story:** As a Supervisor or Manager, I want pre-aggregated board analytics, so that I can judge progress without opening every board.

#### Acceptance Criteria

1. WHEN a Supervisor requests `GET /api/boards/{id}/analytics` for a Board whose `owner_id` is that Supervisor, THE Backend SHALL return an Analytics_Summary.
2. IF a Supervisor requests analytics for a Board whose `owner_id` is not that Supervisor, THEN THE Backend SHALL return HTTP 403.
3. WHEN a Manager requests analytics for any Board, THE Backend SHALL return an Analytics_Summary.
4. IF a Member, Admin, or Guest requests analytics, THEN THE Backend SHALL return HTTP 403, or HTTP 401 when no Token is present.
5. THE Backend SHALL return Analytics_Summary payloads of counts, deltas, and overdue totals, such as `{ "data": { "done": 12, "in_progress": 4, "overdue": 2 } }`, and never a raw dump of every Card.
6. WHEN a Manager requests cross-board analytics, THE Backend SHALL return one Analytics_Summary per Board in a single pre-aggregated response.

### Requirement 11: Board Visibility and Archiving

**User Story:** As a Supervisor, Manager, or Admin, I want to control board visibility and archive boards and cards, so that guests see only what is intended and finished work stays recoverable.

#### Acceptance Criteria

1. THE Backend SHALL store each Board's `visibility` as exactly `public` or `private`.
2. WHEN a Supervisor, Manager, or Admin sets a Board's visibility, THE Backend SHALL apply the change and record it in the Activity_Log.
3. IF a Member or Guest attempts to set Board visibility, THEN THE Backend SHALL return HTTP 403.
4. WHEN a Guest requests the Board list, THE Backend SHALL return only Boards where `visibility` is `public` and `deleted_at` is null.
5. IF a Guest requests a private Board, THEN THE Backend SHALL return HTTP 403 with an error Envelope.
6. WHEN a signed-in user requests any non-deleted Board, THE Backend SHALL return the Board regardless of its `visibility`.
7. WHEN a Guest requests a public Board, THE Backend SHALL return its Columns and Cards and omit `comments` and `activity_log`.
8. WHEN a Manager or Admin archives a Board, THE Backend SHALL set the Board's `archived_at` and allow the archive to be reversed.
9. IF a Member or Supervisor attempts to archive a Board, THEN THE Backend SHALL return HTTP 403.
10. WHEN a Supervisor, Manager, or Admin archives a Card, THE Backend SHALL set the Card's `archived_at`.

### Requirement 12: Search and Filter

**User Story:** As a user viewing a board, I want to search and filter its cards, so that I can find work quickly.

#### Acceptance Criteria

1. WHEN a user calls `GET /api/boards/{id}/cards` with `search=<text>`, THE Backend SHALL return only Cards on that Board whose text matches the search value.
2. WHEN a user calls `GET /api/boards/{id}/cards` with `filter[priority]`, `filter[assignee]`, or `filter[category]`, THE Backend SHALL return only Cards matching every supplied filter.
3. THE Backend SHALL exclude Soft_Deleted Cards from search and filter results.
4. IF a filter field is not supported, THEN THE Backend SHALL return HTTP 400 with the code `VALIDATION_ERROR`.
5. WHEN a user selects a Category chip, THE Frontend SHALL request the Board's Cards with the matching category filter.
6. WHEN a Guest searches a public Board, THE Backend SHALL return Card data only and no Comment or Activity_Log fields.

### Requirement 13: API Conventions and Data Integrity

**User Story:** As a frontend developer, I want one predictable API shape and consistent data rules, so that the client has a single place to unwrap responses and errors.

#### Acceptance Criteria

1. THE Backend SHALL serve all endpoints under `/api/...` without a version segment.
2. WHEN a request succeeds, THE Backend SHALL return `{ "data": <payload> }` with the payload as an object, a list, or null.
3. IF a request fails, THEN THE Backend SHALL return `{ "error": { "code": string, "message": string } }` with the matching HTTP status of 400, 401, 403, 404, or 409.
4. THE Backend SHALL return the Envelope shape on 100 percent of endpoints.
5. THE Backend SHALL use a UUID primary key on every entity and include `created_at` and `updated_at` on every entity.
6. THE Backend SHALL include `deleted_at` and `archived_at` on Board and Card.
7. THE Backend SHALL access the database only through each blueprint's own `repository.py`.
8. THE Backend SHALL read CORS origins from an environment variable allow-list and never use the wildcard `*`.
9. THE System SHALL provide a `.env.example` for the Backend and the Frontend and commit no real `.env` file.

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

### Requirement 15: Automated Testing

**User Story:** As a developer, I want automated tests for the API and the main user journey, so that regressions are caught.

#### Acceptance Criteria

1. THE System SHALL include `pytest` tests for comment creation covering success, validation failure, unauthenticated, and unauthorized cases.
2. THE System SHALL include a Playwright end-to-end test of the Kanban journey that runs against the deployed URL.
3. THE System SHALL contain no `waitForTimeout` call in any Playwright test file.
4. THE System SHALL unit-test each `service.py` against a fake repository without a real database.

### Requirement 16: Stretch Features

**User Story:** As a product owner, I want the prototype's extra card features tracked as stretch work, so that they do not delay the core paths.

#### Acceptance Criteria

1. WHERE the stretch features are enabled, THE Backend SHALL store a nullable 0 to 10 integer `progress` and an integer `views_count` defaulting to 0 on Card.
2. WHERE the stretch features are enabled, THE Frontend SHALL show the per-card progress meter, views counter, and the decorative Overview, Notes, and Questions tabs as in the prototype.
3. THE System SHALL build the stretch features only after Requirements 1 to 15 work end-to-end.
