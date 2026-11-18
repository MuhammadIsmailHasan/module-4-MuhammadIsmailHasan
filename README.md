# Kanban Task Management — Project Scaffold

This is the directory scaffold for the project: the brief, the Kiro steering
docs, coding guidelines, and the backend/frontend skeleton. Copy this whole
structure into the repo root.

## What's here

```text
.
├── .kiro/
│   ├── steering/                  # always-loaded context for Kiro
│   │   ├── product.md
│   │   ├── tech.md
│   │   ├── structure.md
│   │   ├── backend.md
│   │   ├── api-conventions.md
│   │   ├── data-model.md
│   │   ├── frontend.md
│   │   ├── change-management.md
│   │   └── development-workflow.md
│   └── specs/                     # NEXT: requirements.md, design.md, tasks.md, CHANGELOG.md go directly here (no per-feature subfolder)
├── specs/
│   ├── project-brief.md           # the 5-section project brief
│   └── v1/                        # NEXT: frozen, versioned domain files (00-OVERVIEW.md, 01-BOARDS.md, ...)
├── design/
│   └── kanban-prototype.html      # approved visual/interaction reference for the board screen
├── guidelines/                    # coding standards the generated code is checked against
│   ├── frontend.md
│   ├── backend.md
│   └── database.md
├── backend/                       # Flask API
│   ├── app/
│   │   ├── blueprints/
│   │   │   ├── auth/              # routes.py, service.py, repository.py, schema.py go in each
│   │   │   ├── boards/
│   │   │   ├── columns/
│   │   │   ├── cards/
│   │   │   ├── categories/
│   │   │   ├── comments/
│   │   │   ├── notifications/
│   │   │   ├── analytics/
│   │   │   └── users/
│   │   └── models/
│   ├── tests/
│   └── .env.example
└── frontend/                      # Next.js app
    ├── app/
    ├── components/
    │   └── shared/                # BaseButton, BaseBadge, BaseModal
    └── .env.example
```

## How this flows with Kiro

1. Drop `.kiro/steering/*.md` and `guidelines/*.md` into the repo as-is —
   they're the always-on rules the generated code should follow.
2. Open `.kiro/specs/` in Kiro and generate `requirements.md` → `design.md` →
   `tasks.md` straight from `specs/project-brief.md`, directly inside
   `.kiro/specs/` (no per-feature subfolder — see `structure.md`).
3. Start a `CHANGELOG.md` right there from the first revision onward (per
   `change-management.md`).
4. While implementing, add the real `routes.py` / `service.py` /
   `repository.py` / `schema.py` into each `backend/app/blueprints/<domain>/`
   folder, and build frontend pages on top of `components/shared/Base*`,
   mobile-first, Server Components by default.
5. Once there's real generated code, keep a short note of any guideline
   violation found in it and the fix applied — useful for catching drift
   later, not just as a one-time exercise.

Still open: the actual `requirements.md`/`design.md`/`tasks.md`/`CHANGELOG.md`
content, the Flask/Next.js implementation itself, tests, and deployment.
