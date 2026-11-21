# Testing, V13 additions

- `vitest`: Property 59 (title builder), Property 60 (role tag follows the list), one render test per route title, the styling test for the new controls (SIZE-05).
- `pytest`: members rows carry `role`, never `manager` or `admin`; query count unchanged (ROLE-01).
- Playwright (read-only): `document.title` of `/login` and `/register` (TITLE-08).
