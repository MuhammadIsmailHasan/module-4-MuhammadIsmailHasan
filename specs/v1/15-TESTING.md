### Requirement 15: Automated Testing

**User Story:** As a developer, I want automated tests for the API and the main user journey, so that regressions are caught.

#### Acceptance Criteria

1. THE System SHALL include `pytest` tests for comment creation covering success, validation failure, unauthenticated, and unauthorized cases.
2. THE System SHALL include a Playwright end-to-end test of the Kanban journey that runs against the deployed URL.
3. THE System SHALL contain no `waitForTimeout` call in any Playwright test file.
4. THE System SHALL unit-test each `service.py` against a fake repository without a real database.
