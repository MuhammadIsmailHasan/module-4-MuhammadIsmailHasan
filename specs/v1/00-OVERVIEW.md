# Requirements Document

## Introduction

This document specifies the Kanban Task Management application (Version V1). It is a role-based web app with a Flask REST API backend and a mobile-first Next.js frontend. Teams run day-to-day work on boards, columns, and cards, and supervisors and managers oversee progress through analytics without opening every board.

The requirements translate decisions already recorded in `specs/project-brief.md` and the steering documents in `.kiro/steering/`. They add no new scope. Five user decisions that resolved gaps in the brief are included and marked "Decision N" where they apply.

Out of scope for V1: Google OAuth login (post-MVP, added only after email/username and password auth is verified end-to-end), custom per-board workflow templates beyond the five default columns, and subtasks with their own assignee or date. Stretch features (card `progress` meter, `views_count`, decorative Overview/Notes/Questions tabs) are covered in Requirement 16 and are built only after all other requirements work end-to-end.

This feature requires one data-model addition beyond the current `data-model.md` steering: a nullable `Board.owner_id` (Decision 1).

## Glossary

- **System**: The Kanban Task Management application, consisting of the Backend and the Frontend.
- **Backend**: The Flask REST API, organized as one blueprint per domain, each layered `routes.py → service.py → repository.py → schema.py`.
- **Frontend**: The mobile-first Next.js (App Router, TypeScript) application.
- **Guest**: A visitor without an account. Can view the columns and cards of public boards only.
- **Member**: A signed-in user with the member role.
- **Supervisor**: A signed-in user with the supervisor role. Includes everything a Member can do.
- **Manager**: A signed-in user with the manager role. Includes everything a Supervisor can do.
- **Admin**: A signed-in user with the admin role, a separate administrative track (see Requirement 2).
- **Card_Creator**: A Supervisor, Manager, or Admin.
- **Board**: A project container holding Columns, Cards, and Categories. Has `visibility` (`public` or `private`) and a nullable `owner_id`.
- **Board_Owner**: The Supervisor referenced by a Board's `owner_id`.
- **Column**: An ordered list within a Board that contains Cards.
- **Default_Columns**: The five Columns `Todo`, `In Progress`, `Review`, `Revision`, `Done`, in that order, seeded on every new Board.
- **Card**: A unit of work with a title, description, priority, optional start and end dates, optional Category, optional assignee, Subtasks, and Attachments.
- **Assigned_Member**: The user referenced by a Card's `assignee_id`.
- **Priority**: A Card attribute that is exactly one of `high`, `medium`, or `low`.
- **Subtask**: A checklist item of a Card with a title, `is_done` flag, and Float `order`. Has no assignee and no dates.
- **Attachment**: A link (`url`) or an uploaded file (`file_path` and `mime_type`) belonging to a Card. Never has both empty.
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
- **Envelope**: The response shape `{ "data": ... }` for success and `{ "error": { "code", "message" } }` for failure.
- **Soft_Delete**: Setting `deleted_at` on a row instead of removing the row.
- **Token**: The authentication token returned by register and login, identifying the acting user and role.
