### Requirement 14: Non-Functional Quality

**User Story:** As a product owner, I want measurable performance, security, and mobile usability targets, so that quality can be verified.

#### Acceptance Criteria

V11 changes (Decision X): criteria 16, 19, and 26 reworded; every other criterion is unchanged from `specs/v10/14-NON-FUNCTIONAL.md`.

16. THE Frontend SHALL give the Sidebar a toggle, which is the BrandLogo at its top (V11, Requirement 21, criterion 8), that switches between an expanded state (icons with text labels, with the Boards list and team members below them) and a collapsed state (the icon rail only, the logo mark alone with the tooltip RevoTask, and every other icon with a tooltip shown on hover and on focus), the expanded state showing Logo_Full (the mark with the RevoTask wordmark), SHALL remember the choice in the browser, and SHALL keep the off-canvas drawer below 960 pixels unchanged (Decision I).
19. THE Frontend SHALL name the application RevoTask in the Sidebar (through Logo_Full), the page titles, and the sign-in pages (through BrandLogo, Requirement 21), and SHALL keep corner radii small (no more than 10 pixels on Cards, Columns, buttons, and the modal) through the radius tokens (Decision I).
26. THE Frontend SHALL give the Sidebar one type hierarchy: the brand shown as the BrandLogo image (no text size, V11), navigation items 14 pixels medium, Board rows 14 pixels regular, section labels 11 pixels uppercase muted, member names 13 pixels medium with the Username 12 pixels muted (V10; was the login), with every item the same height and left padding (Decision I).
