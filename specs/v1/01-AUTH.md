### Requirement 1: Authentication and Accounts

**User Story:** As a visitor, I want to register and sign in with an email or username and password, so that I can access boards according to my role.

#### Acceptance Criteria

1. WHEN a visitor submits a registration with full name, email or username, and password, THE Backend SHALL create a user account with a hashed password and return `{ "data": { "user": { id, full_name, email_or_username, avatar_url }, "token": "..." } }`.
2. WHEN a registered user submits valid credentials to login, THE Backend SHALL return the same `user` and `token` shape as registration.
3. IF login credentials are invalid, THEN THE Backend SHALL return HTTP 401 with an error Envelope.
4. IF a registration uses an email or username that already exists, THEN THE Backend SHALL return HTTP 409 with an error Envelope.
5. IF a registration omits full name, email or username, or password, THEN THE Backend SHALL return HTTP 400 with the code `VALIDATION_ERROR`.
6. THE Backend SHALL store the user's `avatar_url` as nullable.
7. WHEN an Admin creates, edits, or assigns a role to a user account, THE Backend SHALL apply the change and record it in the Activity_Log.
8. IF a user who is not an Admin requests user account management, THEN THE Backend SHALL return HTTP 403.
9. THE Frontend SHALL present the login and register pages as a split-panel layout with a brand panel beside an elevated rounded form card on desktop widths.
10. WHILE the viewport is at mobile width, THE Frontend SHALL hide the brand panel on the login and register pages and show only the form.
11. THE System SHALL exclude Google OAuth login from V1 until email or username and password authentication is verified end-to-end.
