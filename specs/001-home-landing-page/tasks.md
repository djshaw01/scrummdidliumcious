# Tasks: Home Landing Page Foundation

**Input**: Design documents from `/specs/001-home-landing-page/`
**Prerequisites**: `plan.md` (required), `spec.md` (required), `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Include only requirement-traceable functional tests tied to acceptance scenarios.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize project structure and baseline tooling.

- [ ] T001 Create Flask project directories and package markers in app/__init__.py
- [ ] T002 Initialize dependency and tool configuration with uv in pyproject.toml
- [ ] T003 [P] Add black formatting configuration and Python version constraints in pyproject.toml
- [ ] T004 [P] Create Docker baseline for app runtime in docker/Dockerfile
- [ ] T005 [P] Create local PostgreSQL compose service in docker/docker-compose.yml

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core app plumbing required before user stories.

**CRITICAL**: No user story implementation starts before this phase is complete.

- [ ] T006 Implement Flask app factory and base config loading in app/__init__.py
- [ ] T007 [P] Implement home blueprint module shell in app/routes/home.py
- [ ] T008 [P] Register route blueprint(s) in app/routes/__init__.py
- [ ] T009 [P] Add base template scaffold with extension blocks in app/templates/base.html
- [ ] T010 [P] Add global style scaffold and token variables in app/static/styles/home.css
- [ ] T011 Configure pytest app fixture and test client bootstrap in tests/conftest.py

**Checkpoint**: Foundation complete; user stories can proceed.

---

## Phase 3: User Story 1 - View Branded Home Page (Priority: P1) 🎯 MVP

**Goal**: Render a landing page with exact title and top-left logo at 100em height with preserved aspect ratio.

**Independent Test**: Request `GET /` and verify title text, logo source path, top-left placement marker, and 100em/aspect-ratio styling.

### Tests for User Story 1

- [ ] T012 [P] [US1] Add route contract test for GET / response and content type in tests/contract/test_home_page_contract.py
- [ ] T013 [P] [US1] Add functional test for exact visible title rendering in tests/unit/test_home_page.py
- [ ] T014 [P] [US1] Add functional test for logo source/path and placement hooks in tests/unit/test_home_page.py

### Implementation for User Story 1

- [ ] T015 [US1] Implement LandingPageView as a Pydantic boundary model with invariants in app/models/landing_page_view.py
- [ ] T016 [US1] Implement home route context assembly for title/logo fields in app/routes/home.py
- [ ] T017 [US1] Implement landing page template with title and logo markup in app/templates/home.html
- [ ] T018 [US1] Implement logo-specific CSS rules for top-left anchor, 100em height, and width auto in app/static/styles/home.css

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Use as Navigation Baseline (Priority: P2)

**Goal**: Provide a stable landing-page structure that is ready for future navigation additions without repurposing the page.

**Independent Test**: Verify page contains dedicated home layout regions and extension points while preserving branded hero behavior.

### Tests for User Story 2

- [ ] T019 [P] [US2] Add structure test for dedicated home/landing regions and extension blocks in tests/unit/test_home_page.py

### Implementation for User Story 2

- [ ] T020 [US2] Add semantic layout regions reserved for future navigation in app/templates/home.html
- [ ] T021 [US2] Add non-interactive navigation placeholder container and accessibility label in app/templates/home.html
- [ ] T022 [US2] Add baseline spacing/alignment rules for future nav container in app/static/styles/home.css
- [ ] T023 [US2] Document future navigation insertion points in specs/001-home-landing-page/quickstart.md

**Checkpoint**: User Story 2 remains independently testable and does not require implementing navigation controls.

---

## Phase 5: User Story 3 - Consistent Cross-Device Presentation (Priority: P3)

**Goal**: Keep title/logo readable and coherent on desktop and mobile viewports.

**Independent Test**: Validate responsive style behavior with mobile and desktop viewport checks.

### Tests for User Story 3

- [ ] T024 [P] [US3] Add responsive behavior test assertions for mobile and desktop style hooks in tests/unit/test_home_page.py
- [ ] T025 [P] [US3] Add fallback rendering test when logo asset cannot be loaded in tests/unit/test_home_page.py

### Implementation for User Story 3

- [ ] T026 [US3] Add responsive breakpoints for branded layout and safe spacing in app/static/styles/home.css
- [ ] T027 [US3] Add template fallback text/attributes for degraded logo rendering in app/templates/home.html
- [ ] T028 [US3] Add route-level fallback context for missing-logo scenario in app/routes/home.py

**Checkpoint**: User Story 3 is independently functional with cross-device and fallback behavior.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, performance checks, and docs alignment.

- [ ] T029 [P] Add requirement-traceable performance check for GET / p95 <= 300ms in tests/integration/test_home_page_performance.py
- [ ] T030 [P] Add README command-line run guide in README.md with prerequisites, `uv sync`, optional `docker compose -f docker/docker-compose.yml up -d postgres`, `uv run flask --app app run --debug`, and shutdown/cleanup commands
- [ ] T031 Validate quickstart steps against implemented files in specs/001-home-landing-page/quickstart.md
- [ ] T032 Verify OpenAPI contract and route behavior remain aligned in specs/001-home-landing-page/contracts/home-page.openapi.yaml
- [ ] T033 Enforce docstring completeness with parameter/return docs in app/__init__.py, app/routes/home.py, app/models/landing_page_view.py, and tests/unit/test_home_page.py
- [ ] T034 Validate SC-004 usability protocol (5 viewers, 10-second recognition check, 4/5 pass threshold) in specs/001-home-landing-page/quickstart.md
- [ ] T035 Validate README manual CLI execution steps from a fresh shell session in README.md

---

## Dependencies & Execution Order

### Phase Dependencies

- Phase 1 (Setup): no dependencies.
- Phase 2 (Foundational): depends on Phase 1 completion; blocks all user stories.
- Phase 3 (US1): depends on Phase 2 completion.
- Phase 4 (US2): depends on Phase 2 completion and can run after US1 MVP validation.
- Phase 5 (US3): depends on Phase 2 completion and can run independently of US2.
- Phase 6 (Polish): depends on completion of targeted user stories.

### User Story Dependencies

- US1 (P1): starts after Foundational phase; no dependency on other user stories.
- US2 (P2): starts after Foundational phase; should preserve US1 behavior.
- US3 (P3): starts after Foundational phase; should preserve US1 behavior.

### Graph

- `Setup -> Foundational -> US1 -> (US2 || US3) -> Polish`

---

## Parallel Execution Examples

### User Story 1

- Run `T012`, `T013`, and `T014` in parallel (tests in separate files/independent assertions).
- Run `T017` and `T018` in parallel after `T016` starts route context contract.

### User Story 2

- Run `T020` and `T022` in parallel (template structure vs style baseline).
- Run `T019` while implementation stabilizes to validate structure invariants.

### User Story 3

- Run `T024` and `T025` in parallel (responsive vs fallback tests).
- Run `T026` and `T027` in parallel before integrating fallback context in `T028`.

---

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate US1 independently.
4. Demo/deploy MVP if accepted.

### Incremental Delivery

1. Deliver US1 as MVP.
2. Add US2 baseline structure enhancements.
3. Add US3 responsive/fallback hardening.
4. Complete Polish phase checks.

### Team Parallel Strategy

1. Collaborate on Setup and Foundational phases.
2. After foundation: one developer focuses on US2 while another handles US3.
3. Rejoin for cross-cutting polish and contract/performance validation.
