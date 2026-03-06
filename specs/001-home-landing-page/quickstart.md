# Quickstart: Home Landing Page Foundation

## Prerequisites
- Python 3.11+
- `uv` installed
- Docker (for local PostgreSQL baseline)

## 1. Install dependencies
```bash
uv sync
```

## 2. Start PostgreSQL baseline (Docker)
```bash
docker compose -f docker/docker-compose.yml up -d postgres
```

## 3. Run Flask app locally
```bash
uv run flask --app app run --debug
```

## 4. Validate landing page behavior
1. Open `http://localhost:5000/`.
2. Confirm visible page title is `SCRUMMDidliumcious`.
3. Confirm logo uses `images/scrumm_logo.svg` in top-left placement.
4. Confirm logo height is 100em and aspect ratio is preserved.
5. Check desktop and mobile viewport behavior.

## 5. Run tests
```bash
uv run pytest -q
```

## 6. Run formatting check
```bash
uv run black --check .
```

## 7. Build container image
```bash
docker build -f docker/Dockerfile -t scrummdidliumcious:home-landing .
```

## Navigation Insertion Points (US2 — Future Navigation Baseline)

The home landing page reserves dedicated extension regions for future navigation controls.
No navigation links exist yet; the foundation is structurally ready.

### Where to add navigation

- **Template**: `app/templates/home.html`
  - The `<nav class="nav-baseline" data-nav-placeholder="true">` element is the insertion point.
  - Add navigation `<a>` elements or sub-components inside this `<nav>` block.
  - Remove or repurpose the HTML comment `<!-- Future navigation insertion point -->` when populating nav items.

- **Styles**: `app/static/styles/home.css`
  - `.nav-baseline` provides baseline flex layout and spacing.
  - Add child selectors (e.g., `.nav-baseline a`, `.nav-baseline .nav-item`) to style link items.

- **Base template**: `app/templates/base.html`
  - The `{% block nav %}{% endblock %}` extension block allows page-specific nav overrides.

### SC-004 Usability Protocol

**Goal**: Verify 4 out of 5 viewers can identify the brand within 10 seconds of viewing the page.

**Validation steps**:
1. Load `http://localhost:5000/` in a fresh browser session.
2. Present to each viewer without context or instruction.
3. Ask: "What product or service does this page represent?"
4. Record whether the viewer correctly identifies *SCRUMMDidliumcious* within 10 seconds.
5. Pass threshold: 4 out of 5 viewers must succeed.

**Pass criteria**: Logo and title visible within the first viewport at all tested breakpoints.
