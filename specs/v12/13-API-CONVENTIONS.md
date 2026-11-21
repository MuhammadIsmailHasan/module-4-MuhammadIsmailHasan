# API conventions, V12 changes

Breaking changes (Backend and Frontend deploy together):

- `visibility` is removed from every Board request and response; a posted `visibility` is 400 `VALIDATION_ERROR`.
- `GET /api/boards` returns only owned and member Boards for Member and Supervisor accounts; every Board for Manager and Admin.
- The four `/api/boards/{id}/share` endpoints answer 403 to the Board_Owner (Manager and Admin only).
- `POST /api/boards/{id}/members` and `GET /api/boards/{id}/candidates` are Manager and Admin only, Member and Supervisor accounts only; a Manager or Admin `user_id` is 400.
- `PATCH /api/cards/{id}` rejects an `assignee_id` that is not the owner or a Board_Member (400 `details.assignee_id`) and a posted `progress` (400 `details.progress`); an unchanged PATCH writes no activity row.
- `GET /api/boards/{id}/members` returns the owner first, once, with `is_owner` (round 2 within V12: the Sidebar shows the owner row tagged "Owner" with no remove action); `email` only with `?include=email` for staff.
- `GET /api/notifications` rows gain `type` values, `board_id`, `board_name`, `card_id`, `card_title`, `actor_name`, and `is_read`.

Added endpoints (all in the shared Envelope):

| Method and path | Roles | Success | Errors |
|---|---|---|---|
| `GET`, `POST`, `DELETE /api/boards/{id}/invite`, `POST /api/boards/{id}/invite/regenerate` | owner, Manager, Admin | 200 `{ enabled, token, path }` | 401, 403, 404 |
| `GET /api/invite/{token}` | signed in | 200 `{ board, state, request }` | 401, 404 `NOT_FOUND` |
| `POST /api/invite/{token}/requests` | Member, Supervisor | 201 `{ id, board_id, status, created_at }` | 401, 404, 400 `VALIDATION_ERROR` (Manager, Admin), 409 `CONFLICT` (member, owner, pending) |
| `GET /api/boards/{id}/join-requests?status=` | owner, Manager, Admin | 200 list of `{ id, status, created_at, user: { id, full_name, username, email, avatar_url } }` (round 2 within V12: the Email only here and only to these three roles) | 401, 403, 404, 400 |
| `PATCH /api/join-requests/{id}` | Manager, Admin | 200 | 401, 403 (owner included), 404, 409 `CONFLICT`, 400 |
| `DELETE /api/comments/{id}` | author | 200 `{ deleted: n }` | 401, 403, 404 |

Every `/api/invite` response sends `Cache-Control: private, no-store`. Every mutating method under `/api/shared` answers 405.
