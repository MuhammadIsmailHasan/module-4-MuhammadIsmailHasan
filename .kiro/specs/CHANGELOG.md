# Changelog

## V1 - Initial Release
- Initial requirements generated from `specs/project-brief.md` and `.kiro/steering/*.md`.
- Initial implementation scope established: auth, roles, boards and columns, cards, drag-and-drop, categories, comments, activity log, notifications and inbox, analytics, board visibility and archiving, search and filter. Google OAuth is out of scope. Progress, views, and decorative tabs are stretch.
- Incorporates five user decisions: `Board.owner_id` (supervisor ownership, guest-only privacy, supervisor analytics scope); members move and edit only assigned cards; create-card action shown to supervisor, manager, and admin on manager-authored comments; board soft delete and archive limited to manager and admin; admin permissions (no commenting or priority flagging).

### Impact
- Requirements: 1 to 16 (new).
- Design: created in `.kiro/specs/design.md` (V1). Adds `Board.owner_id` to the data model, omits `updated_at` on the append-only `ActivityLog`, and adds a `(user_id, card_id, type, notify_date)` unique constraint on `Notification`. `data-model.md` steering needs a sync for these.
- Tasks: not yet created.
