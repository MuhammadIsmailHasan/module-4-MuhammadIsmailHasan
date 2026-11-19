# Changelog

Versions match `.kiro/specs/CHANGELOG.md`. Each folder holds requirement domains only; `v1` is the full baseline and later folders hold only changed domains.

## V1 - Initial Release
- Full requirements baseline in `v1/`, one file per domain (`00-OVERVIEW` to `16-STRETCH`).
- Snapshot of the requirements as generated before the V2 decisions.

## V2 - 2026-11-18
### Changes
- `v2/` holds the domains that changed: `00-OVERVIEW` (decisions log, glossary), `01-AUTH`, `02-ROLES`, `03-BOARDS`, `04-CARDS`, `05-DRAG-AND-DROP`, `06-CATEGORIES`, `07-COMMENTS`, `08-ACTIVITY-LOG`, `09-NOTIFICATIONS`, `10-ANALYTICS`, `11-VISIBILITY`, `12-SEARCH-FILTER`, `13-API-CONVENTIONS`, `15-TESTING`.
- Unchanged from V1: `14-NON-FUNCTIONAL`, `16-STRETCH`.
- Board membership and `Board_Staff_Access` (Decision A), intentional Admin exclusions recorded (Decision B), single `login_identifier` (Decision C), signed and time-limited attachment URLs (Decision D), and the secondary defaults listed in `.kiro/specs/CHANGELOG.md`.

### Reason
- Resolve the product owner's decisions A to D and the gaps found in review of V1.

### Impact
- Breaking: `email_or_username` renamed to `login_identifier`; attachment `file_url` is now signed and expires; a tokenless Guest on a private board gets 401 instead of 403.
- Open: `login_identifier` format validation, the public-board reading of Decision A, and attachment delivery cost.

## V3 - 2026-11-18
### Changes
- `v3/17-API-DOCS.md`: new Requirement 17 (API documentation: OpenAPI, `API.md`, Swagger UI gated by `APP_ENV`). Original V3 wording used a hand-written `openapi.yaml`; V4 supersedes it.

### Reason
- The backend had no written API reference. This folder was added after the fact so every version has a snapshot.

## V4 - 2026-11-18
### Changes
- `v4/` holds the changed domains: `00-OVERVIEW` (Decision E, glossary), `01-AUTH`, `07-COMMENTS`, `10-ANALYTICS` (envelope examples), `13-API-CONVENTIONS` (status/message, flask-smorest), `17-API-DOCS` (generated OpenAPI).

### Reason
- Add `status` and `message` to every response and use flask-smorest for schemas and responses.

### Impact
- Breaking: the response body shape changes from `{ data }` to `{ status, message, data }`; 422 validation errors are mapped to 400.


## V5 - 2026-11-18
### Changes
- `v5/` holds the changed domains: `00-OVERVIEW` (Decision F), `13-API-CONVENTIONS` (relationship and no-`to_dict` rules), `14-NON-FUNCTIONAL` (constant query count), `15-TESTING` (query-count and `lazy="raise"` tests).

### Reason
- Keep list endpoints inside the 300 ms p95 target and keep serialization out of models.

### Impact
- No API or schema change; no migration.

## V6 - 2026-11-18
### Changes
- `v6/` holds the changed domains: `00-OVERVIEW` (Decision G, glossary), `01-AUTH`, `07-COMMENTS`, `10-ANALYTICS` (envelope examples), `13-API-CONVENTIONS` (boolean `status`, single `message`, `error.details`).

### Reason
- Remove the duplicated message on errors and make `status` a success flag.

### Impact
- Breaking: `status` changes from a number to a boolean; `error.message` is removed; validation errors add `error.details`.

## V7 - 2026-11-19
### Changes
- `v7/` holds the changed domains: `00-OVERVIEW` (Decision H, glossary: Design_Tokens and shadcn/ui) and `14-NON-FUNCTIONAL` (criteria 5, 9, 10 reworded; 13 to 15 added: Tailwind CSS and shadcn/ui themed from the design tokens, `lg` = 960px, focus ring from `--ring`).

### Reason
- Style the frontend with Tailwind CSS and the shadcn/ui design system. The visual reference is the product owner's light project-management dashboard (white surfaces, navy brand, pastel tags, icon rail); the prototype stays the reference for behaviour and content.

### Impact
- Frontend only: no API or schema change. The `Base*` components become wrappers over shadcn/ui; direct imports of shadcn/ui elsewhere and arbitrary Tailwind values are forbidden.

## V8 - 2026-11-19
### Changes
- `v8/` holds the changed domains: `00-OVERVIEW` (Decision I, introduction), `03-BOARDS` (criteria 20 to 22: visibility icons, wrapped names, Home page), `04-CARDS` (criteria 20 and 21 reworded; 30 to 38 added: chips and popovers, range calendar, start-not-after-end guard, assignee popover, no column select, footer, two-column attachments, subtasks card, pane scrolling), `05-DRAG-AND-DROP` (criterion 2 reworded; 13 added: HTML5 drag on scrolling column bodies), `07-COMMENTS` (criterion 21: `author_name`), `08-ACTIVITY-LOG` (criterion 8: `actor_name`), `14-NON-FUNCTIONAL` (criteria 7 and 10 reworded; 16 to 19 added: Sidebar collapse with the logo toggle, Inter, viewport-locked board, RevoTask name and small radii).

### Reason
- The product owner asked for the Trello board and card experience.

### Impact
- Frontend only: no API or schema change. The Card modal loses its column select; cards move only by drag-and-drop (HTML5 API). The API gains two additive fields: `actor_name` on activity rows and `author_name` on comments and replies.

### V8 round 3 (same version, uncommitted)
- `v8/04-CARDS` (criteria 20, 35, 36 reworded; 39 and 40 added), `v8/08-ACTIVITY-LOG` (criteria 9 and 10 added: activity metadata and wording), `v8/14-NON-FUNCTIONAL` (criteria 20 to 22 added: control and type scale, tooltip behaviour, board card sizes), `v8/00-OVERVIEW` (Decision I "where applied").
- Impact: additive `metadata` keys on new Activity_Log rows (backend); the rest is frontend.

### V8 round 4 (same version, uncommitted)
- `v8/00-OVERVIEW` (Decision J, Decision I "where applied"), `v8/03-BOARDS` (23 to 25), `v8/04-CARDS` (21 and 35 reworded; 41 to 45), `v8/06-CATEGORIES` (13), `v8/07-COMMENTS` (22), `v8/08-ACTIVITY-LOG` (11, 12), `v8/09-NOTIFICATIONS` (11, 12), `v8/13-API-CONVENTIONS` (19), `v8/14-NON-FUNCTIONAL` (10 and 20 reworded; 23 to 26).
- Impact: paging on three endpoints (additive query parameters, same response shape), a new candidates endpoint, and a frontend visual system pass.

### V8 round 5 (same version, uncommitted)
- `v8/03-BOARDS` (23 reworded; 26 to 29), `v8/04-CARDS` (46 to 50), `v8/06-CATEGORIES` (14), `v8/10-ANALYTICS` (8), `v8/00-OVERVIEW` (Decision I "where applied").
- Impact: a migration for `Board.description` and four computed counts on the board list; the rest is frontend.
- Round 5 amendment: `v8/03-BOARDS` criterion 29 drops the cover band (plain bordered tile).
