# Data Model: SCRUM Poker Voting System

## Entity: Team
- Purpose: Defines selectable team context for sessions.
- Fields:
  - `id` (UUID, PK)
  - `name` (string, unique, required)
  - `created_at` (timestamp, required)
- Validation rules:
  - `name` must be non-empty and unique (case-insensitive uniqueness policy recommended).

## Entity: Configuration
- Purpose: Stores global operational settings.
- Fields:
  - `id` (integer, PK; singleton row)
  - `base_url_for_issues` (string, nullable)
  - `default_theme` (enum: `light|dark`, nullable)
  - `updated_at` (timestamp, required)
- Validation rules:
  - `base_url_for_issues` must be a valid absolute URL when provided.
  - `default_theme` must be one of allowed enum values.

## Entity: Session
- Purpose: Represents one SCRUM poker activity lifecycle.
- Fields:
  - `id` (UUID, PK)
  - `name` (string, required)
  - `team_id` (UUID, FK -> Team.id, required)
  - `sprint_number` (integer, required)
  - `status` (enum: `active|completed`, required)
  - `leader_participant_id` (UUID, FK -> Participant.id, nullable until first participant persisted)
  - `card_set_name` (string, required; initial value `fibonacci_plus_specials`)
  - `created_at` (timestamp, required)
  - `completed_at` (timestamp, nullable)
- Validation rules:
  - `status=completed` requires `completed_at`.
  - Active session must have exactly one leader participant.

## Entity: Participant
- Purpose: Tracks users involved in a session and current participation state.
- Fields:
  - `id` (UUID, PK)
  - `session_id` (UUID, FK -> Session.id, required)
  - `user_identifier` (string, required)
  - `display_name` (string, nullable)
  - `joined_at` (timestamp, required)
  - `left_at` (timestamp, nullable)
  - `is_leader` (boolean, required)
  - `active_issue_id` (UUID, FK -> StorageIssue.id, nullable)
- Validation rules:
  - Unique constraint on (`session_id`, `user_identifier`).
  - Exactly one `is_leader=true` per active session.

## Entity: StorageIssue
- Purpose: One issue/story imported into a session for estimation.
- Fields:
  - `id` (UUID, PK)
  - `session_id` (UUID, FK -> Session.id, required)
  - `issue_type` (enum: `Story|Bug`, required)
  - `issue_key` (string, required)
  - `summary` (string, required)
  - `description` (text, nullable)
  - `uploaded_story_points` (string, nullable)
  - `final_estimate` (string, nullable)
  - `is_active` (boolean, required)
  - `revealed_at` (timestamp, nullable)
  - `created_at` (timestamp, required)
- Validation rules:
  - Unique constraint on (`session_id`, `issue_key`).
  - Required CSV columns must map to non-empty values.
  - Once `revealed_at` is set, new votes are rejected.

## Entity: Vote
- Purpose: Captures the latest vote per participant for a specific issue.
- Fields:
  - `id` (UUID, PK)
  - `issue_id` (UUID, FK -> StorageIssue.id, required)
  - `participant_id` (UUID, FK -> Participant.id, required)
  - `card_value` (string, required; allowed: `1,2,3,5,8,13,?,☕,♾`)
  - `created_at` (timestamp, required)
  - `updated_at` (timestamp, required)
- Validation rules:
  - Unique constraint on (`issue_id`, `participant_id`) for latest vote semantics.
  - Vote write blocked when issue/session is completed or issue revealed.

## Relationships
- `Team` 1 -> N `Session`
- `Session` 1 -> N `Participant`
- `Session` 1 -> N `StorageIssue`
- `StorageIssue` 1 -> N `Vote`
- `Participant` 1 -> N `Vote`
- `Session` 1 -> 1 `Participant` leader (enforced by `is_leader` + `leader_participant_id` consistency)

## Derived Views / Read Models
- `SessionListItemView`: session id, name, team, sprint, status, participant count, updated timestamp.
- `SessionDetailView`: session header, participant icons, current issue, vote count, reveal state, estimate controls.
- `IssueNavigationCardView`: issue key, summary snippet, final estimate, active/rejoin indicators.

## State Transitions

### Session
- `active` -> `completed`: triggered by leader completion action; locks further voting and updates.

### Issue
- `pending` (`revealed_at=null`) -> `revealed` (`revealed_at=now`) by leader reveal command.
- `revealed` -> `estimated`: by leader card selection or custom estimate save.
- `estimated` -> `pending` for next issue activation only (new issue becomes active; prior issue remains revealed/estimated).

### Participant Engagement
- `joined` -> `navigated-away`: participant selects non-active issue.
- `navigated-away` -> `rejoined`: participant clicks rejoin for active issue.
- `joined` -> `left`: participant leaves session; historical record retained.

## Concurrency and Consistency Rules
- Reveal action is idempotent: first successful transition sets `revealed_at`; subsequent reveals return existing state.
- Vote updates are atomic upserts under unique (`issue_id`, `participant_id`) constraint.
- Leadership transfer updates old/new leader flags in one transaction.
- Broadcast events are emitted only after transaction commit.