# Phase 0 Research: SCRUM Poker Session Management

## Decision 1: Use a repository-interface architecture with in-memory adapters first
- Decision: Define domain repository interfaces and provide an `inmemory` implementation for this pass, with a parallel SQLAlchemy/PostgreSQL adapter boundary kept ready for later swap-in.
- Rationale: Supports rapid local experimentation and deterministic test data while preserving a clean path to persistent storage without rewriting service or route logic.
- Alternatives considered: Direct DB-first implementation was rejected for this pass because it slows feature iteration; embedding data access in route handlers was rejected because it violates SOLID and increases migration churn.

## Decision 2: Use Flask-SocketIO rooms for real-time session synchronization
- Decision: Implement real-time collaboration via SocketIO room-per-session events (`vote_cast`, `vote_cleared`, `issue_selected`, `votes_revealed`, `leader_changed`, `session_completed`).
- Rationale: Room scoping maps directly to session behavior in FR-022, FR-026, FR-028, and FR-018 and provides a straightforward local development model.
- Alternatives considered: Polling REST endpoints was rejected because it is less responsive and more complex for vote placeholder synchronization; Redis-backed pub/sub was deferred as premature for a single-node local run.

## Decision 3: Parse CSV with Python stdlib `csv` + explicit header normalization
- Decision: Use the standard `csv.DictReader` parser, normalize headers case-insensitively, validate required columns (`Issue Type`, `Issue Key`, `Summary`), and ignore unknown columns.
- Rationale: Meets FR-013 and FR-014 with minimal dependency footprint and aligns with constitution dependency discipline.
- Alternatives considered: Pandas-based parsing was rejected for MVP due to unnecessary dependency size; strict column-order parsing was rejected because it conflicts with FR-013.

## Decision 4: Keep issue-type validation strict and row-level
- Decision: Accept only `Story` and `Bug` issue types and produce row-level error feedback while allowing valid rows to proceed to import review.
- Rationale: Matches edge-case requirements and prevents bad rows from silently polluting session data.
- Alternatives considered: Rejecting the entire file on one invalid row was rejected due to lower usability; coercing unknown values into a fallback type was rejected because it hides data quality issues.

## Decision 5: Server-render with Jinja2, progressively enhanced by lightweight JS
- Decision: Build pages with Jinja2 templates and add targeted client-side JavaScript for SocketIO events and interaction state updates.
- Rationale: Keeps implementation simple, improves local run reliability, and supports fast delivery of responsive/mobile layouts and dark/light mode persistence.
- Alternatives considered: Full SPA frontend was rejected for this pass because it introduces additional complexity and tooling overhead not required by current requirements.

## Decision 6: Testing strategy maps directly to requirements and acceptance scenarios
- Decision: Use pytest for unit and integration tests, plus a small browser smoke suite for create-session, voting, reveal, and completion flows.
- Rationale: Supports constitution requirement for purposeful tests and ensures behavior coverage of the highest-priority paths.
- Alternatives considered: Unit-only testing was rejected because real-time synchronization and cross-user behavior require integration verification; broad E2E-only strategy was rejected due to slower feedback and weaker fault localization.

## Decision 7: Local runtime defaults to mock data but includes Postgres Docker path
- Decision: Run application locally with in-memory seed data by default; include `docker compose` PostgreSQL runtime and config switches for future persistent adapter testing.
- Rationale: Satisfies user goal to run and play locally now while preserving constitution container/data baseline.
- Alternatives considered: Postgres-only local boot was rejected for this iteration because it increases setup friction; skipping container docs entirely was rejected due to constitution requirements.

## Decision 8: Keep estimate computation explicit for special cards
- Decision: During reveal, compute average using numeric cards and map `?`, `☕️`, and `♾️` to numeric `0` per FR-030.
- Rationale: Ensures deterministic calculations and requirement compliance.
- Alternatives considered: Excluding special cards from averages was rejected because FR-030 explicitly defines zero mapping.
