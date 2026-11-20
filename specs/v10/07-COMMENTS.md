### Requirement 7: Comments

**User Story:** As a team member, I want threaded comments with manager priority flags, so that important discussion stays on top and managers can turn their own comments into cards.

#### Acceptance Criteria
**Round 3 within V10 (Decisions U to W):** criteria 21 and 22 reworded (`author_avatar_url`, avatar in the thread); both are repeated below.

V10 changes: criterion 16 reworded (a Guest gets 401 whatever the Board's visibility; breaking). All other criteria are unchanged from V8.

16. IF a Guest calls a comment endpoint, THEN THE Backend SHALL return HTTP 401 whatever the Board's visibility and SHALL return no `comments` field; no shared route returns Comments (Decision K; reworded in V10, breaking: V2 to V9 returned 403 for a Guest on a public Board).
21. THE Backend SHALL include the author's full name as `author_name` and the author's Avatar_URL (or null) as `author_avatar_url` on every returned Comment and Reply, loading names and avatar paths for all authors of a Card's Comments in one query (Decision U), and THE Frontend SHALL show that name and never a placeholder for a known author (Decision I).
22. THE Frontend SHALL render the Comment thread as a thread, not as separate boxes: each Comment shows the author's avatar (the Avatar_Image from `author_avatar_url`, or the Initials_Avatar) on the left, the name and time on one line, the text below, and Reply and priority as small text actions; Replies are indented under their parent with a thin vertical line from the parent's avatar (Decision I).
