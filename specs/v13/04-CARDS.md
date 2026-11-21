# Cards, V13 changes

### Requirement 30: Role Tag in the Assignee Picker

**User Story:** As a Manager or Supervisor, I want each person in the assignee list to show their role, so that I can tell a Member from a Supervisor before I assign a Card.

Note (V13, Decision AG): amends Requirement 4 criterion 33 (the assignee popover) and Requirement 22 criterion 13 (the members list). The role is not private: other users already see it in the Sidebar. The Email rule of Decision S does not change.

#### Acceptance Criteria

1. [ROLE-01] THE Backend SHALL return `role` (`member` or `supervisor`) on every row of `GET /api/boards/{id}/members`, with the other fields of Requirement 22 criterion 13 unchanged; Managers and Admins never appear in that list (Requirement 22, criterion 5), so no row carries `manager` or `admin`.
2. [ROLE-02] THE Frontend SHALL show a role tag in each row of the assignee popover, after the full name: the text "Supervisor" or "Member", drawn by `BaseBadge` (`neutral` tone for Member, `blue` for Supervisor, `tag` shape), at the badge text size, never colour alone, and the tag SHALL be part of the row's accessible name.
3. [ROLE-03] THE Frontend SHALL show the same tag on the Board_Owner row of the Sidebar Team members list beside the "Owner" tag (Requirement 22, criterion 19), and on each other row, so that the Sidebar and the picker read alike; the Email stays out of both unless Requirement 4 criterion 33 shows it to staff.
4. [ROLE-04] THE Frontend SHALL let the search of the assignee popover match the role word as well as the name, Username, and Email (for example "super"), and SHALL keep the current selection, the Unassigned row, and the keyboard behaviour of `BaseCombobox`.
5. [ROLE-05] THE Frontend SHALL show no role tag in the Shared_View and SHALL add no `role` to any `/api/shared` payload (Requirement 23, criterion 5).
