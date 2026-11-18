# Requirements Document

## Introduction

This document specifies the Kanban Task Management application (Version V5). It is a role-based web app with a Flask REST API backend and a mobile-first Next.js frontend. Teams run day-to-day work on boards, columns, and cards, and supervisors and managers oversee progress through analytics without opening every board.

The requirements translate decisions already recorded in `specs/project-brief.md` and the steering documents in `.kiro/steering/`. V5 revises V4 and adds no scope beyond the decisions in the Decisions Log. Eleven decisions that resolved gaps in the brief are recorded there: Decisions 1 to 5 (carried from V1), Decisions A to D (carried from V2), Decision E (carried from V4: every response carries `status` and `message`, and the Backend uses flask-smorest with marshmallow schemas and a generated OpenAPI document), and Decision F (new in V5: models declare SQLAlchemy relationships only for real cross-table reads, repositories load related rows explicitly, and serialization belongs to marshmallow schemas). Criteria affected by a decision carry an inline label such as "(Decision A)".

Out of scope for V2: Google OAuth login (post-MVP, added only after login_identifier and password auth is verified end-to-end), rate limiting and server-side token revocation (deferred past MVP), custom per-board workflow templates beyond the five default columns, and subtasks with their own assignee or date. Stretch features (card `progress` meter, `views_count`, decorative Overview/Notes/Questions tabs) are covered in Requirement 16 and are built only after all other requirements work end-to-end.

This feature requires three data-model additions beyond the current `data-model.md` steering: a nullable `Board.owner_id` (Decision 1), a `BoardMember` entity (Decision A), and a single unique, case-insensitive `login_identifier` column on User in place of separate email and username columns (Decision C).

## Glossary

- **System**: The Kanban Task Management application, consisting of the Backend and the Frontend.
- **Backend**: The Flask REST API, organized as one blueprint per domain, each layered `routes.py → service.py → repository.py → schema.py`.
- **Frontend**: The mobile-first Next.js (App Router, TypeScript) application.
- **Guest**: A visitor without an account or Token. Can view the columns and cards of public boards only.
- **Member**: A signed-in user with the member role.
- **Supervisor**: A signed-in user with the supervisor role. Includes everything a Member can do.
- **Manager**: A signed-in user with the manager role. Includes everything a Supervisor can do.
- **Admin**: A signed-in user with the admin role, a separate administrative track and not a superset of Manager (see Requirement 2 and Decision B).
- **Card_Creator**: A Supervisor, Manager, or Admin. Card creation additionally requires Board_Access to the target Board.
- **login_identifier**: The single unique, case-insensitive string column on User used for registration and login. Its value may have an email shape or a username shape.
- **Board**: A project container holding Columns, Cards, and Categories. Has `visibility` (`public` or `private`) and a nullable `owner_id`.
- **Board_Owner**: The Supervisor referenced by a Board's `owner_id`.
- **BoardMember**: A join record `(board_id, user_id)`, unique per pair, that attaches a user to a Board beyond the Board's `owner_id`.
- **Board_Access**: A user has Board_Access to a Board when the Board is public, or the user is its Board_Owner, a BoardMember, a Manager, or an Admin. For a private Board, a Supervisor has Board_Access only as owner or BoardMember, and a Member only as BoardMember. Card, Comment, Attachment, Activity_Log, and Category access always resolves through the owning Board's Board_Access.
- **Board_Staff_Access**: Write access to a Board's content. A user has Board_Staff_Access when the user is a Manager, an Admin, or a Supervisor who is the Board's Board_Owner or a BoardMember. A Supervisor who is neither owner nor BoardMember has no Board_Staff_Access, even on a public Board. Board_Access remains the read-access term and is also the access a Member needs (as BoardMember on a private Board).
- **Column**: An ordered list within a Board that contains Cards.
- **Default_Columns**: The five Columns `Todo`, `In Progress`, `Review`, `Revision`, `Done`, in that order, seeded on every new Board.
- **Card**: A unit of work with a title, description, priority, optional start and end dates, optional Category, optional assignee, Subtasks, and Attachments.
- **Assigned_Member**: The user referenced by a Card's `assignee_id`.
- **Priority**: A Card attribute that is exactly one of `high`, `medium`, or `low`.
- **Subtask**: A checklist item of a Card with a title, `is_done` flag, and Float `order`. Has no assignee and no dates.
- **Attachment**: A link (`url`) or an uploaded file (`file_path` and `mime_type`) belonging to a Card. Never has both empty.
- **Signed_File_URL**: A time-limited, signature-bearing URL for an uploaded Attachment file, valid for 15 minutes.
- **Category**: A per-Board label with a name and nullable color, shown as a filter chip.
- **Comment**: A message on a Card. A top-level Comment has a null `parent_id`. A Reply has a non-null `parent_id`.
- **Reply**: A Comment whose `parent_id` references a top-level Comment.
- **Priority_Comment**: A Comment with `is_priority` set to true.
- **Reply_Count**: The denormalized `reply_count` integer on a top-level Comment.
- **Activity_Log**: The append-only `ActivityLog` table recording state-changing actions.
- **Notification**: A server-created record targeting one user, of type `assigned` or `deadline`.
- **Inbox**: The side panel listing the signed-in user's Notifications.
- **Side_Panel**: The right-side sliding panel shared by Inbox and Activity.
- **Sidebar**: The left navigation holding brand, nav (including Inbox, Activity, and Categories where permitted), the Boards list, team members, and profile.
- **Analytics_Summary**: A pre-aggregated payload of counts, deltas, and overdue totals for a Board.
- **Overdue_Card**: A non-soft-deleted Card whose `end_date` is before today and whose Column is not `Done`.
- **Envelope**: The response shape `{ "status", "message", "data" }` for success and `{ "status", "message", "error": { "code", "message" } }` for failure, where `status` is the HTTP status code as an integer and `message` is a non-empty string.
- **flask-smorest**: The Flask extension through which every blueprint declares request, query, and response marshmallow schemas and from which the OpenAPI 3 document is generated.
- **Soft_Delete**: Setting `deleted_at` on a row instead of removing the row.
- **Token**: The JWT returned by register and login, identifying the acting user and role, with a fixed 24-hour expiry.
- **APP_TIMEZONE**: The environment variable holding the application's configured server timezone.

## Decisions Log

| ID | Decision | Rationale | Where applied |
|----|----------|-----------|---------------|
| 1 | `Board.owner_id` is nullable and references the owning Supervisor. | Supervisor ownership and analytics scope need a real column. | Req 3.2, 3.16 to 3.19, 10.1, 10.2 |
| 2 | Members move and edit only Cards assigned to them. | Keeps Member authority narrow. | Req 4.8, 4.9, 5.4, 5.5 |
| 3 | The create-card action shows to Supervisor, Manager, and Admin on Manager-authored Comments. | Matches the "create from a manager's comment" workflow. | Req 7.14, 7.15 |

Note on Decision 3: Req 7.14 stands as written (viewer is a Supervisor, Manager, or Admin and the Comment's author is a Manager). The backend, product, and frontend steering documents were aligned to it.
| 4 | Board soft-delete and archive are Manager and Admin only. | Boards are records of real work. | Req 3.6, 3.7, 11.8, 11.9 |
| 5 | Admin permission set: view all, manage users and Boards, create and delete Cards, create Columns; no Comments or priority flags. | Defines the Admin track. | Req 2.4 to 2.6 |
| A | Private Boards require Board_Access (owner, BoardMember, Manager, or Admin). Public Boards stay readable by every signed-in user. | "Private" must gate unrelated signed-in users, not only Guests. Interpretation: the request's wording omitted "private", but the stated problem concerns private Boards, so public Boards remain open to signed-in users. **Pending confirmation by the product owner.** | Req 3.4, 3.11 to 3.19, 4, 5, 6, 7, 8, 11.2, 11.6, 11.11, 11.12, 12 |

Clarification to Decision A (V2): Req 3.4 and 11.2 grant Supervisor writes only as owner or BoardMember, while Req 4 and 6 said "Board_Access", which a Supervisor also holds on any public Board. That wording gap is resolved by the Board_Staff_Access term (Glossary). Supervisor, Manager, and Admin writes (Card create, delete, archive, assign, unassign, edit, move; Subtask and Attachment writes by staff; Category create, rename, delete) require Board_Staff_Access, so an unrelated Supervisor cannot write on a public Board. Members keep Board_Access plus the assignee rule (Decision 2). Reads and Comments keep Board_Access.
| B | Admin is deliberately excluded from commenting and priority flagging (Req 2.5) and from analytics (Req 10.4). Admin is a separate administration track, not a superset of Manager. This is a recorded decision, not an oversight. Future editors must not "fix" it. | Changing it would quietly alter the permission model. | Req 2.5, Req 2 note, 7.3, 10.4 |
| C | One unified `login_identifier` field replaces separate email and username. Uniqueness and login matching are case-insensitive. | One column means one uniqueness check and one login lookup. | Req 1.1 to 1.5, 1.17, Glossary |
| D | Uploaded Attachment files are access-gated through an authenticated endpoint or a Signed_File_URL. No permanent public URL. | A permanent public URL bypasses Board_Access and role checks. | Req 4.18, 4.19, 4.24 to 4.27 |
| E | Every response carries top-level `status` (HTTP status integer) and `message`; the Backend uses flask-smorest with marshmallow schemas, validation failures stay HTTP 400 `VALIDATION_ERROR` (not 422), and the OpenAPI document is generated instead of hand-written. | One declaration per endpoint drives validation, serialization, and documentation, so they cannot drift; the body alone states the outcome. | Req 13.2 to 13.4, 13.11 to 13.15, 17 |
| F | Models declare SQLAlchemy relationships only for real cross-table reads (`Board.columns`, `Board.members`, `Card.subtasks`, `Card.attachments`, `Comment.replies`), each with `back_populates` (not `backref`), `lazy="raise"`, and no cascade delete. Repositories load related rows explicitly with `selectinload` or `joinedload`. Models have no `to_dict`; marshmallow schemas serialize, because output depends on the viewer. | An accidental lazy load fails loudly instead of becoming a hidden N+1 query, and viewer-dependent serialization stays in one place. | Req 13.16 to 13.18, 14.12, 15.8, 15.9 |

Notes on status codes: V2 standardizes "no Token returns 401; valid Token with insufficient role or access returns 403". This changes Req 11.5 (a Guest requesting a private Board) from 403 in V1 to 401 in V2. Guests may still read public Boards without a Token.

## Open Questions

1. **login_identifier format validation:** Should a login_identifier be email-shaped, username-shaped, or an arbitrary string? Not decided. Provisional V2 behavior: trim, non-empty, maximum 255 characters, case-insensitive uniqueness, no further format validation, until the product owner decides.
2. **Attachment delivery cost:** Signed time-limited URLs or an authenticated proxy cost more to implement than a public URL. Flagged for the timeline and estimate owner.
3. **Decision A interpretation:** Confirm that public Boards stay readable by every signed-in user (see Decisions Log).
4. **Swagger UI assets from a CDN:** Under flask-smorest, Swagger UI loads its assets from a CDN by default. This is acceptable in development and testing, where the docs routes exist. Flag if offline documentation is required.
