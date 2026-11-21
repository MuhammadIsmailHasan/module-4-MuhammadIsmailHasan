# Invites, V13 changes

### Requirement 31: Control Sizes in the Invite and Public Link Controls

**User Story:** As a user of the Board header and the Invite modal, I want the buttons to be the same size as every other control, so that the screen looks like one system.

Note (V13, Decision AH): the V12 build used compact (32 pixel) buttons beside 40 pixel inputs and a 40 pixel header bell. Requirement 14 criterion 20 says controls share one scale: 40 pixels, compact 32 pixels only inside a dense row.

#### Acceptance Criteria

1. [SIZE-01] THE Frontend SHALL draw the Invite button and the Public link button in the Board's App_Header at the default control size (40 pixels high, `BaseButton` `md`), with the 18 pixel icon, 12 pixel horizontal padding gap of the system, and the same height as the Inbox bell and the User_Menu trigger, and SHALL show the count badge of Requirement 24 criterion 21 inside that height.
2. [SIZE-02] THE Frontend SHALL draw "Generate invite link", "Regenerate", "Disable", and the Public link popover's Regenerate and Disable at 40 pixels (`md`), and the link field and its Copy button at the same 40 pixel height in one row, so that the field and the button align on one baseline and one top edge.
3. [SIZE-03] THE Frontend SHALL keep Approve and Reject at the compact size (32 pixels) only inside a join-request row, because that row is a dense list; each of them SHALL still have a 44 pixel touch target below 960 pixels (Requirement 14, criterion 21).
4. [SIZE-04] THE Frontend SHALL give the Invite modal the standard modal anatomy of Decision J: header with title and close icon, body at 24 pixel padding with 24 pixels between sections, and no extra footer; each section SHALL be a titled block (`h3` at the heading size), not an unlabelled paragraph, and the empty state SHALL read like the other empty states ("No requests waiting.").
5. [SIZE-05] THE Frontend SHALL use only existing size and spacing tokens for these controls, SHALL add no arbitrary-value utility, and SHALL pass the styling test of Decision H.
6. [SIZE-06] WHILE the viewport is narrower than 960 pixels, THE Frontend SHALL keep the Invite and Public link buttons reachable in the header without horizontal scroll: icon with a visible text label while there is room, and icon only (with the accessible name kept) when the Board name and the buttons do not fit.
