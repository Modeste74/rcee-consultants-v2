import re
import pytest
from app import create_app
from app.extensions import db as _db
from app.models import Admin


@pytest.fixture()
def app():
    """A fresh Flask app + in-memory SQLite DB for every test."""
    application = create_app("testing")
    with application.app_context():
        _db.create_all()
        yield application
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db(app):
    return _db


@pytest.fixture()
def admin_user(db):
    """A ready-made admin account, saved to the DB."""
    admin = Admin(username="mum", email="mum@example.com")
    admin.set_password("testpass123")
    db.session.add(admin)
    db.session.commit()
    return admin


@pytest.fixture()
def logged_in_client(client, admin_user):
    """A test client that's already authenticated as the admin."""
    client.post("/admin/login", data={"username": "mum", "password": "testpass123"})
    return client


def get_csrf_token(html_bytes):
    """Extract the CSRF token from a rendered form, when CSRF is enabled."""
    match = re.search(rb'name="csrf_token" type="hidden" value="([^"]+)"', html_bytes)
    return match.group(1).decode() if match else None