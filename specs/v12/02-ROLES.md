# Roles, V12 changes

Requirement 2 criterion 4 no longer lists "set Board visibility" (Boards have no visibility). The five roles and Decision B are unchanged.

## Access matrix

See the matrix in `.kiro/specs/design.md`, section "V12 Design: Access matrix (V12)". Summary:

- Board access: owner, Board_Member, Manager, Admin. Everyone else: 403 (401 without a Token).
- Public_Link management: Manager and Admin only. Invite_Link management: Board_Owner, Manager, Admin. Join_Request decisions: Manager and Admin only. The owner sees pending requests.
- Direct add of a Board_Member and the candidate search: Manager and Admin only, Member and Supervisor accounts only.
- A Manager or an Admin is never a Board_Member.
- A Member edits only Cards assigned to the Member, including all Subtask actions on them (Requirement 27, criterion 1).
- A Comment can be deleted only by its author; Admin cannot comment (Decision B).

### Requirement 2 criteria with V12 labels

Criteria of Requirement 2 that V12 changed. Each line is the full V1 to V11 criterion followed by its V12 label; the label wins.

4. THE Backend SHALL permit an Admin to view all Boards, Cards, Comments, and Activity_Log entries, manage user accounts, create and assign Boards, archive and Soft_Delete Boards, set Board visibility, manage Categories, and move and edit any Card (Decision 5). (V12: "set Board visibility" no longer exists; Decision Y.)
