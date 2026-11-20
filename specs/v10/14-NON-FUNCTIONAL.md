### Requirement 14: Non-Functional Quality

**User Story:** As a product owner, I want measurable performance, security, and mobile usability targets, so that quality can be verified.

#### Acceptance Criteria

V10 changes: criterion 3 reworded (shared responses, Guest 401), criterion 10 reworded (`BaseMenu`), criterion 26 reworded (Username in the Sidebar), criterion 27 added (route guard, Decision P). All other criteria are unchanged from V8. **Round 2 within V10:** criterion 28 added (invalid Token treated as signed out; Decision T).

3. THE Backend SHALL include no `comments`, `activity`, or `activity_log` field in any shared route response, and SHALL return HTTP 401 to a Guest who calls a comment or activity endpoint directly (Decision K; reworded in V10).
10. THE Frontend SHALL build shared buttons, badges, modals (with a header, a scrolling body, and a footer slot), popovers, calendars, tooltips, searchable selects, and menus only as `BaseButton`, `BaseBadge`, `BaseModal`, `BasePopover`, `BaseCalendar`, `BaseTooltip`, `BaseCombobox`, and, from V10, `BaseMenu` in `components/shared/`, implemented as thin wrappers over the shadcn/ui `Button`, `Badge`, `Dialog`, `Popover`, `Calendar`, `Tooltip`, `Command`, and `DropdownMenu` primitives, and no other file SHALL import the shadcn/ui primitives directly (Decisions H and I).
26. THE Frontend SHALL give the Sidebar one type hierarchy: the brand at 16 pixels semibold, navigation items 14 pixels medium, Board rows 14 pixels regular, section labels 11 pixels uppercase muted, member names 13 pixels medium with the Username 12 pixels muted (V10; was the login), with every item the same height and left padding (Decision I).
27. THE Frontend SHALL treat every page of the `(app)` route group as a Protected_Route: WHEN a request for such a page carries no Session_Cookie, THE Frontend SHALL redirect to `/login` before the page renders through `frontend/proxy.ts`, and SHALL NOT guard `/login`, `/register`, or `/shared/{token}` (Decision P).

28. THE Frontend SHALL treat a malformed, expired, or Backend-rejected Session_Cookie on a Protected_Route as signed out: it ends on `/login`, removes the cookie, and keeps the Safe_Return_Path, as Requirement 1, criteria 57 to 61 define (Decision T).
