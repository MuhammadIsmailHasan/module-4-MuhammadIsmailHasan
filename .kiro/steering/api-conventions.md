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

- **Rule:** Every response carries a top-level `status` (the HTTP status code,
  integer) and a human-readable `message` (string). A success is
  `{ "status": 200, "message": "...", "data": <payload> }` where the payload is
  a single object, a list, or `null`. An error is
  `{ "status": 404, "message": "...", "error": { "code": string, "message": string } }`
  with a matching HTTP status (`400`, `401`, `403`, `404`, `405`, `409`, `500`); `error.message`
  repeats the top-level `message`.
  **Rationale:** One envelope on both paths means the frontend's API client has
  exactly one place that unwraps a response or throws, and the body alone says
  what happened without reading the HTTP line. Keeping `error.code` and
  `error.message` leaves existing error handling intact.
  **Example:** `GET /api/cards/{id}` → `200 { "status": 200, "message": "Card retrieved", "data": { "id": "...", "title": "..." } }`;
  a missing comment body → `400 { "status": 400, "message": "content is required", "error": { "code": "VALIDATION_ERROR", "message": "content is required" } }`.

- **Rule:** List endpoints that back a search/filter UI accept `?search=` and
  `?filter[<field>]=` query params.
  **Rationale:** One documented, reusable convention for "search and filter
  cards on the active board" instead of a bespoke query shape per list.
  **Example:** `GET /api/boards/{id}/cards?search=login&filter[priority]=high`.

- **Rule:** `POST /api/auth/register` and `POST /api/auth/login` both return
  `{ "data": { "user": { id, full_name, login_identifier, avatar_url }, "token": "..." } }`.
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

- **Rule:** The `login_identifier` is one unique, case-insensitive string
  column; the same field accepts an email or a username. Additional auth and
  membership endpoints: `POST /api/auth/logout` (returns `{ "data": null }`),
  `PATCH /api/notifications/{id}/read`, `PATCH /api/notifications/read-all`,
  `GET|POST /api/boards/{id}/members`, `DELETE /api/boards/{id}/members/{user_id}`,
  `GET /api/attachments/{id}/url`.
  **Rationale:** One identifier column keeps register/login matching simple;
  the other endpoints close gaps the first version left open.
  **Example:** `POST /api/boards/b_1/members { "user_id": "u_2" }` →
  `{ "data": { "board_id": "b_1", "user_id": "u_2" } }`.
