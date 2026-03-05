# Tasks: SCRUM Poker Session Management

**Input**: Design documents from `/specs/001-scrum-poker-system/`
**Prerequisites**: `plan.md` (required), `spec.md` (required for user stories), `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Included because the specification defines independent test criteria, API contracts, and real-time behavior requirements.

**Organization**: Tasks are grouped by user story to enable independent implementation and validation.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and baseline tooling for a local mock-data-first web app.

- [x] T001 Create project skeleton for app and tests in `app/` and `tests/`
- [x] T002 Initialize Python project dependencies with `uv` in `pyproject.toml`
- [x] T003 [P] Configure `black` and `ruff` defaults in `pyproject.toml`
- [x] T004 [P] Add runtime environment template for inmemory/postgres modes in `.env.example`
- [x] T005 Create Flask app factory and extension bootstrap in `app/__init__.py`
- [x] T006 Add development/testing/postgres settings in `app/config.py`
- [x] T007 [P] Add application container build definition in `docker/Dockerfile`
- [x] T008 [P] Add local postgres compose stack in `docker/docker-compose.yml`
- [x] T009 Document Stage 1 (Setup) run commands and expected app health checks in `README.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared domain and infrastructure that blocks all user story work.

**⚠️ CRITICAL**: No user story implementation should start before this phase is complete.

- [ ] T010 Define core entities (Team, Session, Participant, Issue, Vote, VotingCardSet, AdminConfig) in `app/domain/entities/`
- [ ] T011 Define repository interfaces for sessions/admin/votes in `app/domain/repositories/`
- [ ] T012 Implement in-memory repositories and seed fixtures in `app/infra/repository_inmemory/`
- [ ] T013 Scaffold SQLAlchemy repository adapters for later persistence swap in `app/infra/repository_sqlalchemy/`
- [ ] T014 Implement shared domain errors and validation primitives in `app/domain/services/errors.py`
- [ ] T015 Create SocketIO bootstrap and room event helpers in `app/web/sockets.py`
- [ ] T016 Build shared base template with status messaging and theme hooks in `app/templates/shared/base.html`
- [ ] T017 Add shared client runtime utilities (API/event/theme) in `app/static/js/app.js`
- [ ] T018 Establish global CSS tokens, breakpoints, and light/dark theme variables in `app/static/css/styles.css`
- [ ] T019 Add reusable pytest fixtures and factory data in `tests/conftest.py`
- [ ] T020 Document Stage 2 (Foundational) run/verification commands in `README.md`

**Checkpoint**: Foundation complete; stories can now be built and tested independently.

---

## Phase 3: User Story 1 - Run a Live Estimation Session (Priority: P1) 🎯 MVP

**Goal**: Enable synchronized issue selection, voting, reveal, final estimate save, and resilient leader continuity.

**Independent Test**: Start one session with multiple participants, activate an issue, cast/change/clear votes, reveal, save final estimate, force leader leave, and verify automatic leader reassignment is broadcast.

### Tests for User Story 1

- [ ] T021 [P] [US1] Add contract tests for session detail and vote lifecycle endpoints in `tests/contract/test_us1_session_voting_contract.py`
- [ ] T022 [P] [US1] Add integration tests for cast/change/clear/reveal/finalize flow in `tests/integration/test_us1_live_estimation_flow.py`
- [ ] T023 [P] [US1] Add realtime event integration tests (`issue_selected`, `vote_count_updated`, `votes_revealed`, `leader_changed`) in `tests/integration/test_us1_realtime_events.py`
- [ ] T024 [P] [US1] Add unit tests for average calculation with `?`, `☕️`, `♾️` mapped to `0` in `tests/unit/test_vote_average_rules.py`
- [ ] T025 [P] [US1] Add integration test for automatic leader reassignment when leader leaves mid-session in `tests/integration/test_us1_leader_reassignment.py`

### Implementation for User Story 1

- [ ] T026 [US1] Implement session orchestration service for active issue and participation state in `app/domain/services/session_service.py`
- [ ] T027 [US1] Implement vote service for cast/change/clear/reveal/finalize/average in `app/domain/services/vote_service.py`
- [ ] T028 [US1] Implement session detail route and view-model composition in `app/web/routes_sessions.py`
- [ ] T029 [US1] Implement vote/reveal/final-estimate/rejoin/leave endpoints in `app/web/routes_sessions.py`
- [ ] T030 [US1] Implement issue activation and leader designation endpoints in `app/web/routes_sessions.py`
- [ ] T031 [US1] Implement automatic leader reassignment and event dispatch on leader leave in `app/domain/services/session_service.py`
- [ ] T032 [US1] Broadcast `leader_changed` and session state updates from socket layer in `app/web/sockets.py`
- [ ] T033 [P] [US1] Build session detail page with 25/75 layout and participant status row in `app/templates/session/detail.html`
- [ ] T034 [P] [US1] Build issue detail partial for placeholders, reveal state, unique cards, and average in `app/templates/session/_issue_detail.html`
- [ ] T035 [US1] Implement client interactions and DOM sync for voting/reveal/rejoin/finalize in `app/static/js/session-detail.js`
- [ ] T036 [US1] Document Stage 3 (US1 MVP) run commands and demo path in `README.md`

**Checkpoint**: US1 is independently functional and testable (MVP).

---

## Phase 4: User Story 2 - Create a Session from Imported Backlog (Priority: P2)

**Goal**: Create sessions from validated metadata + CSV and immediately enter session detail.

**Independent Test**: Open new-session page, select team, verify prefill behavior, upload mixed-order CSV, create session, and verify redirect + history update.

### Tests for User Story 2

- [ ] T037 [P] [US2] Add contract tests for session creation and CSV validation responses in `tests/contract/test_us2_create_session_contract.py`
- [ ] T038 [P] [US2] Add integration tests for team-name prefill and create-session redirect in `tests/integration/test_us2_session_creation_flow.py`
- [ ] T039 [P] [US2] Add parser unit tests for required headers and row-level issue-type validation in `tests/unit/test_us2_csv_parser.py`

### Implementation for User Story 2

- [ ] T040 [US2] Implement CSV parsing with header normalization in `app/infra/csv_import/parser.py`
- [ ] T041 [US2] Implement CSV validation/error payload formatting in `app/infra/csv_import/validation.py`
- [ ] T042 [US2] Implement session creation service for defaults, leader assignment, and issue import in `app/domain/services/session_creation_service.py`
- [ ] T043 [US2] Implement new-session form/display/create routes in `app/web/routes_sessions.py`
- [ ] T044 [P] [US2] Build new-session template with upload and inline error states in `app/templates/session/new.html`
- [ ] T045 [US2] Add client form handling and inline CSV validation messaging in `app/static/js/new-session.js`
- [ ] T046 [US2] Emit `session_created` updates to history subscribers in `app/web/sockets.py`
- [ ] T047 [US2] Document Stage 4 (US2 session creation) run commands and verification flow in `README.md`

**Checkpoint**: US2 is independently functional and testable.

---

## Phase 5: User Story 3 - Review and Reopen Session History (Priority: P3)

**Goal**: Provide recency-sorted history with filtering and open-session navigation.

**Independent Test**: Load history with mixed sessions, apply filters (name/sprint/team), confirm descending order, and open a selected session.

### Tests for User Story 3

- [ ] T048 [P] [US3] Add contract tests for session history list/filter parameters in `tests/contract/test_us3_history_contract.py`
- [ ] T049 [P] [US3] Add integration tests for sorting, filter combinations, and open-session navigation in `tests/integration/test_us3_history_flow.py`

### Implementation for User Story 3

- [ ] T050 [US3] Implement session history query service for recency + filters in `app/domain/services/history_service.py`
- [ ] T051 [US3] Implement history and open-session routes in `app/web/routes_sessions.py`
- [ ] T052 [P] [US3] Build history page template with filter controls/cards in `app/templates/history/index.html`
- [ ] T053 [US3] Add client filter state/query serialization in `app/static/js/history.js`
- [ ] T054 [US3] Document Stage 5 (US3 history/reopen) run commands and validation flow in `README.md`

**Checkpoint**: US3 is independently functional and testable.

---

## Phase 6: User Story 4 - Configure Teams and Session Governance (Priority: P4)

**Goal**: Enable admin team management, base issue URL configuration, and completed session deletion.

**Independent Test**: Add/edit/delete teams, set base issue URL and verify issue link rendering behavior, delete completed session and confirm history removal.

### Tests for User Story 4

- [ ] T055 [P] [US4] Add contract tests for admin teams/config/completed-session endpoints in `tests/contract/test_us4_admin_contract.py`
- [ ] T056 [P] [US4] Add integration tests for admin configuration workflows and downstream session-link behavior in `tests/integration/test_us4_admin_flow.py`

### Implementation for User Story 4

- [ ] T057 [US4] Implement admin service for team lifecycle and base URL management in `app/domain/services/admin_service.py`
- [ ] T058 [US4] Implement admin routes for teams/config/completed-session deletion in `app/web/routes_admin.py`
- [ ] T059 [P] [US4] Build admin configuration template with team CRUD + base URL form in `app/templates/admin/index.html`
- [ ] T060 [P] [US4] Implement issue-link resolver with disabled-link fallback messaging in `app/domain/services/link_service.py`
- [ ] T061 [US4] Connect issue-link rendering to admin config in `app/templates/session/_issue_detail.html`
- [ ] T062 [US4] Document Stage 6 (US4 admin governance) run commands and verification flow in `README.md`

**Checkpoint**: US4 is independently functional and testable.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Cross-story hardening, quality gates, and delivery readiness.

- [ ] T063 [P] Add desktop-focused browser smoke tests for create/vote/reveal/complete flows in `tests/integration/test_smoke_core_flows.py`
- [ ] T064 [P] Add realtime performance verification tests for <=2s propagation targets in `tests/integration/test_performance_realtime.py`
- [ ] T065 Add accessibility and responsive CSS refinements for core flows in `app/static/css/styles.css`
- [ ] T066 [P] Add docstring compliance validation for modules/classes/functions in `pyproject.toml` and `tests/unit/test_docstring_compliance.py`
- [ ] T067 [P] Update quickstart with desktop automated test commands and mobile manual QA guidance in `specs/001-scrum-poker-system/quickstart.md`
- [ ] T068 Update `README.md` with a complete stage-by-stage developer runbook covering Setup, Foundational, US1, US2, US3, US4, and Polish validation in `README.md`
- [ ] T069 Run and document final validation (`black`, `ruff`, pytest suites) in `specs/001-scrum-poker-system/quickstart.md`

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
T021, T022, T023, T024, T025

# Parallel UI work after endpoint contracts stabilize
T033, T034

# Docs checkpoint for MVP stage
T036
```

### User Story 2

```bash
# Parallel tests
T037, T038, T039

# Parser and template work can overlap
T040, T044

# Docs checkpoint for US2 stage
T047
```

### User Story 3

```bash
# Parallel tests
T048, T049

# Service and template tasks can overlap
T050, T052

# Docs checkpoint for US3 stage
T054
```

### User Story 4

```bash
# Parallel tests
T055, T056

# Template and link service tasks can overlap
T059, T060

# Docs checkpoint for US4 stage
T062
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
