### Requirement 1: Authentication and Accounts

**User Story:** As a visitor, I want to register and sign in with an email or username and password, so that I can access boards according to my role.

#### Acceptance Criteria

1. WHEN a visitor submits a registration with full name, login_identifier, and password, THE Backend SHALL create a user account with a hashed password and return `{ "data": { "user": { id, full_name, login_identifier, avatar_url }, "token": "..." } }` (Decision C).
2. WHEN a registered user submits a valid login_identifier and password to login, THE Backend SHALL return the same `user` and `token` shape as registration, matching the login_identifier case-insensitively (Decision C).
3. IF login credentials are invalid, THEN THE Backend SHALL return HTTP 401 with an error Envelope.
4. IF a registration uses a login_identifier that already exists when compared case-insensitively, THEN THE Backend SHALL return HTTP 409 with an error Envelope (Decision C).
5. IF a registration omits full name, login_identifier, or password, or the login_identifier is empty after trimming, or longer than 255 characters, THEN THE Backend SHALL return HTTP 400 with the code `VALIDATION_ERROR` (Decision C).
6. THE Backend SHALL store the user's `avatar_url` as nullable.
7. WHEN an Admin creates, edits, or assigns a role to a user account, THE Backend SHALL apply the change and record it in the Activity_Log.
8. IF an authenticated user who is not an Admin requests user account management, THEN THE Backend SHALL return HTTP 403, or HTTP 401 when no Token is present.
9. THE Frontend SHALL present the login and register pages as a split-panel layout with a brand panel beside an elevated rounded form card on desktop widths.
10. WHILE the viewport is at mobile width, THE Frontend SHALL hide the brand panel on the login and register pages and show only the form.
11. THE System SHALL exclude Google OAuth login from V2 until login_identifier and password authentication is verified end-to-end.
12. IF a registration password is shorter than 8 characters, THEN THE Backend SHALL return HTTP 400 with the code `VALIDATION_ERROR`.
13. THE Backend SHALL hash passwords with bcrypt or argon2.
14. WHEN the Backend issues a Token, THE Backend SHALL set a fixed expiry of 24 hours and keep no server-side revocation list.
15. WHEN a user calls `POST /api/auth/logout`, THE Backend SHALL return `{ "data": null }`.
16. WHEN a user logs out, THE Frontend SHALL discard the stored Token, and the issued Token SHALL remain valid until its expiry.
17. THE Backend SHALL apply no login_identifier format validation beyond trimming, a non-empty value, a maximum of 255 characters, and case-insensitive uniqueness (provisional, see Open Question 1).
18. THE System SHALL defer rate limiting past the MVP.
