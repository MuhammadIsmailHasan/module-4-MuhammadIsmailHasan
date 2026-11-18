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
10. IF a request carries no Token on an endpoint that requires one, THEN THE Backend SHALL return HTTP 401, and IF a valid Token lacks the required role or Board_Access, THEN THE Backend SHALL return HTTP 403, except that Guests may read public Boards without a Token.
