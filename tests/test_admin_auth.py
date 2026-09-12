"""Tests for admin login, logout, and access control."""


def test_admin_pages_require_login(client):
    """Every admin route except login/forgot-password should redirect
    an unauthenticated visitor to the login page."""
    protected_paths = [
        "/admin/", "/admin/offerings", "/admin/testimonials", "/admin/posts",
        "/admin/content/hero", "/admin/content/about", "/admin/content/opening",
        "/admin/inquiries",
    ]
    for path in protected_paths:
        resp = client.get(path, follow_redirects=False)
        assert resp.status_code == 302, f"{path} should redirect when not logged in"
        assert "/admin/login" in resp.headers["Location"]


def test_login_with_correct_credentials_succeeds(client, admin_user):
    resp = client.post("/admin/login",
                        data={"username": "mum", "password": "testpass123"},
                        follow_redirects=True)
    assert resp.status_code == 200
    assert b"Dashboard" in resp.data


def test_login_with_wrong_password_fails(client, admin_user):
    resp = client.post("/admin/login",
                        data={"username": "mum", "password": "wrongpassword"},
                        follow_redirects=True)
    # A failed login re-renders the login page rather than redirecting -
    # checking the final URL is more reliable than checking for the word
    # "Dashboard", which also appears in the nav bar on the login page itself.
    assert resp.request.path == "/admin/login"
    assert b"Invalid username or password" in resp.data


def test_logged_in_admin_can_reach_dashboard(logged_in_client):
    resp = logged_in_client.get("/admin/")
    assert resp.status_code == 200
    assert b"Dashboard" in resp.data


def test_logout_ends_session(logged_in_client):
    logged_in_client.get("/admin/logout")
    resp = logged_in_client.get("/admin/", follow_redirects=False)
    assert resp.status_code == 302  # bounced back to login after logout