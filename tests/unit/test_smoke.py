"""Smoke tests — verify the Stage 1 skeleton starts and all routes are reachable."""


def test_history_page_loads(client):
    """GET / returns 200 and renders the session history skeleton."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Session History" in response.data


def test_new_session_page_loads(client):
    """GET /sessions/new returns 200."""
    response = client.get("/sessions/new")
    assert response.status_code == 200
    assert b"New Session" in response.data


def test_session_detail_page_loads(client):
    """GET /sessions/<id> returns 200 for any session identifier."""
    response = client.get("/sessions/demo-session-123")
    assert response.status_code == 200
    assert b"Session Detail" in response.data


def test_admin_page_loads(client):
    """GET /admin/ returns 200."""
    response = client.get("/admin/")
    assert response.status_code == 200
    assert b"Admin" in response.data


def test_theme_toggle_script_present(client):
    """Base template includes the theme-toggle JavaScript."""
    response = client.get("/")
    assert b"toggleTheme" in response.data
