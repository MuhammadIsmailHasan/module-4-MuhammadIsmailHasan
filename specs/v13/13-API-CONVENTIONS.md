# API conventions, V13 changes

- `GET /api/boards/{id}/members` rows gain `role` (`member` or `supervisor`), additive. No other endpoint changes. `/api/shared` payloads carry no `role` (ROLE-05).
