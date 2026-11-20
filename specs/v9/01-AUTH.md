### Requirement 1: Authentication and Accounts

**User Story:** As a visitor, I want to register and sign in with an email or username and password, so that I can access boards according to my role.

#### Acceptance Criteria

Criteria 1 to 18 are unchanged from V8 (`v2/01-AUTH.md` and later). V9 adds criteria 19 to 38 (specification and test additions, no behaviour change).
The criteria below specify the Playwright tests of the E2E_Auth_Suite (V9). They add no product behaviour: each one verifies behaviour already specified in criteria 1.2, 1.3, 1.5, 1.9, 1.10, 1.15, 1.16, and Requirement 13 (Decision G), except where marked pending. Assumptions: the Test_Account exists and is a Member; the specs run against the deployed Frontend and Backend; the login form posts through `lib/api.ts`; each test starts in a fresh browser context with no Session_Cookie. Each criterion has a stable ID, and the matching test title begins with that ID.

**Sign-in, happy cases**

19. [AUTH-E2E-SI-01] WHEN a visitor submits the Test_Account's `login_identifier` and password on `/login`, THE Frontend SHALL navigate to `/boards` and show the Sign_Out_Control.
20. [AUTH-E2E-SI-02] WHEN a visitor submits the Test_Account's `login_identifier` with every letter upper-cased and the correct password, THE Frontend SHALL navigate to `/boards` and show the Sign_Out_Control (criterion 2, Decision C).
21. [AUTH-E2E-SI-03] WHILE a Test_Account is signed in, WHEN the visitor reloads `/boards`, THE Frontend SHALL stay on `/boards` and show the Sign_Out_Control.
22. [AUTH-E2E-SI-04] WHEN a Test_Account signs in successfully, THE Frontend SHALL set the Session_Cookie.
23. [AUTH-E2E-SI-05] WHILE the viewport is 360 pixels wide, WHEN a visitor opens `/login`, THE Frontend SHALL show the login form and hide the brand panel (criterion 10).

**Sign-in, negative cases**

24. [AUTH-E2E-SI-06] IF a visitor submits the Test_Account's `login_identifier` with a wrong password, THEN THE Frontend SHALL stay on `/login`, show the Generic_Login_Error, and set no Session_Cookie (criterion 3).
25. [AUTH-E2E-SI-07] IF a visitor submits a `login_identifier` that belongs to no account, THEN THE Frontend SHALL stay on `/login`, show the same Generic_Login_Error text as criterion 24, and set no Session_Cookie.
26. [AUTH-E2E-SI-08] IF a visitor submits the login form with an empty `login_identifier` and an empty password, THEN THE Frontend SHALL stay on `/login`, show a validation message beside each of the two fields, and set no Session_Cookie (criterion 5).
27. [AUTH-E2E-SI-09] IF a visitor submits a `login_identifier` of 256 characters, THEN THE Frontend SHALL stay on `/login`, show a validation message beside the `login_identifier` field, and set no Session_Cookie (criterion 5).
28. [AUTH-E2E-SI-10] WHEN a visitor submits the login form, THE Frontend SHALL keep the password out of the page URL and out of the visible page text, and SHALL render the password field with `type="password"`.

**Sign-out, happy cases**

29. [AUTH-E2E-SO-01] WHEN a signed-in Test_Account activates the Sign_Out_Control, THE Frontend SHALL navigate to `/login` (criterion 16).
30. [AUTH-E2E-SO-02] WHEN a signed-in Test_Account activates the Sign_Out_Control, THE Frontend SHALL remove the Session_Cookie and send `POST /api/auth/logout` once (criteria 15 and 16).
31. [AUTH-E2E-SO-03] WHEN a Test_Account has signed out and the visitor opens a Protected_Route, THE Frontend SHALL redirect to `/login` (pending Open Question 5).
32. [AUTH-E2E-SO-04] WHEN a Test_Account has signed out and the visitor navigates back in the browser history, THE Frontend SHALL show no Sign_Out_Control and no signed-in user name.

**Sign-out and session, negative cases**

33. [AUTH-E2E-SO-05] IF a visitor without a Session_Cookie opens a Protected_Route, THEN THE Frontend SHALL redirect to `/login` (pending Open Question 5).
34. [AUTH-E2E-SO-06] IF a request made by a signed-in Frontend returns HTTP 401 for an expired or invalid Token, THEN THE Frontend SHALL remove the Session_Cookie and navigate to `/login` (design: `lib/api.ts`; server renders are covered by Open Question 7).
35. [AUTH-E2E-SO-07] IF `POST /api/auth/logout` fails with a network error or HTTP 500, THEN THE Frontend SHALL still remove the Session_Cookie and navigate to `/login` (criterion 16).
36. [AUTH-E2E-SO-08] IF `POST /api/auth/logout` returns HTTP 401 because the Token has expired, THEN THE Frontend SHALL remove the Session_Cookie and end on `/login` without a redirect loop.

**Traceability**

37. THE E2E_Auth_Suite SHALL give every test a title that begins with the stable ID of the criterion it verifies, and SHALL contain exactly one test per ID in criteria 19 to 36.
38. THE E2E_Auth_Suite SHALL contain no test for registration, role permissions, or Google OAuth.

#### Glossary terms added in V9

- **E2E_Auth_Suite**: The Playwright specs `frontend/tests/e2e/auth/signin.spec.ts` and `frontend/tests/e2e/auth/signout.spec.ts`, which test sign-in and sign-out against the deployed URL (V9).
- **Test_Account**: A seeded, existing user whose `login_identifier` and password are supplied to the E2E_Auth_Suite through the environment variables `E2E_USER_IDENTIFIER` and `E2E_USER_PASSWORD`. The suite assumes a Member account and never creates, edits, or deletes accounts (V9).
- **Auth_Page_Object**: The Page Object class `AuthPage` in `frontend/tests/e2e/auth/pages/AuthPage.ts` that holds every locator and action of the login page and the Sign_Out_Control, so the specs contain no raw selectors (V9).
- **Sign_Out_Control**: The "Log out" item of the Sidebar, whose label includes the signed-in user's full name. It is the only sign-out control in the current Frontend (see Open Question 6).
- **Session_Cookie**: The browser cookie `kanban_token` that holds the Token (`lib/session.ts`). A signed-out browser has no such cookie.
- **Generic_Login_Error**: The form-level message "Invalid credentials" that the Backend returns for both an unknown login_identifier and a wrong password (`auth_service.login`).
- **Protected_Route**: A Frontend page that requires a Token and redirects a visitor without one to `/login`. The Frontend defines no such route yet (see Open Question 5).

#### Open questions added in V9

5. **Route guard (V9):** No Frontend route redirects a visitor without a Token to `/login`. `/boards` is deliberately open to a Guest, who sees public Boards (Req 3, 11.4), and `(app)/layout.tsx` renders for a Guest. Criteria 1.31 and 1.33 therefore depend on a Protected_Route that is not specified. Options: (a) keep Guest access, define the first Token-only page (the Admin users screen, task 19.2, or a private Board URL) as the Protected_Route and guard it; (b) guard all of `/boards`, which contradicts Req 11.4 and the Guest user story. Recommendation: (a). Until the product owner decides, criteria 1.31 and 1.33 are marked "(pending Open Question 5)" and their tests are written with `test.fixme`.
6. **Sign-out control location (V9):** The product request describes sign-out "from the header user control". The Board header shows the bell, avatar, and name (Req 3.23) but no sign-out action; sign-out exists only as the Sidebar "Log out" item (`Sidebar.tsx`). The criteria target the Sidebar item. Moving sign-out into the header is a behaviour change and needs its own decision.
7. **Invalid Token on a server render (V9):** `lib/api.ts` redirects to `/login` on a 401 only for client-side calls made while a Session_Cookie is present. Whether a server render (`serverGet`) with an invalid or expired Session_Cookie redirects, shows the Guest view, or fails is not specified. Criterion 1.34 covers the client-side call only.
