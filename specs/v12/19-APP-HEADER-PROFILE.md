# App header and profile, V12 changes

Requirement 29 (Profile page layout) is new. The App_Header page context on a Board shows the "Public link" button for Manager and Admin and the "Invite" button for the Board_Owner, Manager, and Admin; it shows no visibility icon.

### Requirement 29: Profile Page Layout

**User Story:** As a signed-in user, I want the Profile page to use the width of my screen, so that my account details and my password change are both in view on a desktop.

Note (V12, Decision AF): this requirement amends Requirement 19 only in layout; the fields, validation, and endpoints of Requirement 19 do not change.

#### Acceptance Criteria

1. [PRO-01] WHILE the viewport is 960 pixels wide or more, THE Frontend SHALL lay out the Profile_Page content in two columns of equal width inside a full-width container (the page padding of the App_Header shell, no centred narrow column): the avatar card and the account details card on the left, stacked, and the change-password card on the right.
2. [PRO-02] WHILE the viewport is narrower than 960 pixels, THE Frontend SHALL stack the cards in one column in this order: avatar, account details, change password (mobile-first base styles, with the two-column grid added by a `min-width: 960px` query).
3. [PRO-03] THE Frontend SHALL build the Profile_Page from the existing tokens only: controls 40 pixels high (compact buttons 32 pixels), 16 pixel padding in every card, 24 pixels between cards, titles and labels at the sizes of Requirement 14, criterion 20, and no hard-coded colour or arbitrary value.
4. [PRO-04] THE Frontend SHALL keep every field, action, validation message, and endpoint of Requirement 19 on the Profile_Page, and the avatar preview SHALL keep its size at every width.

### Requirement 19 criteria with V12 labels

Criteria of Requirement 19 that V12 changed. Each line is the full V1 to V11 criterion followed by its V12 label; the label wins.

38. [AVT-21] THE Frontend SHALL draw every user avatar through `BaseAvatar`, showing the Avatar_Image when the URL is set and the Initials_Avatar otherwise, for the author of each Comment and Reply, each Team members row of the Sidebar, each member search result, each row of the assignee popover, the assignee on a board Card, the assignee chip of the Card modal, and the member avatars of a Home tile (Decision U). (V12: no visibility icon on Home tiles, Requirement 22, criterion 14.)
