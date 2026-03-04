# Tasks: SCRUM Poker Session Management

**Input**: Design documents from `/specs/001-scrum-poker-system/`
**Prerequisites**: `plan.md` (required), `spec.md` (required for user stories), `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Included because the specification defines independent test criteria, API contracts, and real-time behavior requirements.

**Organization**: Tasks are grouped by user story to enable independent implementation and validation.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and baseline tooling for a local mock-data-first web app.

- [ ] T001 Create project skeleton for app and tests in `app/` and `tests/`
- [ ] T002 Initialize Python project dependencies with `uv` in `pyproject.toml`
- [ ] T003 [P] Configure `black` and `ruff` defaults in `pyproject.toml`
- [ ] T004 [P] Add runtime environment template for inmemory/postgres modes in `.env.example`
- [ ] T005 Create Flask app factory and extension bootstrap in `app/__init__.py`
- [ ] T006 Add development/testing/postgres settings in `app/config.py`
- [ ] T007 [P] Add application container build definition in `docker/Dockerfile`
- [ ] T008 [P] Add local postgres compose stack in `docker/docker-compose.yml`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared domain and infrastructure that blocks all user story work.

**⚠️ CRITICAL**: No user story implementation should start before this phase is complete.

- [ ] T009 Define core entities (Team, Session, Participant, Issue, Vote, VotingCardSet, AdminConfig) in `app/domain/entities/`
- [ ] T010 Define repository interfaces for sessions/admin/votes in `app/domain/repositories/`
- [ ] T011 Implement in-memory repositories and seed fixtures in `app/infra/repository_inmemory/`
- [ ] T012 Scaffold SQLAlchemy repository adapters for later persistence swap in `app/infra/repository_sqlalchemy/`
- [ ] T013 Implement shared domain errors and validation primitives in `app/domain/services/errors.py`
- [ ] T014 Create SocketIO bootstrap and room event helpers in `app/web/sockets.py`
- [ ] T015 Build shared base template with status messaging and theme hooks in `app/templates/shared/base.html`
- [ ] T016 Add shared client runtime utilities (API/event/theme) in `app/static/js/app.js`
- [ ] T017 Establish global CSS tokens, breakpoints, and light/dark theme variables in `app/static/css/styles.css`
- [ ] T018 Add reusable pytest fixtures and factory data in `tests/conftest.py`

**Checkpoint**: Foundation complete; stories can now be built and tested independently.

---

## Phase 3: User Story 1 - Run a Live Estimation Session (Priority: P1) 🎯 MVP

**Goal**: Enable synchronized issue selection, voting, reveal, final estimate save, and resilient leader continuity.

**Independent Test**: Start one session with multiple participants, activate an issue, cast/change/clear votes, reveal, save final estimate, force leader leave, and verify automatic leader reassignment is broadcast.

### Tests for User Story 1

- [ ] T019 [P] [US1] Add contract tests for session detail and vote lifecycle endpoints in `tests/contract/test_us1_session_voting_contract.py`
- [ ] T020 [P] [US1] Add integration tests for cast/change/clear/reveal/finalize flow in `tests/integration/test_us1_live_estimation_flow.py`
- [ ] T021 [P] [US1] Add realtime event integration tests (`issue_selected`, `vote_count_updated`, `votes_revealed`, `leader_changed`) in `tests/integration/test_us1_realtime_events.py`
- [ ] T022 [P] [US1] Add unit tests for average calculation with `?`, `☕️`, `♾️` mapped to `0` in `tests/unit/test_vote_average_rules.py`
- [ ] T023 [P] [US1] Add integration test for automatic leader reassignment when leader leaves mid-session in `tests/integration/test_us1_leader_reassignment.py`

### Implementation for User Story 1

- [ ] T024 [US1] Implement session orchestration service for active issue and participation state in `app/domain/services/session_service.py`
- [ ] T025 [US1] Implement vote service for cast/change/clear/reveal/finalize/average in `app/domain/services/vote_service.py`
- [ ] T026 [US1] Implement session detail route and view-model composition in `app/web/routes_sessions.py`
- [ ] T027 [US1] Implement vote/reveal/final-estimate/rejoin/leave endpoints in `app/web/routes_sessions.py`
- [ ] T028 [US1] Implement issue activation and leader designation endpoints in `app/web/routes_sessions.py`
- [ ] T029 [US1] Implement automatic leader reassignment and event dispatch on leader leave in `app/domain/services/session_service.py`
- [ ] T030 [US1] Broadcast `leader_changed` and session state updates from socket layer in `app/web/sockets.py`
- [ ] T031 [P] [US1] Build session detail page with 25/75 layout and participant status row in `app/templates/session/detail.html`
- [ ] T032 [P] [US1] Build issue detail partial for placeholders, reveal state, unique cards, and average in `app/templates/session/_issue_detail.html`
- [ ] T033 [US1] Implement client interactions and DOM sync for voting/reveal/rejoin/finalize in `app/static/js/session-detail.js`

**Checkpoint**: US1 is independently functional and testable (MVP).

---

## Phase 4: User Story 2 - Create a Session from Imported Backlog (Priority: P2)

**Goal**: Create sessions from validated metadata + CSV and immediately enter session detail.

**Independent Test**: Open new-session page, select team, verify prefill behavior, upload mixed-order CSV, create session, and verify redirect + history update.

### Tests for User Story 2

- [ ] T034 [P] [US2] Add contract tests for session creation and CSV validation responses in `tests/contract/test_us2_create_session_contract.py`
- [ ] T035 [P] [US2] Add integration tests for team-name prefill and create-session redirect in `tests/integration/test_us2_session_creation_flow.py`
- [ ] T036 [P] [US2] Add parser unit tests for required headers and row-level issue-type validation in `tests/unit/test_us2_csv_parser.py`

### Implementation for User Story 2

- [ ] T037 [US2] Implement CSV parsing with header normalization in `app/infra/csv_import/parser.py`
- [ ] T038 [US2] Implement CSV validation/error payload formatting in `app/infra/csv_import/validation.py`
- [ ] T039 [US2] Implement session creation service for defaults, leader assignment, and issue import in `app/domain/services/session_creation_service.py`
- [ ] T040 [US2] Implement new-session form/display/create routes in `app/web/routes_sessions.py`
- [ ] T041 [P] [US2] Build new-session template with upload and inline error states in `app/templates/session/new.html`
- [ ] T042 [US2] Add client form handling and inline CSV validation messaging in `app/static/js/new-session.js`
- [ ] T043 [US2] Emit `session_created` updates to history subscribers in `app/web/sockets.py`

**Checkpoint**: US2 is independently functional and testable.

---

## Phase 5: User Story 3 - Review and Reopen Session History (Priority: P3)

**Goal**: Provide recency-sorted history with filtering and open-session navigation.

**Independent Test**: Load history with mixed sessions, apply filters (name/sprint/team), confirm descending order, and open a selected session.

### Tests for User Story 3

- [ ] T044 [P] [US3] Add contract tests for session history list/filter parameters in `tests/contract/test_us3_history_contract.py`
- [ ] T045 [P] [US3] Add integration tests for sorting, filter combinations, and open-session navigation in `tests/integration/test_us3_history_flow.py`

### Implementation for User Story 3

- [ ] T046 [US3] Implement session history query service for recency + filters in `app/domain/services/history_service.py`
- [ ] T047 [US3] Implement history and open-session routes in `app/web/routes_sessions.py`
- [ ] T048 [P] [US3] Build history page template with filter controls/cards in `app/templates/history/index.html`
- [ ] T049 [US3] Add client filter state/query serialization in `app/static/js/history.js`

**Checkpoint**: US3 is independently functional and testable.

---

## Phase 6: User Story 4 - Configure Teams and Session Governance (Priority: P4)

**Goal**: Enable admin team management, base issue URL configuration, and completed session deletion.

**Independent Test**: Add/edit/delete teams, set base issue URL and verify issue link rendering behavior, delete completed session and confirm history removal.

### Tests for User Story 4

- [ ] T050 [P] [US4] Add contract tests for admin teams/config/completed-session endpoints in `tests/contract/test_us4_admin_contract.py`
- [ ] T051 [P] [US4] Add integration tests for admin configuration workflows and downstream session-link behavior in `tests/integration/test_us4_admin_flow.py`

### Implementation for User Story 4

- [ ] T052 [US4] Implement admin service for team lifecycle and base URL management in `app/domain/services/admin_service.py`
- [ ] T053 [US4] Implement admin routes for teams/config/completed-session deletion in `app/web/routes_admin.py`
- [ ] T054 [P] [US4] Build admin configuration template with team CRUD + base URL form in `app/templates/admin/index.html`
- [ ] T055 [US4] Implement issue-link resolver with disabled-link fallback messaging in `app/domain/services/link_service.py`
- [ ] T056 [US4] Connect issue-link rendering to admin config in `app/templates/session/_issue_detail.html`

**Checkpoint**: US4 is independently functional and testable.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Cross-story hardening, quality gates, and delivery readiness.

- [ ] T057 [P] Add desktop-focused browser smoke tests for create/vote/reveal/complete flows in `tests/integration/test_smoke_core_flows.py`
- [ ] T058 [P] Add realtime performance verification tests for <=2s propagation targets in `tests/integration/test_performance_realtime.py`
- [ ] T059 Add accessibility and responsive CSS refinements for core flows in `app/static/css/styles.css`
- [ ] T060 [P] Add docstring compliance validation for modules/classes/functions in `pyproject.toml` and `tests/unit/test_docstring_compliance.py`
- [ ] T061 [P] Update quickstart with desktop automated test commands and mobile manual QA guidance in `specs/001-scrum-poker-system/quickstart.md`
- [ ] T062 Run and document final validation (`black`, `ruff`, pytest suites) in `specs/001-scrum-poker-system/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies.
- **Phase 2 (Foundational)**: Depends on Phase 1 and blocks all story execution.
- **Phase 3-6 (User Stories)**: Depend on Phase 2.
- **Phase 7 (Polish)**: Depends on all implemented stories.

### User Story Dependencies

- **US1 (P1)**: Starts after Foundational and defines MVP.
- **US2 (P2)**: Starts after Foundational; independent of US1 business logic.
- **US3 (P3)**: Starts after Foundational; independent of US1/US2 internals.
- **US4 (P4)**: Starts after Foundational; independent with shared entities.

### Within Each User Story

- Tests first (where listed) and confirm failing state.
- Services before routes.
- Routes before UI wiring.
- Complete a story and validate its independent test before moving on.

### Story Completion Order

- Recommended sequence: **US1 -> US2 -> US3 -> US4**
- Parallel option after Foundational: **US2, US3, US4** can proceed in parallel.

## Parallel Execution Examples

### User Story 1

```bash
# Parallel tests
T019, T020, T021, T022, T023

# Parallel UI work after endpoint contracts stabilize
T031, T032
```

### User Story 2

```bash
# Parallel tests
T034, T035, T036

# Parser and template work can overlap
T037, T041
```

### User Story 3

```bash
# Parallel tests
T044, T045

# Service and template tasks can overlap
T046, T048
```

### User Story 4

```bash
# Parallel tests
T050, T051

# Template and link service tasks can overlap
T054, T055
```

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1 and Phase 2.
2. Deliver Phase 3 (US1) end-to-end.
3. Validate US1 independently before expanding scope.

### Incremental Delivery

1. Deliver US1 (live estimation loop + leader continuity).
2. Deliver US2 (CSV session creation).
3. Deliver US3 (history/filter/reopen).
4. Deliver US4 (admin governance).
5. Execute Phase 7 polish and validation.

### Parallel Team Strategy

1. Team collaborates on Setup + Foundational.
2. Split by story after Foundation:
   - Dev A: US1/US2
   - Dev B: US3
   - Dev C: US4
3. Rejoin for cross-cutting hardening and release validation.
