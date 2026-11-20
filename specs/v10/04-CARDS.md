### Requirement 4: Cards

**User Story:** As a team member, I want cards with description, subtasks, priority, dates, and attachments, so that I can capture and track a piece of work in one place.

#### Acceptance Criteria
**Round 3 within V10 (Decisions U to W):** criterion 33 reworded (the assignee popover shows the avatar).

V10 changes: criterion 26 reworded (a Guest obtains Signed_File_URLs only through the shared route). All other criteria are unchanged from V8. **Round 2 within V10:** criterion 33 reworded (the assignee popover shows full name and Email through `?include=email`, hidden from a Member; Decision S).

26. WHEN a signed-in viewer with Board_Access to the Card requests `GET /api/attachments/{id}/url`, THE Backend SHALL return a fresh Signed_File_URL; a Guest obtains one only through the shared route of Requirement 18 (Decisions D and K; reworded in V10).

33. THE Frontend SHALL pick the assignee in a small popover with a search box, the Board's members (Avatar_Image or Initials_Avatar, full name, and Email, loaded through `GET /api/boards/{id}/members?include=email`), a single choice, and a Remove action, with the search box matching full name, Username, and Email case-insensitively, and SHALL hide the control from a Member, who may not assign (Decisions I and S; the Backend rule is criterion 11).
