# Feature Specification: SCRUM Poker Voting System

**Feature Branch**: `002-scrum-poker`  
**Created**: March 5, 2026  
**Status**: Draft  

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Participate in Live Voting Session (Priority: P1)

Team members join a SCRUM poker session and vote on story complexity in real-time. As each issue is presented, participants select voting cards, see aggregated results when revealed, and the system allows the session leader to confirm estimates.

**Why this priority**: This is the core value proposition of the feature. Without live voting capability, the SCRUM poker system has no function. This enables the primary user goal of building consensus on task complexity.

**Independent Test**: Can be fully tested by creating a new session, joining as multiple users, voting on issues, and verifying that votes are aggregated and revealed correctly. Delivers the core value of collaborative story point estimation.

**Acceptance Scenarios**:

1. **Given** a session is active on an issue, **When** a participant clicks a voting card, **Then** their vote is recorded and the "All votes" counter updates to reflect their participation
2. **Given** multiple participants have voted, **When** the leader clicks "Reveal", **Then** all individual votes are displayed horizontally with participant icons visible below each card
3. **Given** votes are revealed, **When** the leader clicks a unique card value, **Then** only numeric values (not ?, ☕, ♾) contribute to the average calculation displayed below
4. **Given** votes are revealed, **When** the leader enters a custom estimate and clicks "Save", **Then** that estimate replaces the card-based consensus and the navigation card is updated with the new estimate
5. **Given** a participant is voting, **When** they click the same card again, **Then** their vote is removed and the counter decrements
6. **Given** a participant voted on an issue, **When** they click on a different issue in navigation, **Then** a "Rejoin" button appears in the status bar for the original issue, allowing them to re-engage

---

### User Story 2 - Create and Lead a Session (Priority: P1)

A team member creates a new SCRUM poker session by selecting team, entering session details, uploading issues from a CSV file, and automatically becomes the session leader with exclusive leadership controls.

**Why this priority**: Session creation is required for any estimation activity. Leadership designation ensures clear session control and decision-making authority. Without this, voting sessions cannot be initiated.

**Independent Test**: Can be fully tested by creating a new session with team selection, session name, sprint number, card set selection, CSV upload, and verifying the creator becomes leader with appropriate controls. Delivers ability to initiate estimation activities.

**Acceptance Scenarios**:

1. **Given** the user clicks "Begin New Session", **When** the new session dialog opens, **Then** the team dropdown is displayed and ready for selection
2. **Given** a team is selected, **When** the form displays, **Then** the session name field pre-populates with the last session name used by that team
3. **Given** the new session dialog is open, **When** the user uploads a valid CSV file, **Then** the file is parsed and issues are stored (file order doesn't matter; extra fields are ignored; Issue Type, Issue Key, Summary are required; Description, Story Points optional)
4. **Given** the user clicks the "Begin" button, **When** the API creates the session, **Then** the user is navigated to the Session Detail page and becomes the designated leader
5. **Given** a session is created, **When** other users refresh or navigate to the Entry page, **Then** the new session appears at the top of the list immediately
6. **Given** the leader is on the Session Detail page, **When** they click "Designate Leader", **Then** a modal appears showing available participants to transfer leadership
7. **Given** the leader transferred leadership, **When** a new leader is designated, **Then** the status bar icons update to reflect the new leader, and the previous leader becomes a standard participant

---

### User Story 3 - View and Join Existing Sessions (Priority: P2)

Users can browse the list of previously conducted SCRUM poker sessions, filter by session name, sprint number, or team, and join an active session.

**Why this priority**: This enables discovery and participation in ongoing estimation activities. While essential for multi-user scenarios, it is secondary to the core voting functionality as a single-user can still estimate through session creation.

**Independent Test**: Can be fully tested by viewing the session list, applying various filters, and verifying sessions are correctly displayed in reverse chronological order. Delivers session discoverability.

**Acceptance Scenarios**:

1. **Given** the Entry page is displayed, **When** it loads, **Then** all non-completed sessions are listed in a table ordered by most recent first
2. **Given** sessions are displayed, **When** the user enters text in the session name filter, **Then** the table updates to show only matching sessions
3. **Given** sessions are displayed, **When** the user selects a team in the filter dropdown, **Then** the table updates to show only sessions with that team
4. **Given** sessions are displayed, **When** the user enters a sprint number, **Then** the table updates to show only sessions with that sprint
5. **Given** the user sees a session in the list, **When** they click on it, **Then** they are navigated to the Session Detail page for that session
6. **Given** a user navigates to a session detail page, **When** they first load it, **Then** they are automatically added as a participant (unless already participating)

---

### User Story 4 - Administer SCRUM Poker Configuration (Priority: P2)

Administrators manage team names, view and delete completed sessions, and configure the base URL for linking to issues in their agile system.

**Why this priority**: Configuration is necessary for operational sustainability and linking back to the source system, but the voting system functions with default configuration. Administrative tasks are secondary to core voting functionality.

**Independent Test**: Can be fully tested by creating teams, managing completed sessions, and configuring base URL for various agile systems. Delivers operational control but doesn't block core functionality.

**Acceptance Scenarios**:

1. **Given** the admin is on the configuration page, **When** they enter a new team name and click add, **Then** the team is created and appears in the team list
2. **Given** the admin is on the configuration page, **When** they click delete next to a team, **Then** the team is removed from the list
3. **Given** the admin is on the configuration page, **When** they scroll to the completed sessions section, **Then** all completed sessions are listed
4. **Given** a completed session is listed, **When** the admin clicks delete, **Then** the session and all its voting data are permanently removed
5. **Given** the admin is on the configuration page, **When** they enter a base URL (e.g., https://dev.azure.com/..., https://jira.example.com/browse/), **Then** this URL is saved and used for issue linking throughout the application
6. **Given** a base URL is configured, **When** an issue key is clicked in session detail, **Then** the link opens to [BASE_URL]/[ISSUE_KEY] in a new browser tab

---

### User Story 5 - Experience Responsive UI with Theme Support (Priority: P1)

Users experience a responsive, professional interface that adapts to screen sizes and supports both light and dark modes selectable from the home page navigation.

**Why this priority**: User experience quality directly impacts adoption. Responsive design ensures usability across devices. Theme support is explicitly required and affects every page viewed by users.

**Independent Test**: Can be tested by resizing the browser window and toggling between light/dark modes, verifying layout integrity and readability on mobile, tablet, and desktop screens. Delivers consistent, accessible user experience.

**Acceptance Scenarios**:

1. **Given** the user is on any page, **When** they reduce the browser window to mobile width (320px), **Then** the layout reflows and remains fully usable without horizontal scrolling
2. **Given** the user is on the home page, **When** they toggle the theme control, **Then** the entire application immediately switches between light and dark modes
3. **Given** the user has selected dark mode, **When** they navigate to different pages, **Then** the dark mode preference persists across all pages
4. **Given** the user is on any page, **When** the theme is dark, **Then** all text is readable with sufficient contrast, and voting cards display appropriately
5. **Given** the theme control is on the home page navigation, **When** the page is mobile-width responsive view, **Then** the theme control remains accessible and usable
6. **Given** the application is running, **When** the user closes and reopens the browser, **Then** their last selected theme preference is restored

---

### Edge Cases

- What happens when a CSV file is uploaded with missing required fields (Issue Type, Issue Key, or Summary)? System MUST reject the file and display a specific error message indicating which field is missing.
- What happens when two leaders try to reveal votes simultaneously? System MUST handle race condition gracefully and show consistent state to all users.
- What happens when a participant votes after the leader has revealed votes? System MUST prevent voting once reveal has occurred for that issue.
- What happens when a user disconnects during an active session? System MUST maintain their status as a participant and allow them to rejoin when they reconnect.
- What happens when the last participant leaves a session? System MUST keep the session active until explicitly completed by the leader.
- What happens when an estimate is set to a custom value outside the Fibonacci range (e.g., 100)? System MUST accept and display the custom value, treating it as a valid estimate.
- What happens when a base URL is not configured in admin settings? System MUST still display issue keys as plain text (non-clickable) rather than failing.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow teams to be created and managed through the admin configuration page with the ability to add and delete team names
- **FR-002**: System MUST allow users to create a new SCRUM poker session by selecting a team, entering a session name (with pre-population from last session for that team), specifying a sprint number, and selecting a card set
- **FR-003**: System MUST support a single card set initially containing Fibonacci numbers 1-13 plus special cards: '?' (unknown), '☕' (coffee break), and '♾️' (infinity)
- **FR-004**: System MUST accept CSV file uploads containing issues with required fields (Issue Type, Issue Key, Summary) and optional fields (Description, Story Points), with parsing that ignores field order and extra columns
- **FR-005**: System MUST designate the session creator as the initial session leader
- **FR-006**: System MUST allow the leader to transfer leadership to another session participant via a modal dialog, updating icons and controls accordingly
- **FR-007**: System MUST allow all participants to vote on each issue by selecting voting cards, with votes being removable and changeable until reveal
- **FR-008**: System MUST display real-time vote count ("All votes N/M") as participants vote
- **FR-009**: System MUST allow the leader to reveal all votes as anonymized cards horizontally with participant icons below each card
- **FR-010**: System MUST calculate and display the average of numeric card values only (?, ☕, ♾ each count as 0 for average calculation)
- **FR-011**: System MUST allow the leader to select specific revealed cards and set a custom estimate, with the custom value saved to the story
- **FR-012**: System MUST maintain a persistent list of completed sessions that the admin can view and delete
- **FR-013**: System MUST store and use a base URL configured in admin settings for generating links to issues in external agile systems (Azure DevOps, Jira, etc.)
- **FR-014**: System MUST support light and dark themes selectable from the home page navigation with persistent user preference
- **FR-015**: System MUST be fully responsive and function correctly on mobile (320px+), tablet, and desktop screens
- **FR-016**: System MUST integrate poker voting feature navigation into the existing home page
- **FR-017**: System MUST display session detail with status row showing session title, participant icons, and action buttons (Leave Session, Complete Session for leader)
- **FR-018**: System MUST allow participants to click on a navigation card to view detailed content in the detail column, with changes broadcasting to all other participants except the viewer
- **FR-019**: System MUST allow participants to "Rejoin" the current evaluation if they navigated away from the active issue
- **FR-020**: System MUST display the detail column with issue type emoji (📖 for Story, 🐞 for Bug), issue key as a link, summary, description (first 200 characters when possible), and current estimate
- **FR-021**: System MUST broadcast all actions (vote, reveal, join, leave, leader change) to all participants in real-time
- **FR-022**: System MUST allow the leader to complete a session, after which no new votes are recorded
- **FR-023**: System MUST prevent voting on an issue after it has been revealed
- **FR-024**: User-facing interactions MUST remain consistent with established UX patterns, including terminology, flow ordering, and status/error messaging
- **FR-025**: Feature MUST define measurable performance targets relevant to scope (e.g., vote broadcast latency, session list load time)
- **FR-026**: Test requirements MUST identify functional behaviors to validate and MUST avoid tests added solely for count or coverage optics
- **FR-027**: All third-party library dependencies MUST be justified with explicit rationale; evaluate standard library or existing approved dependencies as alternatives
- **FR-028**: Web application MUST use Flask, SQLAlchemy ORM, PostgreSQL, and Jinja2 templating
- **FR-029**: Local development MUST support PostgreSQL running in Docker; final application MUST be packaged as a Docker container image
- **FR-030**: Code structure MUST remain self-documenting with required docstrings for modules/classes/functions, document parameters and return values, place private helpers below public interfaces, avoid mixing unrelated functions/classes
- **FR-031**: Python code MUST be formatted with the `black` formatter with enforcement in local development and CI

### Key Entities *(data involved)*

- **Session**: Represents a SCRUM poker estimation session with attributes: ID (UUID), name, team (FK), sprint number, status (active/completed), leader (FK to Participant), created_at, completed_at, card_set configuration
- **Participant**: Represents a person in a session with attributes: ID (UUID), session (FK), user_identifier, join_timestamp, leave_timestamp, is_leader, current_estimate
- **StorageIssue**: Represents an issue to be estimated with attributes: ID (UUID), session (FK), issue_type (Story/Bug), issue_key (unique within session), summary, description (optional), uploaded_story_points (optional), final_estimate
- **Vote**: Represents a single participant's vote on an issue with attributes: ID (UUID), issue (FK), participant (FK), card_value, voted_at, revealed (boolean)
- **Team**: Represents a team with attributes: ID (UUID), name (unique), created_at
- **Configuration**: System configuration with attributes: ID, base_url_for_issues, theme_setting (for defaults)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a new session and begin voting within 2 minutes from accessing the entry page
- **SC-002**: Session changes (new participant join, vote cast, reveal action) are broadcast to all participants within 500ms
- **SC-003**: The Entry page loads showing all active and historical sessions within 2 seconds for datasets up to 500 sessions
- **SC-004**: System supports at least 50 concurrent participants in a single session without vote loss or timing issues
- **SC-005**: 95% of vote registrations are successfully recorded and reflected in real-time vote counts
- **SC-006**: Users on mobile devices (320px width) can complete all voting actions without horizontal scrolling
- **SC-007**: Dark mode toggle switches application theme and persists preference across browser sessions
- **SC-008**: All issue links generated using configured base URL correctly navigate to the external agile system in a new tab
- **SC-009**: CSV file upload rejects files with missing required fields and provides specific error messages within 1 second
- **SC-010**: At least one UX consistency acceptance scenario passes for each changed user flow (navigation integration, theme switching, voting interactions)

## Assumptions

- Each participant is uniquely identifiable by some user session/identifier mechanism (assumes authentication is handled by existing home page)
- Teams are pre-configured by administrators; new teams are not auto-created from session creation
- The CSV upload mechanism uses standard file input; users are expected to format files correctly based on clear error messages
- Dark mode is implemented using CSS custom properties or similar approach that works across all templates
- Real-time broadcasting uses WebSockets or similar mechanism for live updates across participants
- The agile system base URL is presented as a single configurable string (e.g., users copy/paste their Jira/Azure DevOps base URL)
- Participant identification in status bar icons uses initials or first letter(s) derived from user identifier available in session
- Session history is retained indefinitely in the database unless explicitly deleted by an admin
- The application operates within a single organization; no multi-tenant isolation is required
