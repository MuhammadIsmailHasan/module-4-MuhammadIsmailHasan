### Requirement 13: API Conventions and Data Integrity

**User Story:** As a frontend developer, I want one predictable API shape and consistent data rules, so that the client has a single place to unwrap responses and errors.

#### Acceptance Criteria

V10 changes: criteria 3, 10, and 11 reworded (429 joins the status list; `error.details` also on registration `CONFLICT` and `RATE_LIMITED`; Token-free routes listed). All other criteria are unchanged from V8. **Round 2 within V10:** criterion 10 reworded (the signature-checked avatar file route joins the Token-free routes; Decision R).

3. IF a request fails, THEN THE Backend SHALL return `{ "status": false, "message": <non-empty string>, "error": { "code": string, "details"?: object } }` with the matching HTTP status of 400, 401, 403, 404, 405, 409, 429, or 500, stating the message text only at the top level and including no `message` field in `error`, and with `error.details` present only for `VALIDATION_ERROR`, for the `CONFLICT` of a registration (per field, criterion 4 of Requirement 1), and for `RATE_LIMITED` (`retry_after`) (Decisions G and O; amended in V10).
10. IF a request carries no Token on an endpoint that requires one, THEN THE Backend SHALL return HTTP 401, and IF a valid Token lacks the required role or Board_Access, THEN THE Backend SHALL return HTTP 403, except `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/availability`, the shared routes of Requirement 18, and the signed file routes of Attachments and avatars (Decisions D and R), which take a signature in place of a Token (Decision K; reworded in V10, the earlier exception for Guests reading public Boards is removed).
11. THE Backend SHALL set the Envelope `status` to true when the HTTP status is 2xx and to false otherwise, on every Envelope response, including 401, 403, 404, 405, 409, 429, and 500 responses and the errors of the signed file route, with the exceptions of the Swagger UI HTML page, the raw OpenAPI document, and the successful file bytes of the signed file route, which carry no Envelope, and THE Backend SHALL carry the numeric HTTP status on the HTTP line only (Decision G).
