### Requirement 2: Roles and Permissions

**User Story:** As a system owner, I want strictly layered roles enforced on the server, so that each user can reach only the actions their role allows.

Note (Decision B): Admin is a separate administration track and is deliberately not a superset of Manager. The Admin exclusions in criteria 5 and in Requirement 10 criterion 4 are intentional and must not be changed as a "fix".

#### Acceptance Criteria

1. THE Backend SHALL support exactly five roles: guest, member, supervisor, manager, and admin.
2. THE Backend SHALL treat Manager permissions as a superset of Supervisor permissions, Supervisor permissions as a superset of Member permissions, and Member view access as a superset of Guest view access.
3. THE Backend SHALL treat Admin as a separate administration track with the permissions listed in criteria 4 to 6.
4. THE Backend SHALL permit an Admin to view all Boards, Cards, Comments, and Activity_Log entries, manage user accounts, create and assign Boards, archive and Soft_Delete Boards, set Board visibility, manage Categories, and move and edit any Card (Decision 5).
5. THE Backend SHALL deny an Admin the actions of creating a Comment and flagging a Comment as priority (Decision B).
6. THE Backend SHALL permit an Admin to create Cards, delete Cards, archive Cards, and create Columns.
7. WHEN any mutating endpoint is called, THE Backend SHALL determine the acting role from the Token and ignore any role value in the request body.
8. IF a mutating request has no valid Token, THEN THE Backend SHALL return HTTP 401 with an error Envelope.
9. IF an authenticated user calls a mutating endpoint that the user's role or Board_Access does not permit, THEN THE Backend SHALL return HTTP 403 with an error Envelope.
10. THE Backend SHALL re-validate the caller's role on 100 percent of mutating endpoints.
