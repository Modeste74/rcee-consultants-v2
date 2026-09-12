"""Tests for admin CRUD: offerings, testimonials, posts, site content."""
from app.models import Offering, Testimonial, Post, HeroSection


def test_create_offering(logged_in_client, db):
    resp = logged_in_client.post("/admin/offerings/new", data={
        "name": "Career Coaching",
        "type": "program",
        "description": "1:1 coaching sessions",
        "is_published": "y",
    }, follow_redirects=True)
    assert resp.status_code == 200

    offering = Offering.query.filter_by(name="Career Coaching").first()
    assert offering is not None
    assert offering.slug == "career-coaching"  # auto-generated from name


def test_offering_form_rejects_missing_required_fields(logged_in_client, db):
    resp = logged_in_client.post("/admin/offerings/new", data={
        "name": "",  # required field left blank
        "type": "program",
        "description": "Something",
    }, follow_redirects=True)

    assert Offering.query.count() == 0  # nothing should have been saved
    assert b"This field is required" in resp.data or b"required" in resp.data.lower()


def test_duplicate_offering_names_get_unique_slugs(logged_in_client, db):
    for _ in range(2):
        logged_in_client.post("/admin/offerings/new", data={
            "name": "Career Coaching", "type": "program", "description": "desc",
        })
    slugs = sorted(o.slug for o in Offering.query.all())
    assert slugs == ["career-coaching", "career-coaching-2"]


def test_edit_offering_updates_fields(logged_in_client, db):
    offering = Offering(name="Old Name", slug="old-name", description="old", type="program")
    db.session.add(offering)
    db.session.commit()

    logged_in_client.post(f"/admin/offerings/{offering.id}/edit", data={
        "name": "New Name", "type": "service", "description": "new description",
        "is_published": "y",
    })

    updated = db.session.get(Offering, offering.id)
    assert updated.name == "New Name"
    assert updated.type.value == "service"


def test_delete_offering(logged_in_client, db):
    offering = Offering(name="Temp", slug="temp", description="x", type="service")
    db.session.add(offering)
    db.session.commit()

    logged_in_client.post(f"/admin/offerings/{offering.id}/delete")
    assert Offering.query.count() == 0


def test_create_testimonial_linked_to_offering(logged_in_client, db):
    offering = Offering(name="Coaching", slug="coaching", description="d", type="service")
    db.session.add(offering)
    db.session.commit()

    logged_in_client.post("/admin/testimonials/new", data={
        "author_name": "Jane D.", "quote": "Fantastic!",
        "offering_id": offering.id, "is_published": "y",
    })

    testimonial = Testimonial.query.first()
    assert testimonial.offering_id == offering.id


def test_create_post_sets_current_admin_as_author(logged_in_client, db, admin_user):
    logged_in_client.post("/admin/posts/new", data={
        "title": "Welcome to RCEE", "content": "Our first post", "is_published": "y",
    })
    post = Post.query.first()
    assert post.author_id == admin_user.id
    assert post.slug == "welcome-to-rcee"


def test_update_hero_section_creates_row_if_none_exists(logged_in_client, db):
    assert HeroSection.query.count() == 0
    logged_in_client.post("/admin/content/hero", data={
        "heading": "Empowering Your Career", "subheading": "Coaching that gets results",
    })
    hero = HeroSection.query.first()
    assert hero.heading == "Empowering Your Career"