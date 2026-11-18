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
