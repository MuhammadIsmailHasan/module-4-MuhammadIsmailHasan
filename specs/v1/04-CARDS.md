### Requirement 4: Cards

**User Story:** As a team member, I want cards with description, subtasks, priority, dates, and attachments, so that I can capture and track a piece of work in one place.

#### Acceptance Criteria

1. WHEN a Card_Creator creates a Card in a Column, THE Backend SHALL store the Card with a title, a description, a Priority of `high`, `medium`, or `low`, a Float `order`, and nullable `start_date`, `end_date`, `category_id`, and `assignee_id`.
2. IF a Card is submitted with a Priority other than `high`, `medium`, or `low`, THEN THE Backend SHALL return HTTP 400 with the code `VALIDATION_ERROR`.
3. IF a Card is submitted with an `end_date` earlier than its `start_date`, THEN THE Backend SHALL return HTTP 400 with the code `VALIDATION_ERROR`.
4. IF a Member, Supervisor, or Guest attempts to create a Card and the user is not a Card_Creator, THEN THE Backend SHALL return HTTP 403.
5. WHEN a Card_Creator deletes a Card, THE Backend SHALL Soft_Delete the Card by setting `deleted_at`.
6. WHEN a Card_Creator archives a Card, THE Backend SHALL set the Card's `archived_at` and allow the archive to be reversed.
7. IF a Member attempts to create, delete, or archive a Card, THEN THE Backend SHALL return HTTP 403.
8. WHEN a Member edits a Card assigned to that Member, THE Backend SHALL apply the edit.
9. IF a Member edits a Card whose `assignee_id` is not that Member, THEN THE Backend SHALL return HTTP 403.
10. WHEN a Supervisor, Manager, or Admin edits any Card on a Board visible to that user, THE Backend SHALL apply the edit.
11. WHEN a Supervisor, Manager, or Admin assigns a Card to a user, THE Backend SHALL set the Card's `assignee_id` and create an `assigned` Notification for that user in the same transaction.
12. WHEN a user adds a Subtask to a Card the user may edit, THE Backend SHALL store the Subtask with a title, `is_done` defaulting to false, and a Float `order`.
13. WHEN a user toggles a Subtask's `is_done` or reorders it, THE Backend SHALL persist the change through `PATCH /api/subtasks/{id}`.
14. WHEN a user deletes a Subtask on a Card the user may edit, THE Backend SHALL remove the Subtask through `DELETE /api/subtasks/{id}`.
15. WHEN a user adds an Attachment to a Card the user may edit, THE Backend SHALL store either a `url` or a `file_path` with `mime_type`.
16. IF an Attachment has neither a `url` nor a `file_path`, THEN THE Backend SHALL return HTTP 400 with the code `VALIDATION_ERROR`.
17. IF an uploaded Attachment file type is not PDF, Word, or RAR, THEN THE Backend SHALL return HTTP 400 with the code `VALIDATION_ERROR`.
18. THE Backend SHALL return each uploaded Attachment as a stable, directly fetchable `file_url` that the Backend does not stream through an API endpoint.
19. WHEN a user clicks an Attachment, THE Frontend SHALL open it with `target="_blank"` and `rel="noopener noreferrer"` and SHALL provide no in-app preview.
20. WHEN a user opens a Card, THE Frontend SHALL show one two-pane modal used for both viewing and editing, with title, description, Priority, dates, Attachments, the Subtask checklist, and the Card's Activity_Log in the left pane and the Comment thread and composer in the right pane.
21. WHEN a user saves the left pane, THE Frontend SHALL commit the Card changes without closing the modal and without affecting the Comment composer.
22. THE Frontend SHALL render the Subtask checklist as a flat list of checkboxes with inline-editable titles and a drag handle for reordering.
23. THE Backend SHALL never hard-delete a row from the Card table.
