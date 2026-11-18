### Requirement 17: API Documentation

**User Story:** As a frontend developer and reviewer, I want a written API reference and an interactive Swagger page, so that I can learn every endpoint without reading the backend code, while the public production server exposes no extra surface.

#### Acceptance Criteria

1. THE Backend SHALL keep one OpenAPI 3 document at `backend/openapi.yaml` that describes every registered `/api` route with its method, path, path and query parameters, request body, success payload, Token requirement, permitted roles, and error statuses (400, 401, 403, 404, 409).
2. THE System SHALL keep a human-readable `backend/API.md` that lists the same endpoints grouped by blueprint, with the Envelope shape, the error codes, the role-to-endpoint matrix, and one example request and response for each group.
3. WHEN `APP_ENV` is `development` or `testing`, THE Backend SHALL serve Swagger UI at `/api/docs` and the raw document at `/api/docs/openapi.yaml`.
4. WHEN `APP_ENV` is `production` or unset, THE Backend SHALL NOT register the Swagger UI route or the raw document route, so both return the 404 Envelope.
5. THE Backend SHALL read `APP_ENV` from the environment, default it to `production`, list it in `backend/.env.example`, and not refuse to start when it is missing.
6. THE Backend SHALL treat the documentation routes as read-only and public, SHALL NOT return secrets, and SHALL exclude them from the 401/403 mutating-route sweep.
7. THE System SHALL include an automated test that fails when a registered `/api` route is missing from `openapi.yaml` or when `openapi.yaml` lists a route that is not registered.
8. THE System SHALL include an automated test that confirms the documentation routes return 404 when `APP_ENV` is `production`.
