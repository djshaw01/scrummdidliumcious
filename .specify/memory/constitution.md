<!--
Sync Impact Report
- Version change: 1.3.0 → 1.4.0
- Modified principles:
	- VI. Responsible Dependency Management: expanded to include mandated framework/database/ORM/templating stack
	- I. Python 3.11+ Only, uv Package Management & PEP 8 Compliance (NON-NEGOTIABLE): expanded to require Black formatter
- Added sections:
	- VII. Containerized Development & Delivery
	- VIII. Self-Documenting Code & Modular File Organization
- Removed sections:
	- None
- Templates requiring updates:
	- ✅ updated: .specify/templates/plan-template.md
	- ✅ updated: .specify/templates/spec-template.md
	- ✅ updated: .specify/templates/tasks-template.md
	- ⚠ pending: .specify/templates/commands/*.md (directory not present in repository)
- Deferred TODOs:
	- None
-->

# scrummdidliumcious Constitution

## Core Principles

### I. Python 3.11+ Only, uv Package Management & PEP 8 Compliance (NON-NEGOTIABLE)
All production code, scripts, and automation in this repository MUST be written in
Python 3.11 or newer. Code MUST conform to PEP 8 style guidelines and use
consistent formatting across the repository. Code formatting MUST be enforced
with the `black` formatter across the codebase. Any proposal introducing a
non-Python implementation or Python versions below 3.11 is non-compliant unless
this constitution is formally amended.

All package and environment management MUST use `uv` exclusively. Use of `pip`,
`pip-tools`, `pipenv`, `poetry`, or any other package manager is prohibited.
Rationale: a single modern language/runtime baseline and a unified, reproducible
tooling stack minimizes maintenance overhead and review ambiguity.

### II. SOLID-Driven Design
Application architecture MUST follow SOLID principles. Modules MUST maintain
single responsibility, dependencies MUST be invertible where integration points
exist, and abstractions MUST be used to keep code open for extension without
modifying stable behavior. Rationale: SOLID alignment improves change safety,
testability, and long-term maintainability.

### III. Purposeful Testing Standards
Unit tests MUST validate meaningful functional behavior and observable outcomes
of components. Tests MUST NOT be added solely to increase test count or satisfy
cosmetic coverage goals. Each test suite MUST map to explicit requirements,
acceptance scenarios, or defect prevention goals. Rationale: testing investment
must maximize confidence per maintenance cost.

### IV. User Experience Consistency
User-facing behavior MUST remain consistent across equivalent workflows,
terminology, status messaging, and interaction patterns. Changes that alter user
flows MUST include acceptance criteria verifying consistency with established
patterns and documenting intentional deviations. Rationale: predictable UX
reduces user error and onboarding friction.

### V. Performance Requirements by Default
Features MUST define explicit performance expectations before implementation,
including latency, throughput, memory, or responsiveness targets relevant to the
feature scope. Implementations MUST be profiled or benchmarked when performance
risk is non-trivial, and regressions against declared targets MUST be resolved
before merge. Rationale: performance quality is a product requirement, not a
post-release optimization task.

### VI. Responsible Dependency Management
Third-party library usage MUST be intentional, minimal, and justified. Before
adding any dependency, the team MUST evaluate whether the need can be satisfied
by the Python standard library or an already-approved dependency. Each introduced
library MUST be documented with its purpose and explicit rationale in the feature
specification. Transitive dependency footprint MUST be considered. Libraries with
unclear maintenance status, restrictive licenses, broad scope creep, or
unnecessary API surface MUST be escalated for explicit approval before adoption.
The application stack is fixed: Flask for web application behavior, SQLAlchemy
for ORM, PostgreSQL as the preferred database flavor, and Jinja2 for templating.
Substitutions require formal constitution amendment.
Rationale: uncontrolled dependency growth increases attack surface, maintenance
burden, licensing risk, and onboarding complexity.

### VII. Containerized Development & Delivery
Local development MUST provide PostgreSQL via Docker. Final application delivery
MUST package the application in a Docker container image. Development workflows
MAY use mock data, Docker-hosted PostgreSQL, and/or run Flask directly on the
developer machine outside Docker when this improves iteration speed, as long as
production parity expectations are documented.
Rationale: consistent containerized data/runtime baselines reduce environment
drift while preserving practical day-to-day development ergonomics.

### VIII. Self-Documenting Code & Modular File Organization
Code MUST be self-documenting through clear naming and structure. Single-line
comments SHOULD be avoided and MUST only be used when clarification is truly
warranted. All public and private functions, methods, classes, and modules MUST
include Python docstrings. Function and method docstrings MUST document
parameters and return values and SHOULD include an example call when it adds
clarity. Related functions and methods MUST be kept physically near each other,
with private helpers declared after public interfaces. Class-based
implementations SHOULD be preferred when appropriate. Files SHOULD contain one
class per file, and unrelated functions/classes MUST NOT be mixed in the same
file; creating more files is preferred over mixed-responsibility files.
Rationale: explicit structure and documentation improve readability, onboarding,
review quality, and long-term maintainability.

## Engineering Constraints

- Repository code MUST use Python 3.11+ and PEP 8-compliant style.
- Repository formatting MUST use `black` as the canonical formatter.
- All package and environment management MUST use `uv`; `pip` and all other package
  managers are prohibited without exception.
- Application web framework MUST be Flask; ORM MUST be SQLAlchemy; templating
	MUST use Jinja2; PostgreSQL is the preferred database flavor.
- Local development MUST support PostgreSQL in Docker or be configured to use PostgreSQL on an external server
-  Release artifacts MUST include a Dockerized application image.
- Architecture and refactoring decisions MUST explicitly preserve SOLID intent.
- Pull requests MUST document requirement traceability for added or changed tests.
- User-facing changes MUST include UX consistency checks in specification and
  review notes.
- Performance-critical work MUST include measurable targets and validation method.
- Each third-party library added MUST be justified in the specification; standard
  library and existing dependencies MUST be considered as alternatives first.
- Code MUST remain self-documenting; single-line comments are exceptional.
- All functions/methods/classes/modules MUST include docstrings; function/method
	docstrings MUST document parameters and return values.
- Private functions/methods MUST be declared after public ones within a module or
	class when both are present.
- Files MUST NOT mix unrelated functions or classes; one class per file is the
	default preference.

## Delivery Workflow & Quality Gates

Work MUST progress through specification, plan, and task decomposition with
constitution checks at planning time and before merge. Reviewers MUST reject
changes that violate Python-only constraints, PEP 8 compliance, SOLID structure,
purposeful testing criteria, UX consistency expectations, defined performance
targets, uv-only package management, required Flask/SQLAlchemy/PostgreSQL/Jinja2
stack constraints, containerization requirements, or unjustified dependency
additions. Reviewers MUST also reject code that is not `black`-formatted, code
that lacks required docstrings, or code that mixes unrelated responsibilities in
a single file. Exceptions require
documented justification and formal amendment when the
exception is structural rather than temporary.

## Governance

This constitution supersedes conflicting process guidance in the repository.
Amendments require: (1) documented rationale, (2) impact analysis on templates
and workflow artifacts, and (3) reviewer approval in the same change set.

Versioning policy for this constitution follows semantic versioning:
- MAJOR: Backward-incompatible governance changes or principle removals/redefinitions.
- MINOR: New principle/section or materially expanded guidance.
- PATCH: Clarifications, wording improvements, or non-semantic edits.

Compliance review expectations:
- Every implementation plan MUST include a constitution check with pass/fail gates.
- Every pull request MUST state compliance with all core principles.
- Violations MUST be tracked with remediation tasks or rejected prior to merge.

**Version**: 1.4.0 | **Ratified**: 2026-02-19 | **Last Amended**: 2026-03-04
