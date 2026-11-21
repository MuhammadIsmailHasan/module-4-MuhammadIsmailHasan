# Overview, V13 changes

V13 revises V12 (implemented). It adds a role tag to the assignee picker (Decision AG), brings the Invite and Public link controls to the one control scale (Decision AH), and gives every page the document title `RevoTask | <name>` (Decision AI). Everything in `specs/v1/` to `specs/v12/` that this version does not name stands. No migration, no new table, one new field (`role`) on `GET /api/boards/{id}/members`.

## Decisions Log (added)

| ID | Decision | Rationale | Where applied |
|----|----------|-----------|---------------|
| AG | **Role tag in the assignee picker.** Each assignee option and each Team members row shows "Supervisor" or "Member"; the members list returns `role`. | Two people with similar names could not be told apart by role. | Requirement 30 |
| AH | **Control sizes in the Invite and Public link controls.** 40 pixel header and modal buttons; compact only in a dense row; the link field and Copy share one height. | The V12 build mixed 32 pixel buttons with 40 pixel inputs. | Requirement 31 |
| AI | **Document titles.** `RevoTask | <name>` for every page, panel, and open Card, through Next.js `metadata`. | The tab should name the brand and the place. | Requirement 32 |

## Open Questions (added)

29. **Title while a Card modal is open (V13, by default):** the title becomes `RevoTask | <Card title> · <Board name>` (TITLE-05). The owner may prefer to keep the Board title; that removes TITLE-05 only.
30. **Role tag for Managers and Admins (V13, by default):** none, because they are never Board members (Requirement 22, criterion 5). If the owner wants Managers shown as assignees, Decision Y must change first.
