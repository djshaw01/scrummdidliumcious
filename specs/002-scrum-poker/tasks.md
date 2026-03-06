# Tasks: SCRUM Poker Voting System

**Input**: Design documents from `/specs/002-scrum-poker/`
**Prerequisites**: `plan.md` (required), `spec.md` (required for user stories), `research.md`, `data-model.md`, `contracts/`

**Tests**: Include requirement-traceable tests for contract, integration, and unit behaviors defined in the spec.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., `US1`, `US2`, `US3`)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and development tooling alignment

- [ ] T001 Add SCRUM poker runtime dependencies with uv in `pyproject.toml`
- [ ] T002 Configure Flask app settings for PostgreSQL/WebSocket/theme defaults in `app/__init__.py`
- [ ] T003 [P] Add SCRUM poker base stylesheet and script directories in `app/static/styles/poker.css` and `app/static/scripts/poker-session.js`
- [ ] T004 [P] Add SCRUM poker route module placeholders in `app/routes/poker_pages.py`, `app/routes/poker_api.py`, and `app/routes/admin.py`
- [ ] T005 [P] Add developer workflow commands and CI `black --check` enforcement in `README.md` and `.github/workflows/ci.yml`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core persistence, domain boundaries, and realtime plumbing required by all stories

**CRITICAL**: Complete this phase before user story work

- [ ] T006 Create SQLAlchemy `Team` and `Configuration` models in `app/models/team.py` and `app/models/configuration.py`
- [ ] T007 Create SQLAlchemy `Session`, `Participant`, `StorageIssue`, and `Vote` models in `app/models/session.py`, `app/models/participant.py`, `app/models/storage_issue.py`, and `app/models/vote.py`
- [ ] T008 Create initial Alembic migration for SCRUM poker schema in `migrations/versions/002_scrum_poker_initial.py`
- [ ] T009 [P] Implement shared repositories for session/vote/team/configuration access in `app/repositories/session_repository.py`, `app/repositories/vote_repository.py`, `app/repositories/team_repository.py`, and `app/repositories/configuration_repository.py`
- [ ] T010 [P] Implement shared Pydantic request DTOs for session/vote/leadership actions in `app/models/dto/create_session_request.py`, `app/models/dto/vote_update_request.py`, and `app/models/dto/leadership_transfer_request.py`
- [ ] T011 Implement realtime event gateway and websocket endpoint in `app/services/realtime_event_service.py` and `app/realtime/websocket.py`
- [ ] T012 Wire poker routes and websocket registration into app factory in `app/__init__.py`
- [ ] T013 [P] Add foundational model/repository tests in `tests/unit/test_scrum_poker_models.py` and `tests/unit/test_scrum_poker_repositories.py`

**Checkpoint**: Foundation ready for independent story implementation

---

## Phase 3: User Story 1 - Participate in Live Voting Session (Priority: P1) MVP

**Goal**: Participants can vote in real-time, leader can reveal results, and estimates can be saved

**Independent Test**: With an existing active session and issues, two participants can cast/change/remove votes, leader reveals once, average is computed correctly, and estimate is persisted

### Tests for User Story 1

- [ ] T014 [P] [US1] Add contract tests for vote/reveal/estimate/complete-session endpoints in `tests/contract/test_scrum_poker_voting_contract.py`
- [ ] T015 [P] [US1] Add realtime integration test for vote count/reveal broadcast and post-completion vote lock in `tests/integration/test_scrum_poker_realtime.py`
- [ ] T016 [P] [US1] Add vote domain unit tests for upsert/remove/reveal lock behavior in `tests/unit/test_vote_service.py`

### Implementation for User Story 1

- [ ] T017 [US1] Implement vote cast/change/remove service logic with reveal and completed-session guards in `app/services/vote_service.py`
- [ ] T018 [US1] Implement reveal idempotency and numeric-average calculation rules in `app/services/vote_service.py`
- [ ] T019 [US1] Implement estimate save logic for selected cards and custom values in `app/services/vote_service.py`
- [ ] T020 [US1] Implement voting/reveal/estimate/complete-session API routes in `app/routes/poker_api.py`
- [ ] T021 [US1] Implement issue activation and rejoin workflow handling in `app/services/session_service.py` and `app/routes/poker_api.py`
- [ ] T022 [US1] Implement session detail page rendering for cards/vote strip/status row in `app/routes/poker_pages.py` and `app/templates/poker_session.html`
- [ ] T023 [P] [US1] Implement realtime client updates for vote count/reveal state in `app/static/scripts/poker-session.js`
- [ ] T024 [US1] Broadcast vote/reveal/activation/complete events after committed transactions in `app/services/realtime_event_service.py`

**Checkpoint**: User Story 1 is independently testable and demoable

---

## Phase 4: User Story 2 - Create and Lead a Session (Priority: P1)

**Goal**: Users can create sessions from CSV and leaders can transfer session leadership

**Independent Test**: A user creates a session with CSV upload, is auto-assigned leader, sees issues loaded, and can transfer leadership to another participant

### Tests for User Story 2

- [ ] T025 [P] [US2] Add contract tests for session creation and leadership transfer in `tests/contract/test_scrum_poker_session_contract.py`
- [ ] T026 [P] [US2] Add integration tests for session creation flow and leader transfer UI state in `tests/integration/test_scrum_poker_session_lifecycle.py`
- [ ] T027 [P] [US2] Add unit tests for CSV parsing and validation errors in `tests/unit/test_csv_issue_import_service.py`

### Implementation for User Story 2

- [ ] T028 [US2] Implement CSV import parser with required-column validation and extra-column tolerance in `app/services/csv_issue_import_service.py`
- [ ] T029 [US2] Implement session creation service (team/session/sprint/card set + issue ingestion) in `app/services/session_service.py`
- [ ] T030 [US2] Implement create-session and transfer-leader API endpoints in `app/routes/poker_api.py`
- [ ] T031 [US2] Implement entry-page new-session modal and submission flow in `app/templates/poker_entry.html` and `app/static/scripts/poker-session.js`
- [ ] T032 [US2] Implement leader transfer modal and participant selector in `app/templates/poker_session.html` and `app/static/scripts/poker-session.js`
- [ ] T033 [US2] Persist and prefill last session name per team during session creation in `app/repositories/session_repository.py` and `app/services/session_service.py`
- [ ] T034 [US2] Add creator auto-join and initial leader assignment transaction logic in `app/services/session_service.py`

**Checkpoint**: User Story 2 is independently testable and demoable

---

## Phase 5: User Story 5 - Experience Responsive UI with Theme Support (Priority: P1)

**Goal**: Users get a responsive interface and persistent light/dark theme across pages

**Independent Test**: At 320px width all pages remain usable without horizontal scroll, theme toggles instantly, and preference persists after reload/restart

### Tests for User Story 5

- [ ] T035 [P] [US5] Add responsive and theme persistence integration tests in `tests/integration/test_scrum_poker_responsive_theme.py`
- [ ] T036 [P] [US5] Add unit tests for theme persistence service in `tests/unit/test_theme_service.py`

### Implementation for User Story 5

- [ ] T037 [US5] Implement theme preference read/write service in `app/services/theme_service.py`
- [ ] T038 [US5] Add global theme toggle controls in home navigation and base layout in `app/templates/base.html` and `app/templates/home.html`
- [ ] T039 [US5] Apply CSS variable-based light/dark token system in `app/static/styles/theme.css`
- [ ] T040 [US5] Implement responsive layouts for entry and session pages in `app/static/styles/poker.css` and `app/templates/poker_entry.html`
- [ ] T041 [US5] Persist theme selection in browser and sync on page load in `app/static/scripts/theme-toggle.js`

**Checkpoint**: User Story 5 is independently testable and demoable

---

## Phase 6: User Story 3 - View and Join Existing Sessions (Priority: P2)

**Goal**: Users can browse/filter sessions and join active sessions from the entry page

**Independent Test**: Entry page lists active and completed sessions newest-first, filter controls narrow results correctly, and selecting a session auto-joins participant

### Tests for User Story 3

- [ ] T042 [P] [US3] Add contract tests for session list/filter and join endpoints in `tests/contract/test_scrum_poker_entry_contract.py`
- [ ] T043 [P] [US3] Add integration tests for entry table filters and auto-join behavior in `tests/integration/test_scrum_poker_entry_flow.py`

### Implementation for User Story 3

- [ ] T044 [US3] Implement session list query/filter service behavior (name/team/sprint/status) in `app/services/session_service.py`
- [ ] T045 [US3] Implement list-sessions, session-detail, and join endpoints in `app/routes/poker_api.py`
- [ ] T046 [US3] Build entry page sessions table/filter controls in `app/templates/poker_entry.html`
- [ ] T047 [P] [US3] Add client-side filter interactions and auto-join trigger in `app/static/scripts/poker-session.js`
- [ ] T048 [US3] Render session list route and integrate navigation from home in `app/routes/poker_pages.py`, `app/routes/home.py`, and `app/templates/home.html`

**Checkpoint**: User Story 3 is independently testable and demoable

---

## Phase 7: User Story 4 - Administer SCRUM Poker Configuration (Priority: P2)

**Goal**: Admins can manage teams, completed sessions, and issue base URL configuration

**Independent Test**: Admin can add/delete teams, view/delete completed sessions, save base URL, and issue keys become links when configured

### Tests for User Story 4

- [ ] T049 [P] [US4] Add contract tests for teams, completed-session deletion, and config endpoints in `tests/contract/test_scrum_poker_admin_contract.py`
- [ ] T050 [P] [US4] Add integration tests for admin configuration workflows in `tests/integration/test_scrum_poker_admin_configuration.py`

### Implementation for User Story 4

- [ ] T051 [US4] Implement team management and completed-session deletion services in `app/services/session_service.py` and `app/services/admin_service.py`
- [ ] T052 [US4] Implement admin/configuration API endpoints in `app/routes/admin.py` and `app/routes/poker_api.py`
- [ ] T053 [US4] Build admin configuration page for teams/completed sessions/base URL in `app/templates/admin_configuration.html`
- [ ] T054 [P] [US4] Add admin page client actions for create/delete/update operations in `app/static/scripts/poker-session.js`
- [ ] T055 [US4] Implement issue-link rendering with plain-text fallback when base URL is unset in `app/templates/poker_session.html` and `app/services/session_service.py`

**Checkpoint**: User Story 4 is independently testable and demoable

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final quality, performance, and readiness checks across stories

- [ ] T056 [P] Add performance scenarios for SC-002/SC-003/SC-004/SC-009 in `tests/integration/test_scrum_poker_performance.py`
- [ ] T057 Add UX consistency checks for navigation/theme/voting flows in `tests/integration/test_scrum_poker_ux_consistency.py`
- [ ] T058 [P] Add/refresh SCRUM poker OpenAPI contract examples and response schemas in `specs/002-scrum-poker/contracts/scrum-poker.openapi.yaml`
- [ ] T059 Update feature documentation and operator workflow in `specs/002-scrum-poker/quickstart.md` and `README.md`
- [ ] T060 Run `black --check`, docstring compliance audit, full targeted test suite, and Docker image build/smoke validation; document results in `specs/002-scrum-poker/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies, start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 and blocks all user story phases
- **Phases 3-7 (User Stories)**: Depend on Phase 2 completion
- **Phase 8 (Polish)**: Depends on completion of desired user stories

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 2; no dependency on other user stories
- **US2 (P1)**: Starts after Phase 2; independent but integrates cleanly with US1 session detail flow
- **US5 (P1)**: Starts after Phase 2; independent of US1/US2 backend behavior
- **US3 (P2)**: Starts after Phase 2; can run in parallel with US4
- **US4 (P2)**: Starts after Phase 2; can run in parallel with US3

### Recommended Completion Order

1. Setup + Foundational
2. US1 (MVP)
3. US2 and US5
4. US3 and US4
5. Polish

### Parallel Opportunities

- Setup: `T003`, `T004`, `T005` can run in parallel
- Foundational: `T009`, `T010`, `T013` can run in parallel after model skeletons exist
- US1: `T014`, `T015`, `T016` and `T023` can run in parallel
- US2: `T025`, `T026`, `T027` can run in parallel
- US5: `T035`, `T036` can run in parallel
- US3: `T042`, `T043` and `T047` can run in parallel
- US4: `T049`, `T050` and `T054` can run in parallel
- Polish: `T056` and `T058` can run in parallel

---

## Parallel Example: User Story 1

```bash
Task T014: Contract tests in tests/contract/test_scrum_poker_voting_contract.py
Task T015: Integration realtime test in tests/integration/test_scrum_poker_realtime.py
Task T016: Unit tests in tests/unit/test_vote_service.py
Task T023: Client realtime updates in app/static/scripts/poker-session.js
```

## Parallel Example: User Story 2

```bash
Task T025: Contract tests in tests/contract/test_scrum_poker_session_contract.py
Task T026: Integration tests in tests/integration/test_scrum_poker_session_lifecycle.py
Task T027: CSV service unit tests in tests/unit/test_csv_issue_import_service.py
```

## Parallel Example: User Story 5

```bash
Task T035: Responsive/theme integration tests in tests/integration/test_scrum_poker_responsive_theme.py
Task T036: Theme service unit tests in tests/unit/test_theme_service.py
Task T041: Theme persistence script in app/static/scripts/theme-toggle.js
```

## Parallel Example: User Story 3

```bash
Task T042: Entry contract tests in tests/contract/test_scrum_poker_entry_contract.py
Task T043: Entry integration tests in tests/integration/test_scrum_poker_entry_flow.py
Task T047: Entry page interactions in app/static/scripts/poker-session.js
```

## Parallel Example: User Story 4

```bash
Task T049: Admin contract tests in tests/contract/test_scrum_poker_admin_contract.py
Task T050: Admin integration tests in tests/integration/test_scrum_poker_admin_configuration.py
Task T054: Admin client actions in app/static/scripts/poker-session.js
```

---

## Implementation Strategy

### MVP First (User Story 1)

1. Complete Phase 1 and Phase 2
2. Complete Phase 3 (US1)
3. Validate US1 independent test criteria before moving on

### Incremental Delivery

1. Deliver US1 for core real-time voting
2. Deliver US2 for robust creation and leadership control
3. Deliver US5 for responsive and persistent theming
4. Deliver US3 and US4 for discoverability and administration
5. Finalize with Phase 8 performance and quality polish

### Parallel Team Strategy

1. Pair on Phase 1-2 foundations
2. Split by story after foundation completion:
   - Developer A: US1
   - Developer B: US2/US3
   - Developer C: US5/US4
3. Merge by phase checkpoints and run shared regression/performance suite
