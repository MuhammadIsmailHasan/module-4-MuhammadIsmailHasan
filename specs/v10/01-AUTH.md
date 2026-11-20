### Requirement 1: Authentication and Accounts

**User Story:** As a visitor, I want to register and sign in with an email or username and password, so that I can access boards according to my role.

#### Acceptance Criteria
**Round 3 within V10 (Decisions U to W):** criterion 6 reworded (avatars in more payloads); 52 and 53 withdrawn (no legacy backfill, no Email_Prompt); 63 and 64 added (local reset migration, seed data).

V10 changes: criteria 1 to 5 reworded (Username, Email, `identifier`, 409 with `error.details`); criterion 11 reworded; criterion 17 withdrawn (Decision M); criterion 18 superseded (Decision O, Requirement 20); criteria 19 to 37 updated for the new login form, the header sign-out, the route guard, and the User_Menu_Trigger; criteria 39 to 54 added. Criteria 6 to 10, 12 to 16, and 38 are unchanged from V9. **Round 2 within V10:** criterion 6 reworded (Avatar_Image, `avatar_path`; Decision R); criteria 34 and 37 reworded; criteria 55 to 62 added (invalid or expired Token on any request, Decision T; tests AUTH-E2E-SO-11 and -12 and rules TOK-01 to TOK-06).

1. WHEN a visitor submits a registration with full name, Username, Email, and password, THE Backend SHALL create a user account with a hashed password and return HTTP 201 with `{ "status": true, "message": "User registered", "data": { "user": { id, full_name, username, email, avatar_url }, "token": "..." } }` (Decisions G, M, and N; reworded in V10).
2. WHEN a registered user submits a valid `identifier` (a Username or an Email) and password to login, THE Backend SHALL return the same `user` and `token` shape as registration, matching the identifier case-insensitively (Decisions M and N; reworded in V10).
3. IF the `identifier` matches no account or the password is wrong, THEN THE Backend SHALL return HTTP 401 with the same error Envelope and the same message in both cases (Decision N; reworded in V10).
4. IF a registration uses a Username or an Email that already exists when compared case-insensitively, THEN THE Backend SHALL return HTTP 409 with the code `CONFLICT` and an `error.details` object that names each duplicate field (`username`, `email`, or both) with a list of message strings (Decisions M and O; reworded in V10).
5. IF a registration omits full name, Username, Email, or password, or a field fails the format rules of criteria 47 and 48, THEN THE Backend SHALL return HTTP 400 with the code `VALIDATION_ERROR` and an `error.details` entry for each failing field (Decision M; reworded in V10).
6. THE Backend SHALL store the user's Avatar_Image reference as a nullable `avatar_path` and SHALL expose it as `avatar_url` in the `user` payload and in the payloads of criterion 34 of Requirement 19 (Decisions R and U; reworded in V10 rounds 2 and 3).
11. THE System SHALL exclude Google OAuth login until Username-or-Email and password authentication is verified end-to-end.
17. [Withdrawn in V10, Decision M] The provisional "no format validation" rule for `login_identifier` no longer applies; criteria 47 and 48 define the formats.
18. [Superseded in V10, Decision O] Rate limiting is no longer deferred; Requirement 20 defines it.
The criteria below specify the Playwright tests of the E2E_Auth_Suite (V9, updated in V10 to the new login form, the header sign-out, the route guard, and the rate limit). They add no product behaviour: each one verifies behaviour specified in criteria 1.2, 1.3, 1.5, 1.9, 1.10, 1.15, 1.16, 1.44 to 1.46, 1.51, Requirements 13, 19, and 20, and Decisions L, N, O, and P. No criterion is pending in V10. Assumptions: the Test_Account exists and is a Member; the specs run against the deployed Frontend and Backend; the login form posts through `lib/api.ts`; each test starts in a fresh browser context with no Session_Cookie; the suite shows "signed in" by the User_Menu_Trigger. Each criterion has a stable ID, and the matching test title begins with that ID.
**Sign-in, happy cases**
The criteria below specify the Playwright tests of the E2E_Auth_Suite (V9, updated in V10 to the new login form, the header sign-out, the route guard, and the rate limit). They add no product behaviour: each one verifies behaviour specified in criteria 1.2, 1.3, 1.5, 1.9, 1.10, 1.15, 1.16, 1.44 to 1.46, 1.51, Requirements 13, 19, and 20, and Decisions L, N, O, and P. No criterion is pending in V10. Assumptions: the Test_Account exists and is a Member; the specs run against the deployed Frontend and Backend; the login form posts through `lib/api.ts`; each test starts in a fresh browser context with no Session_Cookie; the suite shows "signed in" by the User_Menu_Trigger. Each criterion has a stable ID, and the matching test title begins with that ID.

**Sign-in, happy cases**

19. [AUTH-E2E-SI-01] WHEN a visitor submits the Test_Account's Username or Email and password on `/login`, THE Frontend SHALL navigate to `/boards` and show the User_Menu_Trigger.
20. [AUTH-E2E-SI-02] WHEN a visitor submits the Test_Account's Username or Email with every letter upper-cased and the correct password, THE Frontend SHALL navigate to `/boards` and show the User_Menu_Trigger (criterion 2, Decision M).
21. [AUTH-E2E-SI-03] WHILE a Test_Account is signed in, WHEN the visitor reloads `/boards`, THE Frontend SHALL stay on `/boards` and show the User_Menu_Trigger.
22. [AUTH-E2E-SI-04] WHEN a Test_Account signs in successfully, THE Frontend SHALL set the Session_Cookie.
23. [AUTH-E2E-SI-05] WHILE the viewport is 360 pixels wide, WHEN a visitor opens `/login`, THE Frontend SHALL show the login form with the single "Username or email" field and hide the brand panel (criterion 10).

**Sign-in, negative cases**

24. [AUTH-E2E-SI-06] IF a visitor submits the Test_Account's Username or Email with a wrong password, THEN THE Frontend SHALL stay on `/login`, show the Generic_Login_Error, and set no Session_Cookie (criterion 3).
25. [AUTH-E2E-SI-07] IF a visitor submits a Username-shaped Identifier that belongs to no account (a Throwaway_Identifier), THEN THE Frontend SHALL stay on `/login`, show the same Generic_Login_Error text as criterion 24, and set no Session_Cookie.
26. [AUTH-E2E-SI-08] IF a visitor submits the login form with an empty "Username or email" field and an empty password, THEN THE Frontend SHALL stay on `/login`, show a validation message beside each of the two fields, send no request, and set no Session_Cookie (criterion 5).
27. [AUTH-E2E-SI-09] IF a visitor submits an Identifier of 256 characters without `@`, THEN THE Frontend SHALL stay on `/login`, show a username-shape validation message beside the "Username or email" field, send no request, and set no Session_Cookie (criterion 51).
28. [AUTH-E2E-SI-10] WHEN a visitor submits the login form, THE Frontend SHALL keep the password out of the page URL and out of the visible page text, and SHALL render the password field with `type="password"`.

**Sign-out, happy cases**

29. [AUTH-E2E-SO-01] WHEN a signed-in Test_Account opens the User_Menu and activates the Sign_Out_Control, THE Frontend SHALL navigate to `/login` (criterion 16).
30. [AUTH-E2E-SO-02] WHEN a signed-in Test_Account opens the User_Menu and activates the Sign_Out_Control, THE Frontend SHALL remove the Session_Cookie and send `POST /api/auth/logout` once (criteria 15 and 16).
31. [AUTH-E2E-SO-03] WHEN a Test_Account has signed out and the visitor opens a Protected_Route, THE Frontend SHALL redirect to `/login` (Decision P).
32. [AUTH-E2E-SO-04] WHEN a Test_Account has signed out and the visitor navigates back in the browser history, THE Frontend SHALL end on `/login` and show no User_Menu_Trigger and no signed-in user name (Decision P).

**Sign-out and session, negative cases**

33. [AUTH-E2E-SO-05] IF a visitor without a Session_Cookie opens a Protected_Route, THEN THE Frontend SHALL redirect to `/login` before the page renders (Decision P).
34. [AUTH-E2E-SO-06] IF a request made by a signed-in Frontend returns HTTP 401 for an expired or invalid Token, THEN THE Frontend SHALL remove the Session_Cookie and navigate to `/login` (design: `lib/api.ts`; server renders: criteria 57 and 58, Decision T).
35. [AUTH-E2E-SO-07] IF `POST /api/auth/logout` fails with a network error or HTTP 500, THEN THE Frontend SHALL still remove the Session_Cookie and navigate to `/login` (criterion 16).
36. [AUTH-E2E-SO-08] IF `POST /api/auth/logout` returns HTTP 401 because the Token has expired, THEN THE Frontend SHALL remove the Session_Cookie and end on `/login` without a redirect loop.

**Traceability**

37. THE E2E_Auth_Suite SHALL give every test a title that begins with the stable ID of the criterion it verifies, and SHALL contain exactly one test per ID in criteria 19 to 36, 39 to 42, 55, and 56.
38. THE E2E_Auth_Suite SHALL contain no test for registration, role permissions, or Google OAuth.

**V10 additions to the suite**

39. [AUTH-E2E-SI-11] IF a visitor submits a Throwaway_Identifier with a wrong password until the Rate_Limiter blocks the pair, THEN THE Frontend SHALL show the wait time, disable the submit button, send no further login request while the button is disabled, and set no Session_Cookie (Requirement 20, Decision O). The test makes at most 10 attempts (Requirement 15, criterion 19) and never uses the Test_Account.
40. [AUTH-E2E-SI-12] IF a visitor submits an Identifier that contains `@` but is not a valid Email, THEN THE Frontend SHALL stay on `/login`, show an email-shape validation message beside the "Username or email" field, send no request, and set no Session_Cookie (criterion 51).
41. [AUTH-E2E-SO-09] WHEN a signed-in Test_Account opens the User_Menu, THE Frontend SHALL list the Profile item above the Sign_Out_Control (criterion 2 of Requirement 19, Decision L).
42. [AUTH-E2E-SO-10] WHILE a Test_Account is signed in, THE Frontend SHALL show no Log out item and no Profile entry in the Sidebar (Decision L).

**Account identity (V10)**

43. [USR-01] THE Backend SHALL store a User `username` and a User `email`, each unique when compared case-insensitively through a unique index on the lower-cased value, and SHALL have no `login_identifier` column after the V10 migration (Decision M).
44. [USR-02] WHEN a login request carries an `identifier` that contains `@` and has a valid Email shape, THE Backend SHALL look the user up by `email`, case-insensitively (Decision N).
45. [USR-03] WHEN a login request carries an `identifier` without `@` that matches the Username format, THE Backend SHALL look the user up by `username`, case-insensitively (Decision N).
46. [USR-04] IF a login `identifier` is empty, contains `@` without a valid Email shape, or has no `@` and does not match the Username format, THEN THE Backend SHALL return HTTP 400 with the code `VALIDATION_ERROR` and an `error.details` entry for `identifier`, count no attempt in the Rate_Limiter, and look up no user (Decision N).
47. [USR-05] WHEN the Backend receives a Username, THE Backend SHALL trim it, lower-case it, and accept it only if it has 3 to 30 characters, each one of `a-z`, `0-9`, `_`, or `.`; otherwise THE Backend SHALL return HTTP 400 with the code `VALIDATION_ERROR` and an `error.details` entry for `username` (Decision M).
48. [USR-06] WHEN the Backend receives an Email, THE Backend SHALL trim it, lower-case it, and accept it only if it is at most 255 characters and has a valid Email shape (one `@`, a non-empty local part, a domain with at least one dot, no spaces; no DNS lookup); otherwise THE Backend SHALL return HTTP 400 with the code `VALIDATION_ERROR` and an `error.details` entry for `email` (Decision M).
49. [USR-07] WHEN a visitor calls `GET /api/auth/availability` with `username`, `email`, or both, THE Backend SHALL return `{ "username": { "available": boolean }, "email": { "available": boolean } }` with an entry for each supplied parameter, and SHALL return HTTP 400 with the code `VALIDATION_ERROR` when neither is supplied or a supplied value fails criterion 47 or 48 (Decision M).
50. [USR-08] WHEN a visitor leaves the Username or Email field of the register form, THE Frontend SHALL call the availability endpoint and show the result beside that field; WHEN the Backend answers 409 on submit, THE Frontend SHALL show each `error.details` message beside its field, and the 409 SHALL stay authoritative over an earlier "available" result (Decision M).
51. [USR-09] THE Frontend SHALL show the login form as one "Username or email" field and one password field; WHEN the value contains `@`, THE Frontend SHALL validate the Email shape, and otherwise THE Frontend SHALL validate the Username shape, and SHALL send a request only when the value is valid (Decision N).
52. [USR-10] [Withdrawn in V10 round 3, Decision V] The legacy `login_identifier` backfill and the sanitized-Username rule no longer apply, because the application is not deployed and the migration resets local development data (criterion 63). The ID stays so that references do not move.
53. [USR-11] [Withdrawn in V10 round 3, Decision V] No account has a null Email, so the Frontend shows no Email_Prompt. The ID stays so that references do not move.
54. [USR-12] WHEN an Admin creates or edits a user account through `POST /api/users` or `PATCH /api/users/{id}`, THE Backend SHALL accept and validate `username` and `email` by criteria 47 and 48, apply the uniqueness rule of criterion 4, and return the `user` shape of criterion 1 (Decision M).

**Invalid or expired Token on any request (V10 round 2, Decision T)**
55. [AUTH-E2E-SO-11] IF a visitor whose Session_Cookie holds a value that is not a decodable Token (for example the text `bogus`) opens `/boards`, THEN THE Frontend SHALL end on the login page and remove the Session_Cookie (criterion 57).
56. [AUTH-E2E-SO-12] IF a visitor whose Session_Cookie holds a well-formed Token with a future expiry and an invalid signature opens `/boards`, THEN THE Frontend SHALL end on the login page, remove the Session_Cookie, and make no further request to a Protected_Route after the redirect (criterion 58).
57. [TOK-01] WHEN a request for a Protected_Route carries a Session_Cookie whose value is not three dot-separated base64url segments, whose payload is not a JSON object with a string `sub`, a string `role`, and a numeric `exp`, or whose `exp` is not later than the current time, THE Frontend SHALL answer through `frontend/proxy.ts` with a redirect to `/login` that carries the Safe_Return_Path as `next` and SHALL remove the Session_Cookie in that same response; the proxy SHALL NOT verify the signature, because only the Backend holds the signing secret.
58. [TOK-02] IF the Backend answers a server render of a Protected_Route with HTTP 401 while a Session_Cookie is present, THEN THE Frontend SHALL redirect to the route handler `/session-expired` with the Safe_Return_Path, and that handler SHALL remove the Session_Cookie and redirect to `/login` with the same `next`; a server render that gets HTTP 403 SHALL NOT remove the Session_Cookie.
59. [TOK-03] WHEN login succeeds, THE Frontend SHALL navigate to the Safe_Return_Path given in `next`, and to `/boards` when `next` is absent or is not a Safe_Return_Path.
60. [TOK-04] WHILE the visitor is on `/login`, `/register`, or `/shared/{token}`, THE Frontend SHALL ignore a stale Session_Cookie: no redirect and no cookie removal on arrival (Requirement 18, criterion 24).
61. [TOK-05] THE route handler `/session-expired` SHALL redirect only to `/login`, and `/login` SHALL NOT redirect to a Protected_Route without a user action, so that an invalid Token cannot cause a redirect loop.
62. [TOK-06] WHERE criteria 31, 33, 34, 55, and 56 say the visitor ends on `/login`, THE E2E_Auth_Suite SHALL compare the URL path only, so that a `next` query parameter does not fail the test.
63. [USR-13] WHEN the V10 migration runs and `APP_ENV` is `development` or `testing`, THE Backend SHALL delete every row of `users` and of each table that references it (Boards, BoardMembers, Cards with their Subtasks and Attachments, Comments, Notifications, Activity_Log rows, and rate-limit rows), add `username` and `email` as NOT NULL columns with the unique lower-case indexes of criterion 43, add `boards.share_token` and `rate_limit_attempts`, replace `avatar_url` with `avatar_path`, drop `login_identifier`, and print one line saying that local data was reset and that `flask seed-users` or `flask seed-data` recreates it, without backfilling any legacy value (Decision V); IF `APP_ENV` has any other value or is unset, THEN THE migration SHALL abort before it changes anything, with a message that names `APP_ENV`. Uploaded files under `UPLOAD_DIR` are not touched.
64. [USR-14] WHEN the seed commands `flask seed-users` and `flask seed-data` create a user, THE Backend SHALL set `username`, `email`, and `full_name` on it for every seeded user: the Member, Supervisor, Manager, and Admin of `seed-users`, and `member2` and `supervisor2` of `seed-data`, using the Username `<key>`, the Email `<key>@example.com`, and a two-word full name such as "Member One"; the Member `member` is the Test_Account of the E2E_Auth_Suite (`E2E_USER_IDENTIFIER=member`). Running a seed command twice SHALL create no duplicate (Decision V).
