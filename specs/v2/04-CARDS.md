### Requirement 4: Cards

**User Story:** As a team member, I want cards with description, subtasks, priority, dates, and attachments, so that I can capture and track a piece of work in one place.

#### Acceptance Criteria

1. WHEN a Card_Creator with Board_Staff_Access to a Board creates a Card in a Column of that Board, THE Backend SHALL store the Card with a title, a description, a Priority of `high`, `medium`, or `low`, a Float `order`, and nullable `start_date`, `end_date`, `category_id`, and `assignee_id` (Decision A).
2. IF a Card is submitted with a Priority other than `high`, `medium`, or `low`, THEN THE Backend SHALL return HTTP 400 with the code `VALIDATION_ERROR`.
3. IF a Card is submitted with an `end_date` earlier than its `start_date`, THEN THE Backend SHALL return HTTP 400 with the code `VALIDATION_ERROR`.
4. IF an authenticated user who is not a Card_Creator with Board_Staff_Access attempts to create a Card, THEN THE Backend SHALL return HTTP 403, or HTTP 401 when no Token is present (Decision A).
5. WHEN a Card_Creator with Board_Staff_Access deletes a Card, THE Backend SHALL Soft_Delete the Card by setting `deleted_at`.
6. WHEN a Card_Creator with Board_Staff_Access archives a Card, THE Backend SHALL set the Card's `archived_at` and allow the archive to be reversed.
7. IF an authenticated Member attempts to create, delete, or archive a Card, THEN THE Backend SHALL return HTTP 403, or HTTP 401 when no Token is present.
8. WHEN a Member with Board_Access edits a Card assigned to that Member, THE Backend SHALL apply the edit (Decisions 2 and A).
9. IF a Member edits a Card whose `assignee_id` is not that Member, THEN THE Backend SHALL return HTTP 403 (Decision 2).
10. WHEN a Supervisor, Manager, or Admin with Board_Staff_Access to the Card's Board edits any Card on that Board, THE Backend SHALL apply the edit (Decision A).
11. WHEN a Supervisor, Manager, or Admin with Board_Staff_Access assigns a Card to a user, THE Backend SHALL set the Card's `assignee_id` and create an `assigned` Notification for that user in the same transaction.
12. WHEN a user with edit rights on a Card (Board_Staff_Access for a Supervisor, Manager, or Admin; Board_Access as the Assigned_Member for a Member) adds a Subtask to that Card, THE Backend SHALL store the Subtask with a title, `is_done` defaulting to false, and a Float `order`.
13. WHEN a user with edit rights on a Card toggles a Subtask's `is_done` or reorders it, THE Backend SHALL persist the change through `PATCH /api/subtasks/{id}`, setting a Subtask dropped between two siblings to the average of their `order` values, the first position to `min_order - 1`, the last position to `max_order + 1`, an empty checklist's first Subtask to 1.0, and renumbering the whole checklist as 1.0, 2.0, ... in the same transaction when the gap between adjacent `order` values falls below 1e-6.
14. WHEN a user with edit rights on a Card (Board_Staff_Access for a Supervisor, Manager, or Admin; Board_Access as the Assigned_Member for a Member) deletes a Subtask, THE Backend SHALL remove the Subtask through `DELETE /api/subtasks/{id}`.
15. WHEN a user with edit rights on a Card (Board_Staff_Access for a Supervisor, Manager, or Admin; Board_Access as the Assigned_Member for a Member) adds an Attachment, THE Backend SHALL store either a `url` or a `file_path` with `mime_type`.
16. IF an Attachment has neither a `url` nor a `file_path`, THEN THE Backend SHALL return HTTP 400 with the code `VALIDATION_ERROR`.
17. IF an uploaded Attachment file type is not PDF, Word, or RAR, THEN THE Backend SHALL return HTTP 400 with the code `VALIDATION_ERROR`.
18. THE Backend SHALL serve each uploaded Attachment file through an authenticated endpoint or a Signed_File_URL that enforces the same Board_Access and role rules as the owning Card, and SHALL NOT expose a permanently public, unauthenticated URL (Decision D).
19. WHEN a user clicks an Attachment, THE Frontend SHALL open it with `target="_blank"` and `rel="noopener noreferrer"` and provide no in-app preview, and for a file Attachment whose Signed_File_URL has expired, THE Frontend SHALL request a fresh URL from `GET /api/attachments/{id}/url` before opening it (Decision D).
20. WHEN a user opens a Card, THE Frontend SHALL show one two-pane modal used for both viewing and editing, with title, description, Priority, dates, Attachments, the Subtask checklist, and the Card's Activity_Log in the left pane and the Comment thread and composer in the right pane.
21. WHEN a user saves the left pane, THE Frontend SHALL commit the Card changes without closing the modal and without affecting the Comment composer.
22. THE Frontend SHALL render the Subtask checklist as a flat list of checkboxes with inline-editable titles and a drag handle for reordering.
23. THE Backend SHALL never hard-delete a row from the Card table.
24. THE Backend SHALL set each Signed_File_URL to expire 15 minutes after issue (Decision D).
25. IF a request to the file route carries a bad, modified, or expired file signature, THEN THE Backend SHALL return HTTP 403, because the file route takes no Token (Decision D).
26. WHEN a viewer with Board_Access to the Card, including a Guest on a public Board, requests `GET /api/attachments/{id}/url`, THE Backend SHALL return a fresh Signed_File_URL (Decision D).
27. THE Backend SHALL return a link-type Attachment's `url` as stored (Decision D).
28. WHEN a Supervisor, Manager, or Admin with Board_Staff_Access sets a Card's `assignee_id` to null, THE Backend SHALL clear the assignment, write one `card.unassigned` Activity_Log row in the same transaction, and create no Notification.
29. THE Backend SHALL carry no `deleted_at` on Subtask, Attachment, or Comment rows and SHALL hide them by joining the parent Card's `deleted_at`.
