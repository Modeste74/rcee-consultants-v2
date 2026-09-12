"""Tests for the public contact form: validation, spam protection, and
the admin-side inquiries inbox it feeds into."""
from app.models import Inquiry, InquiryStatus


def _valid_contact_data(**overrides):
    data = {
        "name": "Test Visitor",
        "email": "visitor@example.com",
        "phone": "",
        "offering_id": "",
        "message": "I'm interested in coaching",
        "website": "",  # honeypot - must stay empty for a real submission
    }
    data.update(overrides)
    return data


def test_valid_submission_creates_inquiry(client, db):
    resp = client.post("/contact", data=_valid_contact_data(), follow_redirects=True)
    assert resp.status_code == 200

    inquiry = Inquiry.query.first()
    assert inquiry is not None
    assert inquiry.name == "Test Visitor"
    assert inquiry.status == InquiryStatus.NEW


def test_missing_email_is_rejected(client, db):
    resp = client.post("/contact", data=_valid_contact_data(email=""), follow_redirects=True)
    assert Inquiry.query.count() == 0
    assert b"required" in resp.data.lower() or b"invalid" in resp.data.lower()


def test_invalid_email_format_is_rejected(client, db):
    resp = client.post("/contact", data=_valid_contact_data(email="not-an-email"), follow_redirects=True)
    assert Inquiry.query.count() == 0


def test_honeypot_field_silently_blocks_spam(client, db):
    """A bot that fills every field (including the hidden honeypot) should
    get redirected as if it succeeded, but nothing should be saved."""
    resp = client.post("/contact", data=_valid_contact_data(
        name="Bot", email="bot@spam.com", website="http://spam.example.com"
    ), follow_redirects=True)

    assert resp.status_code == 200  # looks successful to the bot
    assert Inquiry.query.count() == 0  # but nothing was actually saved


def test_submitted_inquiry_appears_in_admin_inbox(client, logged_in_client, db):
    client.post("/contact", data=_valid_contact_data())
    resp = logged_in_client.get("/admin/inquiries")
    assert b"Test Visitor" in resp.data


def test_admin_can_update_inquiry_status(logged_in_client, db):
    inquiry = Inquiry(name="Jane", email="jane@example.com", message="hi")
    db.session.add(inquiry)
    db.session.commit()

    logged_in_client.post(f"/admin/inquiries/{inquiry.id}/status", data={"status": "responded"})
    updated = db.session.get(Inquiry, inquiry.id)
    assert updated.status == InquiryStatus.RESPONDED