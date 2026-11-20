# Kanban API Reference

Hand-written guide to the backend API. The generated OpenAPI document (`backend/openapi.json`, produced by `flask export-openapi`) is the source of truth for every field and schema; this file explains the rules around it. All paths are under `/api`, with no version segment.

## Interactive docs (Swagger)

Swagger UI is served only for local work:

```bash
APP_ENV=development flask run     # then open http://localhost:5000/api/docs
```

| `APP_ENV` | `/api/docs` and `/api/openapi.json` |
|---|---|
| `development`, `testing` | served |
| `production`, unset, or any other value | not registered (404 error envelope) |

`APP_ENV` is optional and defaults to `production`, so a missing variable hides the docs. Regenerate the file with `flask export-openapi` after changing any route or schema; a test fails if `backend/openapi.json` is out of date.

## Response envelope

Every response carries a boolean `status` (true exactly when the HTTP status is 2xx) and a `message` string. The numeric HTTP status travels on the HTTP line only, not in the body.

Success (`status: true`):

```json
{ "status": true, "message": "OK", "data": { "id": "…", "title": "Fix login" } }
```

`data` is an object, a list, or `null`. Mutating endpoints send a short descriptive message ("Card moved"); reads send "OK". Create calls return HTTP 201. List endpoints return every row, except the Inbox and the two activity feeds, which are paged (see Paging below).

Error (`status: false`):

```json
{ "status": false, "message": "Validation failed",
  "error": { "code": "VALIDATION_ERROR", "details": { "content": ["content is required"] } } }
```

The message text appears once, at the top level; `error` holds only the machine-readable `code` and, for `VALIDATION_ERROR` from body or query validation, `details` (field name to a list of messages). Branch on `error.code`. The only responses without an envelope are the Swagger page, `/api/openapi.json`, and the successful bytes of `GET /api/attachments/{id}/file`.

| HTTP | `error.code` | Meaning |
|---|---|---|
| 400 | `VALIDATION_ERROR` | Bad body or query. marshmallow failures are mapped to 400, never 422 |
| 401 | `UNAUTHORIZED` | Missing, invalid or expired Token; bad login; Guest on a private board |
| 403 | `FORBIDDEN` | Valid Token but role, board access or ownership is not enough; bad file signature |
| 404 | `NOT_FOUND` | Unknown or soft-deleted resource, unknown route |
| 405 | `METHOD_NOT_ALLOWED` | Wrong HTTP method |
| 409 | `CONFLICT` | Duplicate login, board member or category name |
| 500 | `INTERNAL_ERROR` | Unhandled error; generic message, details only in server logs |

## Authentication

`POST /api/auth/register` and `POST /api/auth/login` return `{ user, token }`. Send the Token on every other call:

```
Authorization: Bearer <token>
```

The Token is a JWT with a fixed 24-hour expiry. It carries the user id and role; the role is read only from the signed Token, never from a request body. `POST /api/auth/logout` revokes nothing: the client discards the Token. Rate limiting and Google login are not implemented.

Auth column in the tables below: **Token** = required, **Optional** = Guests may call it (public boards), **Public** = no Token.

## Roles

Roles: `guest` (no Token), `member`, `supervisor`, `manager`, `admin`. Admin is a separate administration track, not a Manager superset.

| Action | Guest | Member | Supervisor | Manager | Admin |
|---|---|---|---|---|---|
| Read public board, cards, categories, search | yes | yes | yes | yes | yes |
| Read private board | no (401) | if owner or member of it | if owner or member of it | yes | yes |
| Read comments and activity | no | yes | yes | yes | yes |
| Create, delete, archive card; add column; manage categories | no | no | board owner or member | yes | yes |
| Edit or move a card | no | only when assigned | board owner or member | yes | yes |
| Comment, reply | no | yes | yes | yes | no |
| Toggle comment priority | no | no | no | yes | no |
| Create, archive, delete board | no | no | no | yes | yes |
| Change board owner (must be a supervisor) | no | no | no | yes | yes |
| Change visibility | no | no | owner or member | yes | yes |
| Add or remove board members | no | no | if owner | yes | yes |
| Board analytics | no | no | only as owner | yes | no |
| Cross-board analytics | no | no | no | yes | no |
| Manage users | no | no | no | no | yes |

A private board is visible only to its owner, its members, Managers and Admins. A Guest on a private board gets 401, a signed-in user without access gets 403.

## Behaviours worth knowing

- **Soft delete.** Deleting a board or card sets `deleted_at`; the row stays and is hidden (404). Archive sets `archived_at`.
- **Ordering and move.** `PATCH /api/cards/{id}/move` takes `column_id` plus the neighbour ids `prev` and `next`. The server computes `order` (empty column `1.0`, first `min - 1`, last `max + 1`, otherwise the average) and ignores any client `order`. When two neighbours are closer than `1e-6` the column is renumbered `1.0, 2.0, …` in the same transaction. Moving to a column of another board returns 400. Subtasks reorder with `prev`/`next` or an explicit `order` on `PATCH /api/subtasks/{id}`.
- **Attachments.** Add a link (`{ "url": "https://…" }`) or upload a PDF, Word or RAR file as multipart `file`. Uploaded files are stored privately. A card response carries a fresh signed `file_url` (valid 15 minutes) per uploaded attachment; request a new one with `GET /api/attachments/{id}/url`. `GET /api/attachments/{id}/file?exp=&sig=` needs no Token and returns 403 for a missing, altered or expired signature.
- **Guests.** Card and board responses never include `comments` or `activity` for a Guest; the comment and activity endpoints return 403 on a public board.
- **Notifications.** Created server-side only: an `assigned` one when a card is assigned, a `deadline` one from the daily `flask notify-deadlines` job (dates in `APP_TIMEZONE`). One per user, card, type and day.
- **Search.** `GET /api/boards/{id}/cards?search=&filter[priority]=&filter[assignee]=&filter[category]=`. Filters combine with AND; an unsupported `filter[...]` key returns 400.
- **Comments.** `sort=latest|popular`; priority comments first; replies nested oldest first; replies to replies return 400. `can_create_card` is true when the viewer is a Supervisor, Manager or Admin and the author is a Manager. Every comment and reply carries `author_name`, and every activity row carries `actor_name` (the user's display name), so a client needs no user lookup.
- **Activity metadata.** New activity rows keep the names and changes in `metadata`, so a row reads without a lookup: `card_title` on every card event; `changes` on `card.updated` (`{field: {from, to}}` for `title`, `priority`, `start_date`, `end_date`, and `category` by name; a changed `description` is `{}`); `from_column_name` and `to_column_name` on `card.moved`; `assignee_name` on `card.assigned`; `title` on subtask events; `name` on attachment events. Rows written earlier keep their older keys.

## Endpoints


### auth

Register, log in, log out.

| Method | Path | Auth | Success | Errors | Summary |
|---|---|---|---|---|---|
| POST | `/api/auth/register` | Public | 201 | 400, 409, 422 | Register an account |
| POST | `/api/auth/login` | Public | 200 | 400, 401, 422 | Log in (`identifier` is a username or an email) |
| GET | `/api/auth/availability` | Public | 200 | 400 | Check whether a `username` or `email` is free |
| POST | `/api/auth/logout` | Public | 200 | - | Log out |

### boards

Boards, visibility, archive, members and the board activity feed.

| Method | Path | Auth | Success | Errors | Summary |
|---|---|---|---|---|---|
| POST | `/api/boards` | Token | 201 | 400, 401, 403, 422 | Create a board |
| GET | `/api/boards` | Optional | 200 | - | List visible boards, each with `card_count`, `done_count`, `overdue_count`, `member_count` |
| GET | `/api/boards/{board_id}` | Optional | 200 | 400, 401, 403, 404 | Get a board with its columns |
| PATCH | `/api/boards/{board_id}` | Token | 200 | 400, 401, 403, 404, 422 | Update name, visibility or owner |
| DELETE | `/api/boards/{board_id}` | Token | 200 | 401, 403, 404 | Soft-delete a board |
| POST | `/api/boards/{board_id}/archive` | Token | 200 | 401, 403, 404 | Archive a board |
| POST | `/api/boards/{board_id}/unarchive` | Token | 200 | 401, 403, 404 | Unarchive a board |
| GET | `/api/boards/{board_id}/members` | Optional | 200 | 400, 401, 403, 404 | List board members |
| POST | `/api/boards/{board_id}/members` | Token | 201 | 400, 401, 403, 404, 409, 422 | Add a board member |
| DELETE | `/api/boards/{board_id}/members/{user_id}` | Token | 200 | 401, 403, 404 | Remove a board member |
| GET | `/api/boards/{board_id}/activity` | Optional | 200 | 400, 401, 403, 404 | Board activity feed (paged) |
| GET | `/api/boards/{board_id}/candidates` | Token | 200 | 400, 401, 403, 404 | Search users who can be added to a board |

### columns

Add a column to a board.

| Method | Path | Auth | Success | Errors | Summary |
|---|---|---|---|---|---|
| POST | `/api/boards/{board_id}/columns` | Token | 201 | 400, 401, 403, 404, 422 | Add a column |

### cards

Cards, move, subtasks, attachments, signed file URLs, card activity, search and filter.

| Method | Path | Auth | Success | Errors | Summary |
|---|---|---|---|---|---|
| POST | `/api/columns/{column_id}/cards` | Token | 201 | 400, 401, 403, 404, 422 | Create a card |
| GET | `/api/cards/{card_id}` | Optional | 200 | 400, 401, 403, 404 | Get a card |
| PATCH | `/api/cards/{card_id}` | Token | 200 | 400, 401, 403, 404, 422 | Update a card |
| DELETE | `/api/cards/{card_id}` | Token | 200 | 401, 403, 404 | Soft-delete a card |
| POST | `/api/cards/{card_id}/archive` | Token | 200 | 401, 403, 404 | Archive a card |
| POST | `/api/cards/{card_id}/unarchive` | Token | 200 | 401, 403, 404 | Unarchive a card |
| PATCH | `/api/cards/{card_id}/move` | Token | 200 | 400, 401, 403, 404, 422 | Move or reorder a card |
| GET | `/api/cards/{card_id}/activity` | Optional | 200 | 400, 401, 403, 404 | Card activity (paged) |
| GET | `/api/boards/{board_id}/cards` | Optional | 200 | 400, 401, 403, 404, 422 | Search and filter a board's cards |
| POST | `/api/cards/{card_id}/subtasks` | Token | 201 | 400, 401, 403, 404, 422 | Add a subtask |
| PATCH | `/api/subtasks/{subtask_id}` | Token | 200 | 400, 401, 403, 404, 422 | Edit, toggle or reorder a subtask |
| DELETE | `/api/subtasks/{subtask_id}` | Token | 200 | 401, 403, 404 | Delete a subtask |
| POST | `/api/cards/{card_id}/attachments` | Token | 201 | 400, 401, 403, 404 | Add an attachment |
| DELETE | `/api/attachments/{attachment_id}` | Token | 200 | 401, 403, 404 | Delete an attachment |
| GET | `/api/attachments/{attachment_id}/url` | Optional | 200 | 400, 401, 403, 404 | Issue a fresh signed file URL |
| GET | `/api/attachments/{attachment_id}/file` | Public | 200 | 403, 404 | Download an uploaded file |

### categories

Board-scoped categories.

| Method | Path | Auth | Success | Errors | Summary |
|---|---|---|---|---|---|
| GET | `/api/boards/{board_id}/categories` | Optional | 200 | 400, 401, 403, 404 | List a board's categories |
| POST | `/api/boards/{board_id}/categories` | Token | 201 | 400, 401, 403, 404, 409, 422 | Create a category |
| PATCH | `/api/categories/{category_id}` | Token | 200 | 400, 401, 403, 404, 409, 422 | Rename or recolor a category |
| DELETE | `/api/categories/{category_id}` | Token | 200 | 401, 403, 404 | Delete a category |

### comments

Comments, replies and the priority flag.

| Method | Path | Auth | Success | Errors | Summary |
|---|---|---|---|---|---|
| POST | `/api/cards/{card_id}/comments` | Optional | 201 | 400, 401, 403, 404, 422 | Add a comment |
| GET | `/api/cards/{card_id}/comments` | Optional | 200 | 400, 401, 403, 404, 422 | List comments |
| POST | `/api/comments/{comment_id}/replies` | Optional | 201 | 400, 401, 403, 404, 422 | Reply to a top-level comment |
| PATCH | `/api/comments/{comment_id}/priority` | Token | 200 | 401, 403, 404 | Toggle the priority flag |

### notifications

The caller's inbox.

| Method | Path | Auth | Success | Errors | Summary |
|---|---|---|---|---|---|
| GET | `/api/notifications` | Token | 200 | 400, 401 | List my notifications (paged) |
| PATCH | `/api/notifications/read-all` | Token | 200 | 401 | Mark all my notifications read |
| PATCH | `/api/notifications/{notification_id}/read` | Token | 200 | 401, 404 | Mark one notification read |

### analytics

Board and cross-board summaries.

| Method | Path | Auth | Success | Errors | Summary |
|---|---|---|---|---|---|
| GET | `/api/boards/{board_id}/analytics` | Token | 200 | 400, 401, 403, 404 | Board analytics |
| GET | `/api/analytics/boards` | Token | 200 | 401, 403 | Cross-board analytics |

### users

User administration (Admin only).

| Method | Path | Auth | Success | Errors | Summary |
|---|---|---|---|---|---|
| GET | `/api/users` | Token | 200 | 401, 403 | List users |
| POST | `/api/users` | Token | 201 | 400, 401, 403, 409, 422 | Create a user |
| PATCH | `/api/users/{user_id}` | Token | 200 | 400, 401, 403, 404, 409, 422 | Update a user or assign a role |

## Examples

Register:

```http
POST /api/auth/register
{ "full_name": "Ann", "username": "ann", "email": "ann@example.com", "password": "<at least 8 characters>" }

201 { "status": true, "message": "User registered",
      "data": { "user": { "id": "…", "full_name": "Ann", "username": "ann", "email": "ann@example.com", "avatar_url": null }, "token": "eyJ…" } }
```

Create a board (Manager):

```http
POST /api/boards
{ "name": "Sprint 1", "visibility": "private" }

201 { "status": true, "message": "Board created",
      "data": { "id": "…", "name": "Sprint 1", "visibility": "private", "owner_id": null, "archived_at": null,
                "columns": [ { "id": "…", "name": "Todo", "order": 0.0 }, … ] } }
```

Move a card between two neighbours:

```http
PATCH /api/cards/{id}/move
{ "column_id": "…", "prev": "<card above>", "next": "<card below>" }

200 { "status": true, "message": "Card moved",
      "data": { "id": "…", "column_id": "…", "order": 1.5, … } }
```

Add a comment (blank body is rejected):

```http
POST /api/cards/{id}/comments
{ "content": "   " }

400 { "status": false, "message": "Validation failed",
      "error": { "code": "VALIDATION_ERROR", "details": { "content": ["content is required"] } } }
```

Signed file URL:

```http
GET /api/attachments/{id}/url

200 { "status": true, "message": "OK",
      "data": { "file_url": "/api/attachments/{id}/file?exp=1767225600&sig=…", "expires_at": "2026-01-01T00:00:00+00:00" } }
```

Analytics (Manager):

```http
GET /api/boards/{id}/analytics

200 { "status": true, "message": "OK",
      "data": { "board_id": "…", "name": "Sprint 1", "total": 12, "done": 4, "in_progress": 3, "overdue": 1, "done_delta": 2 } }
```

## Paging

The Inbox (`GET /api/notifications`), the board activity feed, and the card activity list take `limit` (default 20, at most 100) and `before` (the id of the last row already shown). They return the next older rows in the same response shape; a response with fewer rows than `limit` is the last page. A `limit` outside 1 to 100, or a `before` that is not a row of that list, returns 400 `VALIDATION_ERROR`. The Inbox `unread_count` always counts all of the caller's notifications, and `GET /api/cards/{id}` embeds the first 20 activity rows. `GET /api/boards/{id}/candidates?search=` returns at most 20 users who are not members of the board, with `id`, `full_name`, `username`, `email` and `avatar_url` (owner, Manager, Admin). `search` must be at least 2 characters (400 otherwise) and matches the name by substring, the username by prefix, and the email exactly.

## Board description and counts

A board has a nullable `description` (at most 500 characters, trimmed, empty becomes null), accepted on `POST /api/boards` and `PATCH /api/boards/{id}` (name-change rules) and returned on every board response. `GET /api/boards` also returns four computed integers per board: `card_count` (cards not deleted and not archived), `done_count` (of those, in the `Done` column), `overdue_count` (of those, past their end date and not Done), and `member_count`. They come from two grouped queries whatever the number of boards.

