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
