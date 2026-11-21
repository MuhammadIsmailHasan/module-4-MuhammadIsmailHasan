# Comments, V12 changes

Requirement 26 (comment deletion and Attachment removal confirmation) is new.

### Requirement 26: Comment Deletion and Attachment Removal Confirmation

**User Story:** As a user, I want to delete my own comments and to be asked before an attachment is removed, so that I can retract what I wrote and never lose a file by a stray click.

Note (V12, Decision AC): `BaseConfirm` has two forms. The popover form is a small panel anchored to the trigger and is used for Delete Card, Delete Subtask, Remove Board member, Regenerate or Disable a Public_Link or Invite_Link, and Remove profile picture; Approve and Reject on a join request are not confirmed. The modal form is a centred dialog with a backdrop and focus trap and is used where the action removes content other people may rely on or removes more than one row: removing an Attachment and deleting a Comment. Requirement 4 criterion 44 is amended for Attachments only.

#### Acceptance Criteria

1. [DEL-01] WHEN a user activates Remove on an Attachment, THE Frontend SHALL open the modal form of `BaseConfirm` with the title "Remove attachment?", the Attachment's name, a danger "Remove" button, and a "Cancel" button, and SHALL call `DELETE /api/attachments/{id}` only after the user confirms (Decision AC; amends Requirement 4, criterion 44).
2. [DEL-02] WHEN the user confirms, THE Frontend SHALL remove the Attachment tile when the call returns HTTP 200; IF the call fails, THEN THE Frontend SHALL keep the tile and show the inline error with Retry beside the Attachments card.
3. [DEL-03] WHEN an Attachment with an uploaded file is removed, THE Backend SHALL delete the Attachment row and write one `card.attachment_removed` Activity_Log row in one transaction and SHALL delete the stored file after the commit.
4. [DEL-04] WHEN the author of a Comment or Reply calls `DELETE /api/comments/{id}` and still has Board_Access to the Card's Board, THE Backend SHALL delete that row and return HTTP 200 with `{ "deleted": n }`, where `n` is the number of rows removed (Decision AC).
5. [DEL-05] WHEN a Reply is deleted, THE Backend SHALL decrement the parent's `reply_count` by one in the same transaction, so that `reply_count` stays equal to the number of the parent's Replies.
6. [DEL-06] WHEN a top-level Comment that has Replies is deleted, THE Backend SHALL delete its Replies in the same transaction and return `n` equal to one plus the number of Replies.
7. [DEL-07] IF a signed-in user who is not the author calls `DELETE /api/comments/{id}`, a Manager and an Admin included, THEN THE Backend SHALL return HTTP 403; IF no Token is present THEN HTTP 401; IF the id is unknown THEN HTTP 404; and in each case THE Backend SHALL change nothing (Decision AC; Manager and Admin deletion of others' Comments is out of scope).
8. [DEL-08] WHEN a Comment or Reply is deleted, THE Backend SHALL write one `comment.deleted` Activity_Log row in the same transaction with `target_type` `card`, `target_id` the Card's id, and `metadata` holding `card_title`, `comment_id`, `is_reply`, and `deleted_replies`, and no part of the Comment's text, so that the append-only log stays intact and the removed text is not kept.
9. [DEL-09] THE Backend SHALL treat `comment.deleted` as the single documented exception to Requirement 4, criterion 29 for Comments: a Comment has no `deleted_at`, is hidden with its Card by the Card's `deleted_at`, and is physically removed only by the author's action of criterion 4; Subtask rows and Attachment rows follow Requirement 4, criterion 29 unchanged, and Activity_Log rows are never deleted (Requirement 8, criterion 2).
10. [DEL-10] WHERE the viewer is the author of a Comment or Reply on a Card they can open, THE Frontend SHALL show a Delete action on it; WHEN the user activates it, THE Frontend SHALL open the modal form of `BaseConfirm` with the title "Delete comment?" and, for a top-level Comment with Replies, the text "This also deletes its N replies." (N from `reply_count`), and SHALL remove the Comment or Reply and update the parent's reply count on HTTP 200.
11. [DEL-11] THE Frontend SHALL show no Delete action on another user's Comment and no Delete action in the Shared_View or to any viewer without Board_Access.

### Requirement 7 criteria with V12 labels

Criteria of Requirement 7 that V12 changed. Each line is the full V1 to V11 criterion followed by its V12 label; the label wins.

16. IF a Guest calls a comment endpoint, THEN THE Backend SHALL return HTTP 401 whatever the Board's visibility and SHALL return no `comments` field; no shared route returns Comments (Decision K; reworded in V10, breaking: V2 to V9 returned 403 for a Guest on a public Board). (V12: Boards have no visibility.)
