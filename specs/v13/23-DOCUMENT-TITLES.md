# Document titles, V13 (new domain)

### Requirement 32: Document Titles

**User Story:** As a user with several tabs open, I want each tab to say where I am, so that I can find RevoTask and the page I need at a glance.

Note (V13, Decision AI): amends Requirement 21 criterion BRAND-11 (the suffix "· RevoTask") and every page `metadata` title of earlier versions. The root title stays `RevoTask`.

#### Acceptance Criteria

1. [TITLE-01] THE Frontend SHALL set the document title of every page to `RevoTask | <name>` through the Next.js `metadata` API, where `<name>` is the page or panel the user has open, so that the brand comes first and the name follows; the root layout SHALL define `title.default` `RevoTask` and `title.template` `RevoTask | %s`.
2. [TITLE-02] THE Frontend SHALL use these names: Home `Home`; a Board its name (`RevoTask | Alpha Board`); Categories `Categories · <Board name>`; Profile `Profile`; Users `Users`; an invitation `Invitation`; a Shared_View `Shared · <Board name>`; sign-in `Log in`; registration `Register`; the session-expired and not-valid pages `Unavailable`.
3. [TITLE-03] THE Frontend SHALL build the Board and Categories titles with `generateMetadata` from the Board the page already loads (no second request), and SHALL fall back to `RevoTask | Board` when the Board cannot be read; THE title SHALL NOT contain a Token, an invite token, a Share_Token, an Email, or a Comment.
4. [TITLE-04] WHEN the Inbox or the Activity panel is open, THE Frontend SHALL set the title to `RevoTask | Inbox` or `RevoTask | Activity` (with the unread count as `RevoTask | Inbox (3)` when it is above zero), and SHALL restore the title of the page when the panel closes; the title SHALL follow the panel the user opened last.
5. [TITLE-05] WHERE a Card modal is open, THE Frontend SHALL show `RevoTask | <Card title> · <Board name>` and restore the Board title when it closes (Open Question 29).
6. [TITLE-06] THE Frontend SHALL escape no title by hand (React and Next.js do) and SHALL cut a title longer than 60 characters with "…" so that the tab stays readable.
7. [TITLE-07] THE Frontend SHALL keep `robots` `noindex` on the invitation and Shared_View pages, and the other `metadata` fields (description, icons by file convention) SHALL not change.
8. [TITLE-08] THE System SHALL include `vitest` tests for the title builder (a pure function: name in, title out, 60 character cut, panel and unread count) and one test per route that renders its title; the e2e suite SHALL assert `document.title` of `/login` and `/register` only (read-only, Requirement 1 criteria 65 to 72 unchanged).
