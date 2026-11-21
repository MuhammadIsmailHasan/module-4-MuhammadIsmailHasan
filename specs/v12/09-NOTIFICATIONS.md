# Notifications, V12 changes

### Requirement 28: Inbox Navigation and Notification Types

**User Story:** As a signed-in user, I want to open what a notification is about with one click, so that I land on the right Card or Board instead of hunting for it.

Note (V12, Decision AE): this requirement amends Requirement 9 (types and links) and Glossary Notification. A Notification of type `deadline` or `assigned` keeps its V2 rules.

#### Acceptance Criteria

1. [INB-01] THE Backend SHALL store each Notification with `type` (`assigned`, `deadline`, `board_join_requested`, `board_added`, or `board_join_rejected`), nullable `card_id`, nullable `board_id` (always set by the Backend on new rows), nullable `actor_id`, nullable `join_request_id`, `notify_date`, `is_read` (default false), and `created_at`, with a CHECK that a card type has a `card_id` and a board type has a `board_id` and no `card_id` (Decision AE).
2. [INB-02] THE Backend SHALL deduplicate Notifications with three partial unique indexes: `(user_id, card_id, type, notify_date)` where `card_id IS NOT NULL`; `(user_id, type, join_request_id)` where `join_request_id IS NOT NULL`; and `(user_id, type, board_id, notify_date)` where `card_id IS NULL AND join_request_id IS NULL`, so that rows with a null `card_id` stay deduplicated, every join request notifies once per user, and a null never makes two rows distinct (Decision AE).
3. [INB-03] WHEN a Manager or an Admin makes a Supervisor the Board_Owner of a Board (Requirement 22, criterion 12), THE Backend SHALL create one `board_added` Notification for that Supervisor with `board_id` and the actor in the same transaction.
4. [INB-04] THE Backend SHALL return on each Notification in `GET /api/notifications`: `id`, `type`, `board_id`, `board_name`, `card_id`, `card_title`, `actor_name`, `is_read`, and `created_at`, loading names in a fixed number of queries whatever the number of rows, and SHALL return no Email.
5. [INB-05] THE Frontend SHALL render each Inbox row as one link whose `href` is `/boards/{board_id}?card={card_id}` for `assigned` and `deadline`, `/boards/{board_id}?invite=1` for `board_join_requested`, `/boards/{board_id}` for `board_added`, and `/boards` for `board_join_rejected` (the requester has no access to the Board), so that the row is reachable and activatable by keyboard (Enter) and by middle click (Decision AE).
6. [INB-06] WHEN the user activates an Inbox row, THE Frontend SHALL send `PATCH /api/notifications/{id}/read`, lower the unread count at once, navigate without waiting for the response, and close the Side_Panel.
7. [INB-07] WHEN the Board page opens with `?card=<id>`, THE Frontend SHALL open that Card's modal after the Board loads, and WHEN the modal closes THE Frontend SHALL remove the parameter.
8. [INB-08] IF the Card of `?card=` is soft-deleted, unknown, or on another Board, THEN THE Frontend SHALL show the notice "This card is no longer available." above the Board and open no modal; IF the Card is archived, THEN THE Frontend SHALL show "This card is archived." and open no modal.
9. [INB-09] IF the Board answers HTTP 403 or HTTP 404 for a Notification target, THEN THE Frontend SHALL show a page with the message "You no longer have access to this board, or it was removed." and a link to Home, never a blank page or the raw error.
10. [INB-10] WHEN the Board page opens with `?invite=1` and the viewer is the Board_Owner, a Manager, or an Admin, THE Frontend SHALL open the Invite modal on the pending-request list (Requirement 24, criterion 19); for any other viewer THE Frontend SHALL ignore the parameter.
11. [INB-11] THE Frontend SHALL write each new Notification type as a sentence naming the actor and the Board: "Ada Lovelace asked to join "Board name"", "You were added to "Board name"", and "Your request to join "Board name" was declined".

### Requirement 9 criteria with V12 labels

Criteria of Requirement 9 that V12 changed. Each line is the full V1 to V11 criterion followed by its V12 label; the label wins.

1. WHEN a Card is assigned to a user, THE Backend SHALL insert a Notification of type `assigned` for that user in the same transaction as the assignment. (V12: Notification types `board_join_requested`, `board_added`, and `board_join_rejected` are added, Requirement 28.)
6. WHEN a user clicks Inbox in the Sidebar or clicks the header bell, THE Frontend SHALL open the Side_Panel on the Inbox view through the same toggle. (V12: each Inbox row is a link, Requirement 28, criteria 5 and 6.)
