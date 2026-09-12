"""Tests for the forgot-password / reset-password flow, including the
mail-failure-shouldn't-crash-the-request fix from manual testing."""
from itsdangerous import URLSafeTimedSerializer


def test_forgot_password_does_not_crash_without_mail_configured(client, admin_user, app):
    """Regression test: this used to raise an unhandled exception and 500
    when no SMTP server was reachable. It should now degrade gracefully."""
    resp = client.post("/admin/forgot-password", data={"email": "mum@example.com"},
                        follow_redirects=True)
    assert resp.status_code == 200
    assert b"reset link has been sent" in resp.data.lower()


def test_forgot_password_gives_same_message_for_unknown_email(client, db):
    """Doesn't reveal whether an email is a registered admin - avoids
    leaking account existence to an attacker."""
    resp = client.post("/admin/forgot-password", data={"email": "nobody@example.com"},
                        follow_redirects=True)
    assert b"reset link has been sent" in resp.data.lower()


def test_reset_password_with_valid_token_changes_password(client, admin_user, app):
    serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    token = serializer.dumps(admin_user.id, salt="password-reset")

    resp = client.post(f"/admin/reset-password/{token}", data={
        "password": "newpassword456", "confirm_password": "newpassword456",
    }, follow_redirects=True)
    assert resp.status_code == 200

    # Confirm login now works with the new password
    login_resp = client.post("/admin/login",
                              data={"username": "mum", "password": "newpassword456"},
                              follow_redirects=True)
    assert b"Dashboard" in login_resp.data


def test_reset_password_with_invalid_token_is_rejected(client, admin_user):
    resp = client.get("/admin/reset-password/not-a-real-token", follow_redirects=True)
    assert b"Invalid reset link" in resp.data


def test_reset_password_mismatched_confirmation_is_rejected(client, admin_user, app):
    serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
    token = serializer.dumps(admin_user.id, salt="password-reset")

    client.post(f"/admin/reset-password/{token}", data={
        "password": "newpassword456", "confirm_password": "somethingelse",
    })

    # Old password should still work since the mismatched reset shouldn't apply
    login_resp = client.post("/admin/login",
                              data={"username": "mum", "password": "testpass123"},
                              follow_redirects=True)
    assert b"Dashboard" in login_resp.data