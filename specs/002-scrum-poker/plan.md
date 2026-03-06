# Implementation Plan: SCRUM Poker Voting System

**Branch**: `002-scrum-poker` | **Date**: 2026-03-05 | **Spec**: `/Users/dshaw/Documents/Projects/scrummdidliumcious/specs/002-scrum-poker/spec.md`
**Input**: Feature specification from `/Users/dshaw/Documents/Projects/scrummdidliumcious/specs/002-scrum-poker/spec.md`

## Summary

Implement a real-time SCRUM poker system in the existing Flask application with session creation from CSV, live participant voting and reveal, leader controls, admin/team configuration, and persistent light/dark theme support. The design uses SQLAlchemy + PostgreSQL persistence, Alembic migrations, Pydantic boundary validation, Flask-rendered pages, and a real-time event channel for <500ms broadcast targets.

## Technical Context

**Language/Version**: Python 3.11+  
**Package Manager**: `uv` (required; pip and all other managers are prohibited)  
**Primary Dependencies**: Flask (routes and server-side rendering), SQLAlchemy (ORM), Alembic (schema migrations), Pydantic (boundary validation), psycopg (PostgreSQL driver), Jinja2 (templates), Flask-Sock (WebSocket transport for real-time events; chosen over polling to meet latency target with lower request overhead)  
**Web Framework**: Flask (required)  
**ORM**: SQLAlchemy (required)  
**Templating**: Jinja2 (required for templating)  
**Storage**: PostgreSQL (preferred database flavor)  
**Local DB Runtime**: PostgreSQL via Docker (required baseline)  
**Deployment Artifact**: Docker container image for final application (required)  
**Testing**: pytest + Flask test client + focused integration tests for real-time behavior, CSV validation, and performance targets  
**Target Platform**: Dockerized Linux web service with modern desktop/mobile browsers as clients  
**Project Type**: Web application (server-rendered templates with REST + WebSocket endpoints)  
**Performance Goals**: Session event broadcast <= 500ms (SC-002), entry/session listing <= 2s for 500 sessions (SC-003), CSV validation error feedback <= 1s (SC-009)  
**Constraints**: Reveal is idempotent and race-safe, post-reveal voting blocked, responsive layout from 320px upward, theme selection persisted across sessions, no unnecessary third-party UI frameworks  
**Scale/Scope**: Up to 50 concurrent participants in one session, up to 500 sessions listed, one configurable card set initially

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- PASS: Python-only scope confirmed; no non-Python implementation introduced.
- PASS: Python runtime baseline remains 3.11+.
- PASS: Package management remains `uv` only.
- PASS: Required stack remains Flask + SQLAlchemy + Alembic + Pydantic + PostgreSQL + Jinja2.
- PASS: Local PostgreSQL in Docker and Dockerized deployment are part of implementation and validation flow.
- PASS: PEP 8 + `black` strategy is explicit in quickstart and planned CI checks.
- PASS: SOLID boundaries are planned with separated route, service, repository, and model responsibilities.
- PASS: Test plan is requirement-traceable (voting, reveal, session creation, admin, theme, performance).
- PASS: UX consistency checks are included for status messages, flow ordering, and terminology.
- PASS: Performance targets are explicit and measurable.
- PASS: New dependencies are justified with alternatives documented in `research.md`.
- PASS: Docstring expectations are preserved for all modules/classes/functions/methods.
- PASS: File organization plan keeps related responsibilities together and private helpers below public interfaces.
- PASS: Local and CI `black` enforcement remains part of quality gates.

## Project Structure

### Documentation (this feature)

```text
specs/002-scrum-poker/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── scrum-poker.openapi.yaml
└── tasks.md              # Created later by /speckit.tasks
```

### Source Code (repository root)

```text
app/
├── __init__.py
├── models/
│   ├── landing_page_view.py
│   ├── session.py
│   ├── participant.py
│   ├── storage_issue.py
│   ├── vote.py
│   ├── team.py
│   ├── configuration.py
│   └── dto/
│       ├── create_session_request.py
│       ├── vote_update_request.py
│       └── leadership_transfer_request.py
├── routes/
│   ├── home.py
│   ├── poker_pages.py
│   ├── poker_api.py
│   └── admin.py
├── services/
│   ├── session_service.py
│   ├── vote_service.py
│   ├── csv_issue_import_service.py
│   ├── theme_service.py
│   └── realtime_event_service.py
├── repositories/
│   ├── session_repository.py
│   ├── vote_repository.py
│   ├── configuration_repository.py
│   └── team_repository.py
├── realtime/
│   └── websocket.py
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── poker_entry.html
│   ├── poker_session.html
│   └── admin_configuration.html
└── static/
    ├── styles/
    │   ├── home.css
    │   ├── poker.css
    │   └── theme.css
    └── scripts/
        ├── poker-session.js
        └── theme-toggle.js

migrations/
└── versions/

tests/
├── unit/
│   ├── test_csv_issue_import_service.py
│   ├── test_vote_service.py
│   └── test_theme_service.py
├── contract/
│   └── test_scrum_poker_contract.py
└── integration/
    ├── test_scrum_poker_realtime.py
    ├── test_scrum_poker_performance.py
    └── test_scrum_poker_responsive_theme.py

docker/
├── Dockerfile
└── docker-compose.yml
```

**Structure Decision**: Keep the existing single Flask app and extend it with explicit domain modules (`models`, `services`, `repositories`, `realtime`) rather than introducing a separate backend/frontend split. This keeps implementation consistent with current architecture and minimizes migration risk while still supporting real-time UX.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

## Implementation Phases

### Phase 0: Research and Technical Decisions (Complete)
- Finalize real-time transport, CSV parsing rules, issue-link strategy, theme persistence strategy, and race-condition handling.
- Capture dependency rationale and alternatives in `research.md`.

### Phase 1: Design and Contracts (Complete)
- Finalize entity model, validation rules, and state transitions in `data-model.md`.
- Define API contract for session lifecycle, voting actions, admin configuration, and filters in `contracts/scrum-poker.openapi.yaml`.
- Provide operator/developer execution flow in `quickstart.md`.

### Phase 2: Persistence and Domain Foundation
- Create SQLAlchemy models and Alembic migrations for Session, Participant, StorageIssue, Vote, Team, Configuration.
- Implement repository layer and Pydantic request/response DTOs.
- Add baseline unit tests for entity validation and repository behavior.

### Phase 3: Session Lifecycle and Entry Experience
- Build entry page list/filter interactions for active and historical sessions and session creation flow with CSV upload.
- Implement participant auto-join, leave, and session navigation behavior.
- Implement leader transfer workflow and session completion state change.

### Phase 4: Real-Time Voting and Consensus
- Implement real-time channel + event broadcasting for join/leave/vote/reveal/leader-change.
- Implement vote cast/remove/change, reveal lock, numeric-only averaging (exclude non-numeric cards), selected-card consensus, and custom estimate save.
- Enforce reveal race safety and post-reveal voting prevention with transaction-safe guards.

### Phase 5: Admin, Theming, and Responsive UI
- Build admin configuration page for teams, completed session cleanup, and base URL management.
- Implement issue key linking behavior with graceful non-link fallback when base URL is unset.
- Implement home navigation integration and persistent light/dark theme toggle across pages and browser restarts.

### Phase 6: Performance and Readiness Validation
- Validate SC-002/SC-003/SC-004/SC-009 through integration/performance tests.
- Verify UX consistency acceptance scenarios for changed user flows.
- Run full test suite + `black --check` and prepare for `/speckit.tasks` decomposition.

## Post-Design Constitution Check

- PASS: Phase 0 and Phase 1 artifacts fully generated with no unresolved clarifications.
- PASS: Design remains compliant with required technology stack and governance constraints.
- PASS: Dependency additions are justified with alternatives documented.
- PASS: Performance targets, UX consistency expectations, and purposeful test strategy are explicit and measurable.
- PASS: No constitution violations require complexity exceptions.
