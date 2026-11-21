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
## V9 - 2026-11-20
### Changes
- `v9/` holds the changed domains: `01-AUTH` (criteria 19 to 38: sign-in and sign-out end-to-end criteria with IDs `AUTH-E2E-SI-01` to `-10` and `AUTH-E2E-SO-01` to `-08`, new Glossary terms, Open Questions 5 to 7), `15-TESTING` (criteria 10 to 15: suite files, environment variables, `.env.example`, no `waitForTimeout`, test isolation).
### Reason
- The product owner asked for Playwright end-to-end specifications for sign-in and sign-out, happy and negative cases.
### Impact
- Specification and test additions only; no behaviour, API, or schema change. Criteria SO-03 and SO-05 are pending Open Question 5 (no Frontend route guard exists; `/boards` is open to Guests).
## V10 - 2026-11-20
### Changes
- `v10/` holds the changed domains: `00-OVERVIEW` (Decisions K to P, new and changed Glossary terms, Open Questions 1, 3, 5, 6 resolved and 7 to 13), `01-AUTH` (criteria 1 to 5, 11, 17, 18 reworded or withdrawn; 19 to 37 updated for the new login form, header sign-out, and route guard; 39 to 54 added), `03-BOARDS` (23, 25), `04-CARDS` (26), `06-CATEGORIES` (6), `07-COMMENTS` (16), `08-ACTIVITY-LOG` (5), `11-VISIBILITY` (4, 5, 7 reworded; 13 added), `12-SEARCH-FILTER` (6, 7), `13-API-CONVENTIONS` (3, 10, 11), `14-NON-FUNCTIONAL` (3, 10, 26 reworded; 27 added), `15-TESTING` (7, 11, 15 reworded; 16 to 19 added), `17-API-DOCS` (1), and the new domains `18-SHARE-LINKS`, `19-APP-HEADER-PROFILE`, `20-RATE-LIMITING`.
### Reason
- Guests no longer browse public Boards (share links instead); one header user menu; separate Username and Email; rate limiting; every signed-in page guarded; V9 e2e criteria brought in line.
### Impact
- Breaking API changes: login field `identifier`; register fields `username` and `email`; `user` shape; Guest requests to board routes return 401 (comment endpoints 401 instead of 403); candidate search fields; 429 `RATE_LIMITED`; `error.details` on a registration 409; Signed_File_URL signature scope. Database revision `b7d2e4f6a801` (reversible in part). Full list in `.kiro/specs/CHANGELOG.md` V10.
- Earlier version folders are unchanged.
### V10 round 2 (same version; V10 is specified but not implemented, so there is no V11)
- `v10/00-OVERVIEW` (Decisions Q to T; Decisions L, M, O, P annotated; Glossary: Avatar_Image, Avatar_URL, Initials_Avatar, Safe_Return_Path; Open Questions 7, 8, 10, 12 resolved, 14 to 16 added), `v10/01-AUTH` (1.6, 1.34, 1.37 reworded; 55 to 62 added: invalid or expired Token on any request, tests AUTH-E2E-SO-11 and -12), `v10/03-BOARDS` (25 reworded; 30 to 32 added: Email to staff), `v10/04-CARDS` (33 reworded: assignee popover with Email), `v10/13-API-CONVENTIONS` (10), `v10/14-NON-FUNCTIONAL` (28), `v10/15-TESTING` (16 reworded; 20 to 24 added), `v10/18-SHARE-LINKS` (24), `v10/19-APP-HEADER-PROFILE` (8 to 10 reworded; 18 to 33 added: avatar upload), `v10/20-RATE-LIMITING` (7 withdrawn; 8, 10, 15 reworded; 18 added: registration not limited).
- Impact: no `RATE_LIMIT_REGISTER_MAX` and no register limiter; avatar upload endpoints and `avatar_path` replace the `https` avatar URL; `GET /api/boards/{id}/candidates` and `GET /api/boards/{id}/members?include=email` return `email` to staff; an unusable Token ends on `/login` with the cookie removed. Full list in `.kiro/specs/CHANGELOG.md`, "Round 2 within V10".
- Open for the owner: the availability limiter was kept by the specifier (Open Question 14); avatar visibility (15); Email exposure through name search (16).
### V10 round 3 (same version; amendment)
- `v10/00-OVERVIEW` (Decisions U to W; Open Questions 9, 11, 13 to 18 resolved), `v10/01-AUTH` (1.6 reworded; 1.52, 1.53 withdrawn; 1.63, 1.64 added), `v10/03-BOARDS`, `v10/04-CARDS`, `v10/07-COMMENTS`, `v10/12-SEARCH-FILTER`, `v10/15-TESTING` (16, 18, 24 reworded; 25 to 27 added), `v10/17-API-DOCS` (11), `v10/18-SHARE-LINKS` (11, 25), `v10/19-APP-HEADER-PROFILE` (avatar routes under `/api/users`; 13, 14 withdrawn; 34 to 40 added), `v10/20-RATE-LIMITING` (change-password limiter, 19 to 23).
- Impact: avatar routes move to `/api/users/me/avatar`; `avatar_url` appears in Comment, member, candidate, and assignee payloads for signed-in viewers (Guests: initials); the V10 migration resets local development data and the seed fills username, email, and full_name; change-password is rate limited; candidate search needs 2 characters.
- Still open: Open Questions 19 to 21 (V11). Details in `.kiro/specs/CHANGELOG.md`, "Round 3 within V10".
## V11 - 2026-11-21
### Changes
- `v11/` holds the changed domains: `00-OVERVIEW` (Decision X, Glossary terms Brand_Assets, Logo_Mark, Logo_Full, BrandLogo, Embedded_Raster, Favicon_File, Open Questions 19 to 21), `14-NON-FUNCTIONAL` (criteria 16, 19, 26 reworded), `15-TESTING` (criterion 28 added), and the new domain `21-BRANDING` (BRAND-01 to BRAND-17: favicon through the Next.js file convention, logos in `public/brand/` shown only through `BrandLogo` with `next/image` and `unoptimized`, alt text, sizes, Sidebar, sign-in pages, header, tests).
### Reason
- The product owner supplied the RevoTask logo and favicon to replace the placeholder mark.
### Impact
- No API, data model, or permission change. Frontend only.
- Finding: both SVG logos wrap a PNG (640 by 640 and 720 by 220 pixels, no alpha), so they are not true vector art (Open Question 19). Only `favicon.ico` is supplied (Open Question 20).
- V10 round 3 is applied separately; `v10/` is unchanged by V11. Full list in `.kiro/specs/CHANGELOG.md`, V11.

