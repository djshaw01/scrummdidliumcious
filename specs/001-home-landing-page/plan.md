# Implementation Plan: Home Landing Page Foundation

**Branch**: `001-home-landing-page` | **Date**: 2026-03-05 | **Spec**: `/Users/dshaw/Documents/Projects/scrummdidliumcious/specs/001-home-landing-page/spec.md`
**Input**: Feature specification from `/Users/dshaw/Documents/Projects/scrummdidliumcious/specs/001-home-landing-page/spec.md`

## Summary

Deliver a dedicated home/landing page that displays the exact visible title `SCRUMMDidliumcious` and the `images/scrumm_logo.svg` logo at the top-left, rendered at 100em height with preserved aspect ratio across desktop and mobile. Implementation will use a minimal Flask + Jinja2 server-rendered page with dedicated style rules and purposeful acceptance-focused tests.

## Technical Context

**Language/Version**: Python 3.11+  
**Package Manager**: `uv` (required; pip and all other managers are prohibited)  
**Primary Dependencies**: Flask (HTTP routing and template rendering), SQLAlchemy (required ORM baseline, no feature-specific models in this slice), Alembic (required migration workflow baseline), Pydantic (required boundary modeling baseline), psycopg (PostgreSQL driver), Jinja2 (HTML templating via Flask)  
**Web Framework**: Flask (required)  
**ORM**: SQLAlchemy (required)  
**Templating**: Jinja2 (required for templating)  
**Storage**: PostgreSQL (preferred database flavor)  
**Local DB Runtime**: PostgreSQL via Docker (required baseline)  
**Deployment Artifact**: Docker container image for final application (required)  
**Testing**: pytest (functional route and response-content assertions tied to acceptance scenarios)  
**Target Platform**: Dockerized Linux web service (browser clients on desktop and mobile)
**Project Type**: Web application (server-rendered HTML)  
**Performance Goals**: p95 server response time for `GET /` <= 300ms in local containerized environment; first meaningful branded content visible within 2.5s on standard local network test profile  
**Constraints**: Logo must remain undistorted at 100em height, title text must match exact case/spelling, layout must stay recognizable at mobile and desktop breakpoints, no unnecessary third-party UI libraries  
**Scale/Scope**: Single public landing route, static logo asset rendering, no authentication, no user-generated data, no database writes in this feature slice

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- PASS: Python-only scope confirmed; no non-Python implementation introduced.
- PASS: Python runtime baseline confirmed at version 3.11 or newer.
- PASS: Package management confirmed as `uv` only; no pip/pipenv/poetry usage.
- PASS: Flask, SQLAlchemy, Jinja2, and PostgreSQL stack requirements are satisfied.
- PASS: Local PostgreSQL Docker workflow and final Docker packaging are defined.
- PASS: PEP 8 compliance strategy defined and `black` formatter enforcement is specified.
- PASS: SOLID design approach documented for route, service, and template boundaries.
- PASS: Testing plan includes only purposeful functional tests tied to requirements.
- PASS: UX consistency criteria defined for title/logo behavior and acceptance scenarios.
- PASS: Performance targets and validation method (response-time measurement) are defined.
- PASS: Dependencies are explicitly justified and constrained to required stack.
- PASS: Docstring requirements are defined for public/private modules/classes/functions.
- PASS: File organization keeps related responsibilities grouped and avoids mixed concerns.
- PASS: Plan defines `black` execution in local workflow and CI.

## Project Structure

### Documentation (this feature)

```text
specs/001-home-landing-page/
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
├── models/
│   └── landing_page_view.py
├── routes/
│   └── home.py
├── templates/
│   └── home.html
└── static/
    └── styles/
        └── home.css

images/
└── scrumm_logo.svg

tests/
├── contract/
│   └── test_home_page_contract.py
├── integration/
│   └── test_home_page_performance.py
└── unit/
    └── test_home_page.py

docker/
├── Dockerfile
└── docker-compose.yml
```

**Structure Decision**: Use a single Flask web application structure with server-rendered templates. Keep the existing `images/scrumm_logo.svg` as the source asset and reference it directly for the landing-page logo requirement, while placing page-specific styling under app/static/styles/ and organizing requirement-traceable tests across tests/contract/, tests/integration/, and tests/unit/.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

## Post-Design Constitution Check

- PASS: Phase 0/1 artifacts (`research.md`, `data-model.md`, `contracts/`, `quickstart.md`) are present and consistent with Python 3.11+ and `uv` workflow.
- PASS: Required stack usage (Flask, SQLAlchemy, Alembic, Pydantic, PostgreSQL, Jinja2) is preserved in technical context and design decisions.
- PASS: UX consistency and performance targets remain measurable and tied to acceptance expectations.
- PASS: Dependency additions are constrained to required stack; no optional third-party UI framework introduced.
- PASS: Planned test strategy remains purposeful and requirement-traceable.
- PASS: No constitution violations identified; complexity exceptions are not required.
