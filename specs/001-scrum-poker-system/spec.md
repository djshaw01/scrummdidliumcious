# Feature Specification: SCRUM Poker Session Management

**Feature Branch**: `[001-scrum-poker-system]`  
**Created**: 2026-03-04  
**Status**: Draft  
**Input**: User description: "SCRUMM poker feature with admin configuration, session history, session creation from CSV, and real-time collaborative voting."

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Run a Live Estimation Session (Priority: P1)

As a session leader, I can run a live estimation session where participants vote on one issue at a time and see synchronized session state, so the team can reach consensus quickly.

**Why this priority**: Real-time estimation is the core business value of SCRUM poker; without it, the feature does not fulfill its purpose.

**Independent Test**: Can be fully tested by creating one session with multiple participants, selecting an issue for active evaluation, casting votes, revealing votes, and saving the final estimate.

**Acceptance Scenarios**:

1. **Given** an active session with participants, **When** the leader selects an issue for evaluation, **Then** all participants see that issue as the active item and their detail view updates accordingly.
2. **Given** an active issue, **When** participants cast or change their votes, **Then** only each participant sees their own chosen card while the shared vote row shows anonymized placeholders and the vote count updates.
3. **Given** votes are cast, **When** the leader clicks Reveal, **Then** all participant votes are shown, the average based on numeric cards is displayed, and the leader can save a final estimate.
4. **Given** a participant navigates to a non-active issue, **When** the participant leaves the active evaluation context, **Then** that participant is marked as not participating in the current evaluation and can rejoin using a Rejoin action.

---

### User Story 2 - Create a Session from Imported Backlog (Priority: P2)

As a team member, I can start a new session by selecting a team, entering session metadata, and uploading a CSV of issues, so estimation can begin quickly with real work items.

**Why this priority**: Fast setup reduces overhead and ensures teams can begin estimation with complete issue context.

**Independent Test**: Can be tested by opening the new-session dialog, filling required fields, uploading a valid CSV with columns in varied order and extra fields, and confirming a new session appears and opens.

**Acceptance Scenarios**:

1. **Given** the new-session dialog is open, **When** a team is selected, **Then** the session name defaults to the most recent prior session name for that team (if one exists).
2. **Given** a CSV file with required columns in any order plus extra columns, **When** the file is uploaded, **Then** the system imports all valid issues and ignores unknown fields.
3. **Given** a valid session form and issue file, **When** Begin is selected, **Then** the session is created, the initiating user becomes leader, and navigation moves to session detail.

---

### User Story 3 - Review and Reopen Session History (Priority: P3)

As a team member, I can browse prior sessions, filter them, and open a selected session, so I can review estimates and continue active sessions.

**Why this priority**: Historical visibility supports continuity, auditing, and follow-up planning.

**Independent Test**: Can be tested by loading the entry page with mixed sessions, applying filters, checking ordering, and opening a selected session.

**Acceptance Scenarios**:

1. **Given** multiple sessions exist, **When** the entry page loads, **Then** sessions are listed from most recent to least recent.
2. **Given** session filters for name, sprint, and team, **When** one or more filters are applied, **Then** only matching sessions are shown.
3. **Given** a session in the list, **When** the user selects it, **Then** the session detail page opens for that session.

---

### User Story 4 - Configure Teams and Session Governance (Priority: P4)

As an administrator, I can manage team names, completed sessions, and the issue base URL template, so sessions are organized and issue links are consistent.

**Why this priority**: Administrative governance improves data quality and operational control but is not required to prove the core voting loop.

**Independent Test**: Can be tested by adding/updating/removing teams, setting the base issue URL, and deleting a completed session from admin configuration.

**Acceptance Scenarios**:

1. **Given** an admin user on configuration page, **When** team names are created or updated, **Then** those team options are available in new session setup.
2. **Given** a configured base issue URL and imported issue keys, **When** issue links are displayed in session views, **Then** each link opens the corresponding issue in a new browser tab.
3. **Given** completed sessions exist, **When** an admin deletes one, **Then** it no longer appears in session history.

---

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- CSV upload is missing one or more required fields (`Issue Type`, `Issue Key`, `Summary`): session creation is blocked and a clear validation message identifies missing fields.
- CSV includes unsupported `Issue Type` values: those rows are rejected with row-level feedback while valid rows remain importable.
- A participant leaves during active voting: vote counts and participant totals update immediately and no stale vote is counted.
- The current leader leaves the session before designating a new leader: the system automatically assigns a replacement leader from connected participants, announces the new leader to all participants, and preserves active issue/voting continuity.
- A session is marked complete while participants are on the page: all users immediately see voting controls disabled and no further votes are recorded.
- A participant tries to open an issue link when no base URL is configured: the issue key is displayed but link activation is disabled with explanatory text.

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: The feature MUST provide four user-facing surfaces: admin configuration page, entry/history page, new-session creation interface, and session detail page.
- **FR-002**: The user interface MUST be responsive across desktop and mobile viewport sizes; automated verification is required for representative desktop viewport behavior, while mobile viewport verification may be manual and user-test driven.
- **FR-003**: Users MUST be able to select either light mode or dark mode, and the selected mode MUST persist for future visits.
- **FR-004**: Admins MUST be able to create, edit, and remove team names used in session setup.
- **FR-005**: Admins MUST be able to set and update a base issue URL used to build issue links from imported issue keys.
- **FR-006**: Admins MUST be able to view and delete completed sessions.
- **FR-007**: The entry page MUST list sessions in descending recency order by creation date/time.
- **FR-008**: The entry page MUST support filtering sessions by session name, sprint number, and team.
- **FR-009**: The entry page MUST include an action to begin a new session and MUST allow navigation to a selected session detail.
- **FR-010**: New-session setup MUST require team selection, session name, sprint number, voting card set selection, and CSV upload.
- **FR-011**: The initial voting card set MUST include `1, 2, 3, 5, 8, 13, ?, ☕️, ♾️`.
- **FR-012**: When a team is selected in new-session setup, the session name MUST prepopulate with that team’s most recent prior session name when available.
- **FR-013**: CSV import MUST accept required fields in any column order, ignore extra columns, and treat `Description` and `Story points` as optional.
- **FR-014**: CSV import MUST require each issue row to include `Issue Type` (`Story` or `Bug`), `Issue Key`, and `Summary`.
- **FR-015**: Starting a session MUST persist the session, assign the initiating user as leader, navigate to session detail, and make the new session visible at the top of entry/history for all viewers currently on that page.
- **FR-016**: Session status row MUST display session title, participant icons, a leave-session action for all participants, and a visually distinct leader indicator.
- **FR-017**: Only the current leader MUST be able to complete the session or designate a different participant as leader.
- **FR-018**: Leader designation MUST immediately update leader identity in participant indicators for all users.
- **FR-018a**: If the current leader leaves an active session without designating a successor, the system MUST automatically assign a new leader from connected participants within 2 seconds and broadcast the leader change to all participants.
- **FR-019**: Completing a session MUST stop further voting and prevent additional vote recording.
- **FR-020**: The session detail view MUST present a navigation column and detail column with a 25%/75% width split target.
- **FR-021**: Navigation cards MUST show issue type emoji (`📖` for Story, `🐞` for Bug), issue key link, summary, and current estimate if available.
- **FR-022**: When the leader selects the active issue, all participants MUST see that same active issue and corresponding detail content.
- **FR-023**: Non-leader participants MAY open other issues for personal viewing; doing so MUST mark them as not participating in current evaluation and expose a rejoin action.
- **FR-024**: Issue detail MUST show type row with issue link, summary, description with heading, current estimate, participant vote cards, vote count (`N/M`), anonymized vote placeholders, and an actions section.
- **FR-025**: Participants MUST be able to cast, change, and clear their own vote before reveal.
- **FR-026**: Vote summary MUST update in real time to reflect current number of votes cast and total active participants.
- **FR-027**: Before reveal, each cast vote MUST be represented as an anonymized `...` placeholder with participant icon beneath it.
- **FR-028**: Only the leader can trigger reveal; after reveal, placeholders MUST be replaced by actual selected cards.
- **FR-029**: After reveal, the actions area MUST show only unique selected cards as selectable options for leader finalization; non-leaders can view but cannot activate those options.
- **FR-030**: The displayed average after reveal MUST include only numeric card values and treat `?`, `☕️`, and `♾️` as numeric `0`.
- **FR-031**: The leader MUST be able to enter a custom estimate and save it as the final issue estimate.
- **FR-032**: User-facing interactions MUST provide actionable validation and status messaging: field-level errors for invalid CSV/form inputs, role/permission errors for invalid actions, and session-state notifications for reveal/complete/leader changes.

### Key Entities *(include if feature involves data)*

- **Team**: Named participant group used to scope sessions; includes display name and lifecycle state.
- **Session**: Time-bound estimation event linked to one team; includes session name, sprint number, creator, leader, status (active/completed), and participant set.
- **Participant**: User present in a session; includes display initials, leadership flag, join state, and active-evaluation participation state.
- **Issue**: Imported work item to estimate; includes issue type, issue key, summary, optional description, optional prior estimate, and final estimate.
- **Vote**: Per-participant selection for the currently active issue; includes selected card value, timestamp, and visibility state (hidden/revealed).
- **Voting Card Set**: Allowed symbols/values available for voting in a session.
- **AdminConfig**: Workspace-level settings including issue base URL and governance options used by admin workflows.

### Assumptions

- Any session participant can initiate a new session; no additional role gate is required beyond admin-only actions on the admin page.
- Session list updates for users currently viewing entry/history are expected to occur quickly enough to appear near-real-time for normal team collaboration.
- If no previous session exists for a selected team, the session name field remains editable and starts empty.
- All session participants can see revealed votes and final estimate outcomes once the leader performs reveal/save actions.
- Responsive behavior for mobile viewports is validated through moderated user testing and manual QA passes; automated device-level responsive testing is out of scope for this iteration.

### Dependencies

- Session issue linking depends on a valid base issue URL being configured by an admin.
- New session creation depends on a valid CSV file containing required issue fields.
- Live collaboration depends on participants being connected during active session updates.

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: At least 90% of new sessions with valid CSV files are created successfully on the first attempt without manual data correction.
- **SC-002**: In usability validation, at least 90% of users can start a session from entry page and reach session detail in under 2 minutes.
- **SC-003**: During live sessions with at least 8 participants, vote count (`N/M`) and anonymized vote placeholders reflect participant actions within 2 seconds in at least 95% of interactions.
- **SC-004**: At least 95% of completed issue evaluations result in a stored final estimate (selected or custom) before moving to the next issue.
- **SC-005**: At least 90% of users can locate and reopen a prior session using list sorting and filters without facilitator assistance.
- **SC-006**: Automated tests verify core flows (create session, vote, reveal, complete session) on representative desktop viewports, while moderated usability review verifies the same flows on representative mobile viewports in both light and dark modes.
