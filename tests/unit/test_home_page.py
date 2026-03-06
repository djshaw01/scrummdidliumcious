"""Unit tests for the home landing page template rendering.

Requirement traces:
  US1 — Branded home page with exact title and logo.
  US2 — Stable navigation baseline with semantic layout regions.
  US3 — Consistent cross-device presentation with responsive/fallback behavior.
"""


# ---------------------------------------------------------------------------
# US1 — Title rendering
# ---------------------------------------------------------------------------


def test_home_page_contains_exact_title_text(client):
    """Rendered page must contain the exact visible title 'SCRUMMDidliumcious'.

    :param client: Flask test client fixture.
    """
    response = client.get("/")
    assert b"SCRUMMDidliumcious" in response.data


def test_home_page_html_title_element_matches(client):
    """The HTML <title> element must contain 'SCRUMMDidliumcious'.

    :param client: Flask test client fixture.
    """
    response = client.get("/")
    assert b"<title>SCRUMMDidliumcious</title>" in response.data


# ---------------------------------------------------------------------------
# US1 — Logo source, path and placement hooks
# ---------------------------------------------------------------------------


def test_home_page_logo_src_references_svg_asset(client):
    """The logo <img> src attribute must reference 'images/scrumm_logo.svg'.

    :param client: Flask test client fixture.
    """
    response = client.get("/")
    assert b"images/scrumm_logo.svg" in response.data


def test_home_page_logo_has_top_left_placement_class(client):
    """The logo element must carry the top-left placement marker class.

    :param client: Flask test client fixture.
    """
    response = client.get("/")
    assert b"logo--top-left" in response.data


def test_home_page_logo_has_100em_height_style(client):
    """The logo element or its container must carry the 100em height CSS hook.

    :param client: Flask test client fixture.
    """
    response = client.get("/")
    # Either a class hook or inline style must encode the constraint.
    assert b"logo--100em" in response.data or b"100em" in response.data


def test_home_page_logo_has_aspect_ratio_class(client):
    """The logo element must carry a CSS hook that marks aspect-ratio preservation.

    :param client: Flask test client fixture.
    """
    response = client.get("/")
    assert b"logo--aspect-auto" in response.data


# ---------------------------------------------------------------------------
# US2 — Navigation baseline structure
# ---------------------------------------------------------------------------


def test_home_page_has_hero_region(client):
    """Rendered page must contain a dedicated hero/branding region.

    :param client: Flask test client fixture.
    """
    response = client.get("/")
    assert b'class="hero"' in response.data or b'data-region="hero"' in response.data


def test_home_page_has_nav_placeholder(client):
    """Rendered page must contain a non-interactive nav placeholder container.

    :param client: Flask test client fixture.
    """
    response = client.get("/")
    assert b'data-nav-placeholder' in response.data


def test_home_page_nav_placeholder_has_aria_label(client):
    """Nav placeholder must carry an accessibility label.

    :param client: Flask test client fixture.
    """
    response = client.get("/")
    assert b'aria-label' in response.data


# ---------------------------------------------------------------------------
# US3 — Responsive and fallback behavior hooks
# ---------------------------------------------------------------------------


def test_home_page_has_responsive_class_on_hero(client):
    """Hero region must carry a CSS class that enables responsive layout rules.

    :param client: Flask test client fixture.
    """
    response = client.get("/")
    assert b"hero--responsive" in response.data


def test_home_page_logo_has_alt_text(client):
    """Logo image must carry a non-empty alt attribute for fallback rendering.

    :param client: Flask test client fixture.
    """
    response = client.get("/")
    assert b'alt="' in response.data
    # Ensure alt value is not empty
    assert b'alt=""' not in response.data


def test_home_page_logo_has_onerror_fallback(client):
    """Logo image must carry an onerror handler or data attribute for graceful degradation.

    :param client: Flask test client fixture.
    """
    response = client.get("/")
    assert b"data-logo-fallback" in response.data or b"onerror" in response.data
