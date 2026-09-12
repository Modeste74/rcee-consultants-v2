"""Smoke tests for every public-facing route, plus the custom error pages."""
from app.models import Offering, OfferingType, Post


def test_public_pages_load(client):
    for path in ["/", "/about", "/offerings", "/blog", "/contact", "/privacy"]:
        resp = client.get(path)
        assert resp.status_code == 200, f"{path} returned {resp.status_code}"


def test_nonexistent_page_returns_custom_404(client):
    resp = client.get("/this-page-does-not-exist")
    assert resp.status_code == 404


def test_unpublished_offering_is_not_publicly_visible(client, db):
    offering = Offering(name="Draft Program", slug="draft-program",
                         description="Not ready yet", type=OfferingType.PROGRAM,
                         is_published=False)
    db.session.add(offering)
    db.session.commit()

    resp = client.get("/offerings")
    assert b"Draft Program" not in resp.data

    resp = client.get("/offerings/draft-program")
    assert resp.status_code == 404  # drafts aren't reachable by direct URL either


def test_published_offering_is_visible(client, db):
    offering = Offering(name="Career Coaching", slug="career-coaching",
                         description="1:1 coaching", type=OfferingType.PROGRAM,
                         is_published=True)
    db.session.add(offering)
    db.session.commit()

    resp = client.get("/offerings")
    assert b"Career Coaching" in resp.data

    resp = client.get("/offerings/career-coaching")
    assert resp.status_code == 200
    assert b"Career Coaching" in resp.data


def test_unpublished_post_is_not_publicly_visible(client, db, admin_user):
    post = Post(title="Draft Post", slug="draft-post", content="wip",
                author_id=admin_user.id, is_published=False)
    db.session.add(post)
    db.session.commit()

    resp = client.get("/blog")
    assert b"Draft Post" not in resp.data