from app import create_app


def test_app_creates_without_errors():
    app = create_app()
    assert app is not None


def test_user_management_routes_are_available():
    app = create_app()
    client = app.test_client()

    response = client.get("/users")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
