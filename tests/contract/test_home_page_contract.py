"""Contract tests for the home landing page endpoint (GET /).

Requirement trace: OpenAPI contract — 200 response with text/html content type.
"""


def test_get_home_returns_200(client):
    """GET / must return HTTP 200.

    :param client: Flask test client fixture.
    """
    response = client.get("/")
    assert response.status_code == 200


def test_get_home_content_type_is_html(client):
    """GET / must return a text/html content type.

    :param client: Flask test client fixture.
    """
    response = client.get("/")
    assert "text/html" in response.content_type


def test_get_home_body_is_not_empty(client):
    """GET / must return a non-empty HTML body.

    :param client: Flask test client fixture.
    """
    response = client.get("/")
    assert len(response.data) > 0
