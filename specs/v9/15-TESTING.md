### Requirement 15: Automated Testing

**User Story:** As a developer, I want automated tests for the API and the main user journey, so that regressions are caught.

#### Acceptance Criteria

Criteria 1 to 9 are unchanged from V8. V9 adds criteria 10 to 15.

10. THE E2E_Auth_Suite SHALL be written in Playwright under `frontend/tests/e2e/auth/` as `signin.spec.ts` and `signout.spec.ts`, and SHALL reach every locator and action of the login page and the Sign_Out_Control only through the Auth_Page_Object (V9).
11. THE E2E_Auth_Suite SHALL read the base URL from `E2E_BASE_URL`, the Test_Account's login_identifier from `E2E_USER_IDENTIFIER`, and its password from `E2E_USER_PASSWORD`, and SHALL contain no credential literal (V9).
12. IF `E2E_BASE_URL`, `E2E_USER_IDENTIFIER`, or `E2E_USER_PASSWORD` is unset or empty, THEN THE E2E_Auth_Suite SHALL fail before the first test with an error message that names the missing variable (V9).
13. THE Frontend SHALL list `E2E_BASE_URL`, `E2E_USER_IDENTIFIER`, and `E2E_USER_PASSWORD` with empty or placeholder values in `frontend/.env.example`, and no real `.env` file SHALL be committed (V9).
14. THE E2E_Auth_Suite SHALL use web-first assertions such as `expect(locator).toBeVisible()` and `expect(page).toHaveURL()`, and SHALL contain no `waitForTimeout` call (extends criterion 3) (V9).
15. THE E2E_Auth_Suite SHALL start every test in a fresh browser context with no Session_Cookie, SHALL create no account or other data, and SHALL leave the Test_Account unchanged (V9).
