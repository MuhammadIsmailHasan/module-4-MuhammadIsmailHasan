### Requirement 15: Automated Testing

**User Story:** As a developer, I want automated tests for the API and the main user journey, so that regressions are caught.

#### Acceptance Criteria

1. THE System SHALL include `pytest` tests for comment creation covering success, validation failure, unauthenticated, and unauthorized cases.
2. THE System SHALL include a Playwright end-to-end test of the Kanban journey that runs against the deployed URL.
3. THE System SHALL contain no `waitForTimeout` call in any Playwright test file.
4. THE System SHALL unit-test each `service.py` against a fake repository without a real database.
5. THE System SHALL include `pytest` tests covering the HTTP 401 (no Token) and HTTP 403 (insufficient role or access) cases for every mutating endpoint.
6. THE System SHALL include a `pytest` test that an unrelated Member receives HTTP 403 on a private Board (Decision A).
7. THE System SHALL include `pytest` tests for Attachment access covering a permitted viewer, an unrelated Member, a Guest on a private Board, and an expired signature (Decision D).
