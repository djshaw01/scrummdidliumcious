# Phase 0 Research: SCRUM Poker Voting System

## Decision 1: Real-time transport will use WebSockets via `Flask-Sock`
- Decision: Use a WebSocket endpoint for session event broadcast and client subscription, with REST endpoints for command actions.
- Rationale: The 500ms broadcast target and 50-concurrent-participant target are more reliably met with server push than short polling.
- Alternatives considered: HTTP polling (rejected due to request overhead and stale-state windows), Server-Sent Events with REST commands (rejected because bidirectional command/ack flow is less direct and complicates reconnect handling).

## Decision 2: Session commands remain RESTful and transaction-backed
- Decision: Keep create/join/vote/reveal/complete/admin updates as REST endpoints; emit domain events after committed writes.
- Rationale: REST keeps auditability and idempotency straightforward while WebSocket handles low-latency fanout.
- Alternatives considered: WebSocket-only command channel (rejected due to harder validation/error semantics), GraphQL subscriptions (rejected as unnecessary dependency and complexity).

## Decision 3: CSV parsing uses Python `csv.DictReader` with strict required-column validation
- Decision: Parse uploaded CSV server-side using standard library `csv`, normalize header names, enforce required fields (`Issue Type`, `Issue Key`, `Summary`), and ignore unknown columns.
- Rationale: Meets FR-004 without introducing parser dependencies and supports field-order independence.
- Alternatives considered: Pandas-based parsing (rejected due to heavy dependency footprint), client-only parsing (rejected because validation must be authoritative on server).

## Decision 4: Persist theme preference at user boundary with cookie/localStorage fallback
- Decision: Store selected theme in server-managed preference when user identity is available; mirror in browser storage for fast initial render and restore.
- Rationale: Satisfies persistence across browser restarts and cross-page consistency while remaining resilient for anonymous sessions.
- Alternatives considered: CSS media query only (rejected because user override persistence is required), cookie-only without client storage (rejected due to render flicker risk).

## Decision 5: Reveal race condition is resolved by optimistic lock + idempotent reveal
- Decision: Introduce issue-level `revealed_at` state and version check; first valid reveal transition wins, subsequent reveal attempts return current state with no mutation.
- Rationale: Guarantees consistent state under concurrent leader actions and satisfies edge-case requirements.
- Alternatives considered: Coarse process lock (rejected as non-scalable in multi-worker deployment), last-write-wins (rejected due to inconsistent user experience).

## Decision 6: Numeric average behavior excludes non-numeric cards
- Decision: Parse card values into numeric/non-numeric classes and compute averages using only numeric votes; non-numeric cards (`?`, `☕`, `♾`) are excluded from numerator and denominator.
- Rationale: Aligns with user-story acceptance language and keeps consensus math intuitive for teams.
- Alternatives considered: Treat non-numeric cards as zero values (rejected because it distorts numeric consensus and contradicts updated FR-010 intent).

## Decision 7: Base issue URL is composed safely by config + issue key
- Decision: Build issue hyperlink as `base_url.rstrip('/') + '/' + issue_key` when configured; otherwise render issue key as text.
- Rationale: Supports Jira/Azure URL patterns and required graceful fallback.
- Alternatives considered: Provider-specific URL templates (rejected for initial scope), hardcoded vendor behavior (rejected by configurability requirement).

## Decision 8: Purposeful testing matrix and performance checks
- Decision: Add unit tests for services/validation, contract tests for REST behavior, and integration tests for real-time events and latency thresholds.
- Rationale: Satisfies constitution principle for requirement-traceable tests and measurable performance gates.
- Alternatives considered: UI-only end-to-end testing as primary signal (rejected due to lower isolation and slower feedback loop).

## Dependency Justification Summary
- `Flask-Sock`: Required to support low-latency bidirectional real-time updates for voting/session events.
- No additional parsing dependencies: standard library `csv` is sufficient.
- No frontend framework dependency: Jinja + targeted JS keeps scope aligned to existing architecture.