# Tasks: SCRUM Poker Session Management

**Input**: Design documents from `/specs/001-scrum-poker-system/`
**Prerequisites**: `plan.md` (required), `spec.md` (required for user stories), `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Included because the feature specification explicitly defines mandatory testing scenarios and independent test criteria per user story.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and baseline tooling for a locally runnable mock-data-first web app.

- [ ] T001 Create application and test directory skeleton per plan in app/ and tests/
- [ ] T002 Initialize project metadata and dependencies with uv in pyproject.toml
- [ ] T003 [P] Configure formatting and linting defaults in pyproject.toml for black and ruff
- [ ] T004 [P] Add environment variable templates for mock and postgres backends in .env.example
- [ ] T005 Create Flask app factory and extension bootstrap in app/__init__.py
- [ ] T006 Add runtime configuration classes for development/testing/postgres in app/config.py
- [ ] T007 [P] Create Docker runtime scaffolding for app and postgres in docker/Dockerfile
- [ ] T008 [P] Create compose stack for optional postgres runtime in docker/docker-compose.yml

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared domain and infrastructure that blocks all story work until complete.

**⚠️ CRITICAL**: No user story work should begin until this phase is complete.

- [ ] T009 Define domain entities (Team, Session, Participant, Issue, Vote, VotingCardSet, AdminConfig) in app/domain/entities/
- [ ] T010 Define repository interfaces for core aggregates in app/domain/repositories/
- [ ] T011 Implement in-memory repository adapters and seed fixtures in app/infra/repository_inmemory/
- [ ] T012 Scaffold SQLAlchemy repository adapter interfaces for future DB swap in app/infra/repository_sqlalchemy/
- [ ] T013 Implement shared service-layer errors and validation primitives in app/domain/services/errors.py
- [ ] T014 Create SocketIO initialization and session-room event helpers in app/web/sockets.py
- [ ] T015 Build shared base layout, flash/status components, and theme persistence hooks in app/templates/shared/base.html
- [ ] T016 Add shared client utilities for API calls, event subscriptions, and theme toggle in app/static/js/app.js
- [ ] T017 Establish global CSS tokens, responsive breakpoints, and light/dark themes in app/static/css/styles.css
- [ ] T018 Add common test fixtures and factory data for sessions/issues/participants in tests/conftest.py

**Checkpoint**: Foundation complete - user stories can now be implemented and validated independently.

---

## Phase 3: User Story 1 - Run a Live Estimation Session (Priority: P1) 🎯 MVP

**Goal**: Enable a leader to run active issue estimation with synchronized voting, reveal, and final estimate save.

**Independent Test**: Start one seeded session with multiple participants, select active issue, cast/change/clear votes, reveal votes, save final estimate, and verify all participants see synchronized state updates.

### Tests for User Story 1

- [ ] T019 [P] [US1] Add contract tests for session detail and vote lifecycle endpoints in tests/contract/test_us1_session_voting_contract.py
- [ ] T020 [P] [US1] Add integration tests for live voting/reveal/finalize and rejoin behavior in tests/integration/test_us1_live_estimation_flow.py
- [ ] T021 [P] [US1] Add SocketIO synchronization tests for vote_count_updated, issue_selected, votes_revealed, and leader_changed in tests/integration/test_us1_realtime_events.py
- [ ] T061 [P] [US1] Add unit tests for average calculation with mixed cards (`?`, `☕️`, `♾️` treated as `0`) in tests/unit/test_vote_average_rules.py
- [ ] T062 [P] [US1] Add integration test for automatic leader reassignment when leader leaves mid-session in tests/integration/test_us1_leader_reassignment.py

### Implementation for User Story 1

- [ ] T022 [US1] Implement session state orchestration service (active issue, participation state, completion guardrails) in app/domain/services/session_service.py
- [ ] T023 [US1] Implement vote domain service (cast/change/clear/reveal/average/finalize) in app/domain/services/vote_service.py
- [ ] T024 [US1] Implement session detail route and view-model composition in app/web/routes_sessions.py
- [ ] T025 [US1] Implement vote, reveal, final-estimate, rejoin, and leave endpoints in app/web/routes_sessions.py
- [ ] T026 [US1] Implement issue activation and leader designation endpoints in app/web/routes_sessions.py
- [ ] T027 [P] [US1] Build session detail template with 25/75 navigation-detail layout and participant status row in app/templates/session/detail.html
- [ ] T028 [P] [US1] Build issue detail partial with placeholders, vote row, reveal state, unique-card finalization, and average display in app/templates/session/_issue_detail.html
- [ ] T029 [US1] Implement client-side session interactions for voting, reveal, rejoin, and final estimate save in app/static/js/session-detail.js
- [ ] T030 [US1] Wire SocketIO room subscriptions and DOM synchronization for active issue and vote count updates in app/static/js/session-detail.js
- [ ] T031 [US1] Enforce leader-only action guards and user-facing invalid-action messaging in app/domain/services/session_service.py
- [ ] T063 [US1] Implement automatic leader reassignment and broadcast on leader leave in app/domain/services/session_service.py and app/web/sockets.py

**Checkpoint**: User Story 1 is independently functional and testable (MVP).

---

## Phase 4: User Story 2 - Create a Session from Imported Backlog (Priority: P2)

**Goal**: Let a team member create a session by entering metadata, uploading CSV, and navigating directly into the new session.

**Independent Test**: Open new-session UI, choose team, verify session-name prefill behavior, upload valid mixed-order CSV, begin session, and verify redirect + history visibility update.

### Tests for User Story 2

- [ ] T032 [P] [US2] Add contract tests for session creation and CSV validation responses in tests/contract/test_us2_create_session_contract.py
- [ ] T033 [P] [US2] Add integration tests for team prefill, CSV parsing rules, and create-session redirect in tests/integration/test_us2_session_creation_flow.py
- [ ] T034 [P] [US2] Add parser-focused tests for required header detection and row-level issue-type errors in tests/unit/test_us2_csv_parser.py

### Implementation for User Story 2

- [ ] T035 [US2] Implement CSV parser with header normalization and optional-field handling in app/infra/csv_import/parser.py
- [ ] T036 [US2] Implement CSV validation error formatter with row-level feedback payloads in app/infra/csv_import/validation.py
- [ ] T037 [US2] Implement session creation service (team default naming, leader assignment, issue import) in app/domain/services/session_creation_service.py
- [ ] T038 [US2] Implement new-session form routes and create endpoint in app/web/routes_sessions.py
- [ ] T039 [P] [US2] Build new-session template with metadata form and CSV upload UX states in app/templates/session/new.html
- [ ] T040 [US2] Add client-side form handling and inline validation messaging for CSV errors in app/static/js/new-session.js
- [ ] T041 [US2] Emit session_created event and update entry/history subscribers on create in app/web/sockets.py

**Checkpoint**: User Story 2 is independently functional and testable.

---

## Phase 5: User Story 3 - Review and Reopen Session History (Priority: P3)

**Goal**: Provide a session history page with recency ordering, filters, and open-session navigation.

**Independent Test**: Load history with mixed sessions, apply name/sprint/team filters, verify descending order, and open selected session detail.

### Tests for User Story 3

- [ ] T042 [P] [US3] Add contract tests for session history list and filter query parameters in tests/contract/test_us3_history_contract.py
- [ ] T043 [P] [US3] Add integration tests for sorting, filter combinations, and open-session navigation in tests/integration/test_us3_history_flow.py

### Implementation for User Story 3

- [ ] T044 [US3] Implement session history query service with descending recency and filter criteria in app/domain/services/history_service.py
- [ ] T045 [US3] Implement history and open-session routes in app/web/routes_sessions.py
- [ ] T046 [P] [US3] Build history page template with filter controls and session cards in app/templates/history/index.html
- [ ] T047 [US3] Add client-side filter state and query serialization in app/static/js/history.js

**Checkpoint**: User Story 3 is independently functional and testable.

---

## Phase 6: User Story 4 - Configure Teams and Session Governance (Priority: P4)

**Goal**: Allow administrators to manage teams, base issue URL, and completed session deletion.

**Independent Test**: Add/edit/delete teams, set base issue URL and verify link behavior in session views, and delete a completed session from admin configuration.

### Tests for User Story 4

- [ ] T048 [P] [US4] Add contract tests for admin team/config/completed-session endpoints in tests/contract/test_us4_admin_contract.py
- [ ] T049 [P] [US4] Add integration tests for admin configuration workflows and downstream session-link behavior in tests/integration/test_us4_admin_flow.py

### Implementation for User Story 4

- [ ] T050 [US4] Implement admin configuration service for team lifecycle and base URL management in app/domain/services/admin_service.py
- [ ] T051 [US4] Implement admin routes for teams/config/completed-session deletion in app/web/routes_admin.py
- [ ] T052 [P] [US4] Build admin configuration template with team CRUD and base URL form sections in app/templates/admin/index.html
- [ ] T053 [US4] Add issue-link resolver logic with disabled-link fallback messaging in app/domain/services/link_service.py
- [ ] T054 [US4] Connect issue link rendering to configured base URL in app/templates/session/_issue_detail.html

**Checkpoint**: User Story 4 is independently functional and testable.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Cross-story hardening, documentation, and final validation.

- [ ] T055 [P] Add end-to-end smoke test script for create-session and live-vote happy path in tests/integration/test_smoke_core_flows.py
- [ ] T056 [P] Add performance verification tests for <=2s update propagation in tests/integration/test_performance_realtime.py
- [ ] T057 Finalize responsive and accessibility pass (keyboard flow, focus states, contrast checks) in app/static/css/styles.css
- [ ] T058 [P] Update quickstart and developer notes for mock-data and optional postgres modes in specs/001-scrum-poker-system/quickstart.md
- [ ] T059 Run full validation commands and record results in specs/001-scrum-poker-system/quickstart.md
- [ ] T060 Add docstring compliance validation for modules/classes/functions and enforce in CI/local checks (Constitution VIII)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies, starts immediately.
- **Phase 2 (Foundational)**: Depends on Phase 1 and blocks all user story implementation.
- **Phase 3+ (User Stories)**: Depend on Phase 2 completion.
- **Phase 7 (Polish)**: Depends on completion of all desired user stories.

### User Story Dependencies

- **US1 (P1)**: Starts after Foundational and is the MVP baseline.
- **US2 (P2)**: Starts after Foundational; independent but integrates with session creation and event update patterns from shared foundation.
- **US3 (P3)**: Starts after Foundational; independent of US1/US2 business logic.
- **US4 (P4)**: Starts after Foundational; independent with shared entities/services.

### Within Each User Story

- Write tests first and confirm they fail for the intended behavior.
- Implement domain/services before routes.
- Implement routes before UI wiring.
- Complete story before moving to next priority checkpoint.

### Story Completion Order

- Recommended: **US1 -> US2 -> US3 -> US4**
- Parallel-capable after Foundational: **US2, US3, US4** can proceed in parallel if staffing allows.

## Parallel Execution Examples

### User Story 1

```bash
# Parallel tests
T019, T020, T021

# Parallel UI template work after service contracts are stable
T027, T028
```

### User Story 2

```bash
# Parallel tests
T032, T033, T034

# Parser and template work can overlap after interface agreement
T035, T039
```

### User Story 3

```bash
# Parallel tests
T042, T043

# Service and template can run in parallel with agreed view-model contract
T044, T046
```

### User Story 4

```bash
# Parallel tests
T048, T049

# Template and link service can run in parallel
T052, T053
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Deliver Phase 3 (US1) end-to-end.
3. Validate US1 independent test criteria before adding more scope.

### Incremental Delivery

1. Deliver US1 (live estimation loop).
2. Deliver US2 (session creation from CSV).
3. Deliver US3 (history/filter/reopen).
4. Deliver US4 (admin governance).
5. Execute Phase 7 polish and final validation.

### Parallel Team Strategy

1. Team collaborates on Phase 1 and Phase 2.
2. After checkpoint, split by story:
   - Dev A: US1/US2 critical path
   - Dev B: US3
   - Dev C: US4
3. Rejoin for Phase 7 cross-cutting hardening.
