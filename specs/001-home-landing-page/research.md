# Phase 0 Research: Home Landing Page Foundation

## Decision 1: Serve the landing page as a Flask-rendered route (`GET /`)
- Decision: Implement a single Flask route for the home page and render a Jinja2 template.
- Rationale: Constitution mandates Flask/Jinja2, and this route directly maps to the primary user action (open landing page).
- Alternatives considered: Static HTML only (rejected due to required Flask stack baseline), SPA framework (rejected as unnecessary dependency and scope expansion).

## Decision 2: Keep logo source at `images/scrumm_logo.svg`
- Decision: Use the existing SVG at `images/scrumm_logo.svg` as the canonical logo asset path for the home page.
- Rationale: Requirement explicitly names this file; preserving the current asset location avoids duplicate assets and ambiguity.
- Alternatives considered: Copy logo into another static directory (rejected due to duplication risk), convert to raster image (rejected due to quality/scaling loss).

## Decision 3: Enforce 100em vertical logo size with preserved aspect ratio via CSS
- Decision: Apply CSS that sets logo height to `100em` and width to `auto`.
- Rationale: This directly satisfies explicit height and aspect-ratio requirements and remains resilient for SVG rendering.
- Alternatives considered: Hardcoded width/height pair (rejected as distortion risk), inline SVG transform scaling (rejected as unnecessary complexity).

## Decision 4: Mobile and desktop support via responsive layout constraints
- Decision: Use a simple responsive layout with top-left anchored brand block and viewport-safe spacing for both mobile and desktop.
- Rationale: Feature scope requires coherent cross-device branding, not full navigation architecture.
- Alternatives considered: Device-specific templates (rejected as overengineering), fixed-pixel layout (rejected for poor responsiveness).

## Decision 5: Purposeful testing strategy with pytest + Flask test client
- Decision: Add requirement-traceable tests that verify title text, logo reference path, and rendered style constraints tied to acceptance criteria.
- Rationale: Aligns with constitution testing principles and avoids cosmetic test inflation.
- Alternatives considered: Screenshot-only visual regression tool (rejected due to added dependency and setup overhead), no tests (rejected due to quality gate non-compliance).

## Decision 6: Performance validation for this thin page
- Decision: Validate `GET /` p95 response time threshold in local containerized conditions during QA runs.
- Rationale: Constitution requires explicit performance expectations; thin route should meet conservative latency target.
- Alternatives considered: No performance target (rejected by constitution), high-load benchmarking suite for this slice (rejected as disproportionate).

## Decision 7: Resolve technical unknown from user prompt
- Decision: Proceed with constitution-defined Python/Flask stack despite incomplete user phrase "I am building with...".
- Rationale: Project constitution is authoritative and fully specifies required implementation stack; no unresolved blockers remain.
- Alternatives considered: Pause for stack clarification (rejected because constitution already resolves the decision).
