### Requirement 9: Notifications and Inbox

**User Story:** As a member, I want to be notified when a card is assigned to me or reaches its deadline, so that I do not miss work.

#### Acceptance Criteria

1. WHEN a Card is assigned to a user, THE Backend SHALL insert a Notification of type `assigned` for that user in the same transaction as the assignment.
2. WHEN the scheduled daily job runs, THE Backend SHALL create one `deadline` Notification for the Assigned_Member of each Card whose `end_date` equals today in the APP_TIMEZONE timezone and whose `deleted_at` is null, using no per-user timezone.
3. WHEN the scheduled daily job runs more than once on the same date, THE Backend SHALL create no duplicate `deadline` Notification for the same Card and assignee.
4. THE Backend SHALL create Notifications on the server and the Frontend SHALL not compute or poll them client-side.
5. WHEN a signed-in user requests the Inbox, THE Backend SHALL return only that user's Notifications and an unread count that reflects read-marking through criteria 8 and 9.
6. WHEN a user clicks Inbox in the Sidebar or clicks the header bell, THE Frontend SHALL open the Side_Panel on the Inbox view through the same toggle.
7. WHERE the API response omits Inbox data, THE Frontend SHALL omit the Inbox panel.
8. WHEN a signed-in user calls `PATCH /api/notifications/{id}/read` on one of the user's own Notifications, THE Backend SHALL mark that Notification read.
9. WHEN a signed-in user calls `PATCH /api/notifications/read-all`, THE Backend SHALL mark all of that user's own Notifications read.
10. IF a user calls `PATCH /api/notifications/{id}/read` on another user's Notification, THEN THE Backend SHALL return HTTP 404.
