# Implementation Plan: SCRUM Poker Session Management

**Branch**: `[001-scrum-poker-system]` | **Date**: 2026-03-04 | **Spec**: `/Users/dshaw/Documents/Projects/scrummdidliumcious/specs/001-scrum-poker-system/spec.md`
**Input**: Feature specification from `/specs/001-scrum-poker-system/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Build a locally runnable SCRUM poker web app that supports session history, admin configuration, CSV-based session creation, and live collaborative voting flows. For this pass, the app will use a mock-data-first architecture (in-memory repositories plus seed data) behind stable service interfaces, while preserving constitution-required Flask + SQLAlchemy + Jinja2 + PostgreSQL + Docker delivery direction so a database-backed adapter can be plugged in later without changing UI behavior.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.12  
**Package Manager**: `uv` (required; pip and all other managers are prohibited)  
**Primary Dependencies**: Flask (web routing + request lifecycle), SQLAlchemy (domain model persistence contract and future Postgres adapter), Jinja2 (server-rendered views), Flask-SocketIO (real-time vote and session synchronization), WTForms (validated form handling), python-csv/std `csv` (CSV ingestion), pytest (unit/integration testing), Playwright (critical flow browser verification)  
**Web Framework**: Flask (required)  
**ORM**: SQLAlchemy (required)  
**Templating**: Jinja2 (required for templating)  
**Storage**: Mock in-memory repositories for this planning pass; PostgreSQL is the target production store via SQLAlchemy models  
**Local DB Runtime**: PostgreSQL via Docker (required baseline)  
**Deployment Artifact**: Docker container image for final application (required)  
**Testing**: pytest for functional unit/integration tests mapped to FRs; Playwright smoke checks for create-session/vote/reveal/complete UX flows  
**Target Platform**: Linux/macOS local development and Linux container runtime for deployment
**Project Type**: Web application (Flask backend + Jinja templates + static JS client)  
**Performance Goals**: Session state updates (vote cast, reveal, leader change) visible to connected clients within 2 seconds in >=95% of interactions (aligns with SC-003)  
**Constraints**: Real-time collaboration for >=8 participants per session; responsive desktop/mobile UI; light/dark mode persistence; no data loss during single-process local runtime  
**Scale/Scope**: Team-level usage (up to ~20 concurrent active participants per session, hundreds of historical sessions per workspace)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- PASS: Python-only scope confirmed; no non-Python implementation introduced.
- PASS: Python runtime baseline fixed at 3.12 (>=3.11).
- PASS: Package management fixed to `uv` only.
- PASS: Flask, SQLAlchemy, Jinja2, and PostgreSQL direction preserved; mock repository layer is explicitly temporary for fast local iteration per Constitution VII.
- PASS: Local PostgreSQL Docker workflow and final Docker packaging included in quickstart + contracts assumptions.
- PASS: PEP 8 and `black` enforcement defined (`uv run black .` locally, CI format check).
- PASS: SOLID boundaries defined via repository/service/controller separation.
- PASS: Testing plan is requirement-traceable (FR and acceptance-scenario mapped).
- PASS: UX consistency criteria include shared status copy, voting state transitions, and mobile/desktop parity.
- PASS: Performance target and validation approach defined (SocketIO event timing checks + integration assertions).
- PASS: Dependencies listed with clear rationale; standard library used for CSV parsing before adding parser libraries.
- PASS: Docstring rules enforced for modules/classes/functions and parameter/return docs.
- PASS: File organization keeps related responsibilities grouped and private helpers below public interfaces.
- PASS: `black` execution strategy documented for local dev and CI.

## Project Structure

### Documentation (this feature)

```text
specs/001-scrum-poker-system/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
app/
├── __init__.py
├── config.py
├── web/
│   ├── routes_admin.py
│   ├── routes_sessions.py
│   └── sockets.py
├── domain/
│   ├── entities/
│   ├── services/
│   └── repositories/
├── infra/
│   ├── repository_inmemory/
│   ├── repository_sqlalchemy/
│   └── csv_import/
├── templates/
│   ├── admin/
│   ├── history/
│   ├── session/
│   └── shared/
└── static/
  ├── css/
  └── js/

tests/
├── unit/
├── integration/
└── contract/

docker/
├── Dockerfile
└── docker-compose.yml
```

**Structure Decision**: Use a web application structure centered on `app/` with server-rendered Jinja pages and SocketIO-powered real-time updates. Domain logic is isolated behind repository interfaces so mock data can be used immediately and swapped for SQLAlchemy/PostgreSQL repositories later with minimal changes.

## Complexity Tracking

No constitution violations identified in this plan.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

## Post-Design Constitution Check

- PASS: Phase 0 `research.md` resolves all technical unknowns with documented alternatives.
- PASS: Phase 1 artifacts (`data-model.md`, `contracts/openapi.yaml`, `quickstart.md`) remain Python + Flask + SQLAlchemy + Jinja2 + PostgreSQL aligned.
- PASS: Mock-data-first execution is explicitly bounded to repository adapters and does not alter required production stack direction.
- PASS: Purposeful testing, UX consistency, and performance validation approach are preserved in design artifacts.
- PASS: Dependency set remains minimal and justified; no prohibited package managers or stack substitutions introduced.
