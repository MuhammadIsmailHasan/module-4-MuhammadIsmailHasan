### Requirement 14: Non-Functional Quality

**User Story:** As a product owner, I want measurable performance, security, and mobile usability targets, so that quality can be verified.

#### Acceptance Criteria

1. WHILE the Backend is under normal load, THE Backend SHALL respond within 300 ms at the 95th percentile.
2. WHEN a Board with 200 Cards loads over a throttled Fast 3G connection, THE Frontend SHALL reach first meaningful paint within 2 seconds.
3. THE Backend SHALL include no `comments` or `activity` field in any Guest-facing response, including direct calls to the comment and activity endpoints.
4. WHILE the viewport width is between 360 and 414 pixels, THE Frontend SHALL show every page without horizontal scroll or cut-off or overlapping content.
5. THE Frontend SHALL write base (unprefixed) styles for a 360 to 414 pixel screen and add tablet and desktop layouts only through `min-width` variants, never a `max-width` variant that strips a desktop layout down for mobile.
6. WHILE the viewport is below 960 pixels, THE Frontend SHALL show the Sidebar as an off-canvas drawer behind a scrim with its toggle in a persistent header.
7. WHILE the viewport is 960 pixels or wider, THE Frontend SHALL keep the Sidebar visible.
8. THE Frontend SHALL place each primary action (add card, open Inbox, switch Board) within a persistent header or the bottom third of the screen on mobile.
9. THE Frontend SHALL take all colors, spacing, radii, and shadows from the Design_Tokens, exposed to Tailwind through its theme, and SHALL NOT use Tailwind's default palette, arbitrary values such as `bg-[#fff]` or `p-[13px]`, or hard-coded hex or pixel values in components, and SHALL NOT write numeric literals for sizes, layers (z-index), durations, or opacities: every such value is a named token utility (Decision H).
10. THE Frontend SHALL build shared buttons, badges, and modals only as `BaseButton`, `BaseBadge`, and `BaseModal` in `components/shared/`, implemented as thin wrappers over the shadcn/ui `Button`, `Badge`, and `Dialog` primitives, and no other file SHALL import the shadcn/ui primitives directly (Decision H).
11. THE Frontend SHALL render components as Server Components unless a component needs state, an event handler, or a browser API.
12. WHEN a list endpoint returns rows, THE Backend SHALL execute a number of database queries that does not depend on the number of returned rows, so that the board cards list with Subtasks and Attachments loads in at most a fixed number of queries instead of one query per Card (Decision F).
13. THE Frontend SHALL style components with Tailwind CSS and shadcn/ui primitives copied into `components/ui/`, themed from the Design_Tokens so the look follows the product owner's visual reference (light surfaces, navy brand, pastel tags, icon rail, flat columns), and MAY refine spacing, motion, and visual hierarchy without changing that palette, layout, or the interaction patterns (Decision H).
14. THE Frontend SHALL set the Tailwind `lg` breakpoint to 960 pixels so the Sidebar drawer behaviour of criteria 6 and 7 is unchanged (Decision H).
15. THE Frontend SHALL show a visible focus ring from the `--ring` token on every interactive element, and SHALL NOT remove an outline without a replacement focus style (Decision H).
