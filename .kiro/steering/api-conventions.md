---
inclusion: always
---

# API Conventions Steering

- **Rule:** All endpoints are versionless, under `/api/...`, and resource-nested
  for creation (`POST /api/boards/{board_id}/columns`), flat for direct access
  (`GET /api/cards/{id}`).
  **Rationale:** One predictable routing shape across every blueprint, instead
  of each domain inventing its own.
  **Example:** `PATCH /api/cards/{id}/move` for a drag-and-drop position change.

- **Rule:** Every response carries a top-level boolean `status` (`true` exactly
  when the HTTP status is 2xx, otherwise `false`) and a human-readable
  `message`. A success is `{ "status": true, "message": "...", "data": <payload> }`
  where the payload is a single object, a list, or `null`. An error is
  `{ "status": false, "message": "...", "error": { "code": string, "details"?: object } }`
  with a matching HTTP status (`400`, `401`, `403`, `404`, `405`, `409`, `429`, `500`).
  The message text appears once, at the top level; `error` holds only the
  machine-readable `code` and a `details` object only for `VALIDATION_ERROR`
  (each field to a list of messages), for the `CONFLICT` of a registration or
  email save (each duplicate field to a list of messages), and for
  `RATE_LIMITED` (`{ "retry_after": seconds }`, also sent as the `Retry-After`
  header). The HTTP status code travels on
  the HTTP line only. Mutating endpoints send a short descriptive `message`
  ("Card moved"); reads default to "OK".
  **Rationale:** One envelope on both paths means the frontend's API client has
  exactly one place that unwraps a response or throws. Putting the text once
  avoids two messages drifting apart, and `error.code` is what code branches on.
  **Example:** `GET /api/cards/{id}` → `200 { "status": true, "message": "OK", "data": { "id": "...", "title": "..." } }`;
  a missing comment body → `400 { "status": false, "message": "Validation failed", "error": { "code": "VALIDATION_ERROR", "details": { "content": ["Missing data for required field."] } } }`.

- **Rule:** List endpoints that back a search/filter UI accept `?search=` and
  `?filter[<field>]=` query params.
  **Rationale:** One documented, reusable convention for "search and filter
  cards on the active board" instead of a bespoke query shape per list.
  **Example:** `GET /api/boards/{id}/cards?search=login&filter[priority]=high`.

- **Rule:** `POST /api/auth/register` (`full_name`, `username`, `email`,
  `password`) and `POST /api/auth/login` (`identifier`, `password`) both return
  `{ "data": { "user": { id, full_name, username, email, avatar_url }, "token": "..." } }`.
  `GET /api/auth/availability?username=&email=` answers
  `{ "username": { "available": bool }, "email": { "available": bool } }`.
  **Rationale:** One shared user shape from both endpoints keeps the frontend
  auth client simple — it never branches on which endpoint it just called.
  **Example:** register and login responses are interchangeable as far as the
  client's session storage is concerned.

- **Rule:** `GET /api/cards/{id}/comments?sort=latest|popular` (default
  `latest`; `popular` orders by reply count, ties broken by newest) returns
  priority-flagged top-level comments first, then the rest in the requested
  order, each with its replies nested inline and always ordered oldest-first.
  `POST /api/cards/{id}/comments` creates a top-level comment;
  `POST /api/comments/{id}/replies` creates a reply (`400` if the target is
  itself a reply); `PATCH /api/comments/{id}/priority` (manager-only) toggles
  the priority flag. There is no like endpoint.
  **Rationale:** One documented set of endpoints for every comment
  interaction, instead of ad hoc routes invented per feature as comments grow.
  **Example:** each comment in the response carries
  `{ "reply_count": 3, "is_priority": false, "can_create_card": true }`.

- **Rule:** `GET /api/boards/{board_id}/categories` lists a board's
  categories (open to anyone with board access); `POST` creates one,
  `PATCH /api/categories/{id}` renames/recolors it, `DELETE /api/categories/{id}`
  removes it — the last three are supervisor/manager/admin-only.
  **Rationale:** Categories are scoped per board and filtered on the same
  board page, so a nested-under-`boards` + flat-by-id shape matches every
  other board sub-resource.
  **Example:** `POST /api/boards/b_1/categories { "name": "Design", "color": "purple" }`
  → `{ "data": { "id": "cat_1", "board_id": "b_1", "name": "Design", "color": "purple" } }`.

- **Rule:** `POST /api/cards/{id}/subtasks` creates a subtask;
  `PATCH /api/subtasks/{id}` updates `title` / `is_done` / `order`;
  `DELETE /api/subtasks/{id}` removes it.
  **Rationale:** Subtasks are simple enough that a dedicated small CRUD under
  the card resource is clearer than overloading the card's own `PATCH` body
  with a nested array every time one checkbox changes.
  **Example:** `PATCH /api/subtasks/st_1 { "is_done": true }` →
  `{ "data": { "id": "st_1", "is_done": true } }`.

- **Rule:** The login `identifier` is a username (no `@`) or an email (has `@`);
  the server decides the type and answers `400 VALIDATION_ERROR` when it fits
  neither shape. Unknown user and wrong password return the same `401`.
  Profile endpoints: `GET|PATCH /api/auth/me`, `POST /api/auth/change-password`
  (a wrong current password is `400`, never `401`). Share-link endpoints:
  `GET|POST|DELETE /api/boards/{id}/share`, `POST /api/boards/{id}/share/regenerate`
  (owner, manager, admin); the token-free read-only routes are
  `GET /api/shared/{token}`, `/cards`, `/categories`, `/cards/{card_id}`,
  `/attachments/{id}/url` — there is no comment, activity, or mutating route
  under `/api/shared`. Additional auth and
  membership endpoints: `POST /api/auth/logout` (returns `{ "data": null }`),
  `PATCH /api/notifications/{id}/read`, `PATCH /api/notifications/read-all`,
  `GET|POST /api/boards/{id}/members`, `DELETE /api/boards/{id}/members/{user_id}`,
  `GET /api/attachments/{id}/url`, and `GET /api/boards/{id}/candidates` (matches
  `full_name`, `username` by prefix, `email` by exact match, case-insensitively;
  owner, manager, admin only; returns `id`, `full_name`, `username`, `email`).
  `GET /api/boards/{id}/members` returns `id`, `full_name`, `username`, and adds
  `email` only with `?include=email`, which needs write access to the board
  (otherwise `403`). Avatar endpoints: `POST` (multipart, field `file`) and
  `DELETE /api/auth/me/avatar`, and the signature-checked, token-free
  `GET /api/auth/avatars/{user_id}/file`; `avatar_url` in a `user` payload is a
  signed URL or `null`, and no other payload carries it.
  A malformed, expired, or invalid Bearer Token on a `/api/shared` route is
  ignored (the caller is a guest, never `401`).
  **Rationale:** One identifier column keeps register/login matching simple;
  the other endpoints close gaps the first version left open.
  **Example:** `POST /api/boards/b_1/members { "user_id": "u_2" }` →
  `{ "data": { "board_id": "b_1", "user_id": "u_2" } }`.

- **Rule:** Lists are unpaged, except the Inbox and the two activity feeds, which
  take `limit` (default 20, at most 100) and `before` (the id of the last row the
  client has) and keep their response shape (Decision J).
  **Rationale:** Only these lists grow without bound; a row-id cursor adds paging
  without changing what existing clients read.
  **Example:** `GET /api/boards/{id}/activity?limit=20&before=<activity id>`.

