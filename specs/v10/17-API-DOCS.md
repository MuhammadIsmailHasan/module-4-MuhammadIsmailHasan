### Requirement 17: API Documentation

**User Story:** As a frontend developer and reviewer, I want a generated OpenAPI document, an interactive Swagger page, and a written API reference, so that I can learn every endpoint without reading the backend code, while the public production server exposes no extra surface.

#### Acceptance Criteria
**Round 3 within V10 (Decisions U to W):** criterion 11 added (avatar routes under `/api/users`, avatar fields, candidate minimum length, 429 on change-password).

V10 changes: criterion 1 reworded (429 documented on the rate-limited operations). All other criteria are unchanged from V4.

1. THE Backend SHALL generate its OpenAPI 3 document with flask-smorest, describing every registered `/api` route with its method, path, path and query parameters, request schema, Envelope response schema, Token requirement, and error responses 400, 401, 403, 404, and 409, plus 429 on the rate-limited operations of Requirement 20 (Decisions E and O).
11. THE Backend SHALL document in the OpenAPI document and in `backend/API.md` the avatar routes under `/api/users` (`POST` and `DELETE /api/users/me/avatar`, `GET /api/users/{user_id}/avatar/file`), the `avatar_url`, `author_avatar_url`, and `assignee_avatar_url` fields of the Comment, member, candidate, and Card schemas, the `search` minimum length of the candidates endpoint, and the 429 response of `POST /api/auth/change-password` (Decisions U and W; V10 round 3).
