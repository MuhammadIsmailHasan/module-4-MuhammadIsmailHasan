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
