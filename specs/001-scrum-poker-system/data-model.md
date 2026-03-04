# Data Model: SCRUM Poker Session Management

## Team
- Purpose: Named group used to scope sessions and defaults.
- Fields:
- `id` (UUID/string, required)
- `name` (string, required, unique within workspace)
- `is_active` (boolean, required, default `true`)
- `created_at` (datetime, required)
- `updated_at` (datetime, required)
- Validation:
- `name` must be non-empty and trimmed.
- Team delete is blocked if policy forbids deleting teams with active sessions (implementation policy choice).
- Relationships:
- One Team has many Sessions.

## Session
- Purpose: Time-bound estimation event tied to one team.
- Fields:
- `id` (UUID/string, required)
- `team_id` (FK -> Team, required)
- `name` (string, required)
- `sprint_number` (string/integer, required)
- `card_set_id` (FK -> VotingCardSet, required)
- `status` (enum: `active`, `completed`, required)
- `leader_participant_id` (FK -> Participant, required while active)
- `created_by_participant_id` (FK -> Participant, required)
- `created_at` (datetime, required)
- `completed_at` (datetime, nullable)
- Validation:
- Session cannot transition from `completed` back to `active` without explicit reopen flow.
- `leader_participant_id` must reference an active participant while session is `active`.
- Relationships:
- One Session has many Participants.
- One Session has many Issues.
- One Session has one active VotingCardSet.

## Participant
- Purpose: User presence and role within a session.
- Fields:
- `id` (UUID/string, required)
- `session_id` (FK -> Session, required)
- `display_name` (string, required)
- `initials` (string, required)
- `is_leader` (boolean, required)
- `join_state` (enum: `joined`, `left`, required)
- `evaluation_state` (enum: `active_issue_participating`, `browsing_other_issue`, required)
- `joined_at` (datetime, required)
- `left_at` (datetime, nullable)
- Validation:
- At most one participant with `is_leader=true` per session.
- Participants in `left` state cannot cast votes.
- Relationships:
- One Participant has many Votes.

## Issue
- Purpose: Imported work item being estimated in a session.
- Fields:
- `id` (UUID/string, required)
- `session_id` (FK -> Session, required)
- `order_index` (integer, required)
- `issue_type` (enum: `Story`, `Bug`, required)
- `issue_key` (string, required)
- `summary` (string, required)
- `description` (text, optional)
- `prior_estimate` (string/number, optional)
- `final_estimate` (string/number, optional)
- `is_active` (boolean, required)
- `revealed_at` (datetime, nullable)
- Validation:
- `issue_type` must be one of `Story` or `Bug`.
- `issue_key` and `summary` cannot be empty.
- Only one issue can have `is_active=true` in a session.
- Relationships:
- One Issue has many Votes.

## Vote
- Purpose: Participant card selection for the current active issue.
- Fields:
- `id` (UUID/string, required)
- `session_id` (FK -> Session, required)
- `issue_id` (FK -> Issue, required)
- `participant_id` (FK -> Participant, required)
- `selected_card` (string, required)
- `visibility_state` (enum: `hidden`, `revealed`, required)
- `cast_at` (datetime, required)
- `updated_at` (datetime, required)
- Validation:
- One active vote per (`issue_id`, `participant_id`) at a time.
- `selected_card` must be in the session card set.
- Vote mutations are blocked when session status is `completed`.

## VotingCardSet
- Purpose: Allowed card values for session voting.
- Fields:
- `id` (UUID/string, required)
- `name` (string, required)
- `cards` (ordered array of strings, required)
- `created_at` (datetime, required)
- Validation:
- Initial default set includes `1, 2, 3, 5, 8, 13, ?, ☕️, ♾️`.

## AdminConfig
- Purpose: Tenant/workspace-level settings used by session UX.
- Fields:
- `id` (singleton key)
- `base_issue_url` (string/url, optional)
- `theme_default` (enum: `light`, `dark`, optional)
- `updated_at` (datetime, required)
- Validation:
- If `base_issue_url` is missing, issue keys render as non-clickable with explanatory text.

## State Transitions

### Session
- `active` -> `completed`: Triggered by leader-only complete action (FR-017, FR-019).
- `completed` -> `active`: Not in scope for this feature unless reopen workflow is later specified.

### Issue Evaluation
- `not_selected` -> `active`: Leader selects issue (FR-022).
- `active` -> `revealed`: Leader triggers reveal (FR-028).
- `revealed` -> `finalized`: Leader selects or enters final estimate and saves (FR-029, FR-031).

### Participant Evaluation State
- `active_issue_participating` -> `browsing_other_issue`: Participant navigates away from active issue (FR-023).
- `browsing_other_issue` -> `active_issue_participating`: Participant uses Rejoin action (FR-023).
