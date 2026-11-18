### Requirement 7: Comments

**User Story:** As a team member, I want threaded comments with manager priority flags, so that important discussion stays on top and managers can turn their own comments into cards.

#### Acceptance Criteria

1. WHEN a Member, Supervisor, or Manager posts to `POST /api/cards/{id}/comments` on a Card the user can view, THE Backend SHALL create a top-level Comment.
2. IF a Comment body is missing or empty, THEN THE Backend SHALL return HTTP 400 with the code `VALIDATION_ERROR` and the message `content is required`.
3. IF a Guest or an Admin attempts to create a Comment, THEN THE Backend SHALL return HTTP 403, or HTTP 401 when no Token is present.
4. WHEN a Member, Supervisor, or Manager posts to `POST /api/comments/{id}/replies` targeting a top-level Comment, THE Backend SHALL create the Reply and increment the parent's Reply_Count in the same transaction.
5. IF the target of a reply request has a non-null `parent_id`, THEN THE Backend SHALL return HTTP 400.
6. THE Backend SHALL provide no like or vote endpoint in the comments domain.
7. WHEN a Manager calls `PATCH /api/comments/{id}/priority` on any Comment, THE Backend SHALL toggle that Comment's `is_priority`.
8. IF a user who is not a Manager calls `PATCH /api/comments/{id}/priority`, THEN THE Backend SHALL return HTTP 403.
9. WHEN `GET /api/cards/{id}/comments` is called, THE Backend SHALL return Priority_Comments first, ordered newest priority first, followed by the remaining top-level Comments in the requested order.
10. WHEN the `sort` parameter is `latest` or omitted, THE Backend SHALL order the remaining top-level Comments newest first.
11. WHEN the `sort` parameter is `popular`, THE Backend SHALL order the remaining top-level Comments by Reply_Count descending, with ties broken by `created_at` descending.
12. THE Backend SHALL return each top-level Comment's Replies nested inline, ordered oldest first, regardless of the `sort` parameter.
13. THE Backend SHALL include `reply_count`, `is_priority`, and `can_create_card` on every returned Comment.
14. WHEN the viewer is a Supervisor, Manager, or Admin and the Comment's author role is manager, THE Backend SHALL set `can_create_card` to true regardless of `is_priority`.
15. IF the viewer is a Member or Guest, or the Comment's author role is not manager, THEN THE Backend SHALL set `can_create_card` to false.
16. IF a Guest requests a Card's Comments, THEN THE Backend SHALL return no `comments` field, including on direct calls to the comment endpoints.
17. THE Frontend SHALL render Priority_Comments first with a priority indicator, then the remaining top-level Comments under a visible Latest and Popular toggle that shows the Reply_Count as a badge.
18. THE Frontend SHALL show a Reply action only on top-level Comments.
19. WHERE `can_create_card` is true on a Comment, THE Frontend SHALL show the "create new card" action on that Comment.
20. WHERE the Card response omits `comments`, THE Frontend SHALL omit the Comment thread.
