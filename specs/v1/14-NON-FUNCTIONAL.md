### Requirement 14: Non-Functional Quality

**User Story:** As a product owner, I want measurable performance, security, and mobile usability targets, so that quality can be verified.

#### Acceptance Criteria

1. WHILE the Backend is under normal load, THE Backend SHALL respond within 300 ms at the 95th percentile.
2. WHEN a Board with 200 Cards loads over a throttled Fast 3G connection, THE Frontend SHALL reach first meaningful paint within 2 seconds.
3. THE Backend SHALL include no `comments` or `activity` field in any Guest-facing response, including direct calls to the comment and activity endpoints.
4. WHILE the viewport width is between 360 and 414 pixels, THE Frontend SHALL show every page without horizontal scroll or cut-off or overlapping content.
5. THE Frontend SHALL write base styles for a 360 to 414 pixel screen and add tablet and desktop layouts through `min-width` media queries.
6. WHILE the viewport is below 960 pixels, THE Frontend SHALL show the Sidebar as an off-canvas drawer behind a scrim with its toggle in a persistent header.
7. WHILE the viewport is 960 pixels or wider, THE Frontend SHALL keep the Sidebar visible.
8. THE Frontend SHALL place each primary action (add card, open Inbox, switch Board) within a persistent header or the bottom third of the screen on mobile.
9. THE Frontend SHALL use the prototype's CSS custom properties for all colors, spacing, and radii and no hard-coded hex or pixel values.
10. THE Frontend SHALL build shared buttons, badges, and modals only as `BaseButton`, `BaseBadge`, and `BaseModal` in `components/shared/`.
11. THE Frontend SHALL render components as Server Components unless a component needs state, an event handler, or a browser API.
