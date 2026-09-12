"""Tests for model relationships and behavior - the things that justified
choosing PostgreSQL over the original MongoDB approach."""
from app.models import Admin, Offering, OfferingType, Testimonial, Inquiry, InquiryStatus, Post


def test_admin_password_hashing(db):
    admin = Admin(username="jane", email="jane@example.com")
    admin.set_password("supersecret")
    db.session.add(admin)
    db.session.commit()

    assert admin.password_hash != "supersecret"  # never stored in plain text
    assert admin.check_password("supersecret") is True
    assert admin.check_password("wrongpassword") is False


def test_offering_testimonial_relationship(db):
    offering = Offering(name="Career Coaching", slug="career-coaching",
                         description="1:1 sessions", type=OfferingType.PROGRAM)
    db.session.add(offering)
    db.session.commit()

    testimonial = Testimonial(author_name="Jane D.", quote="Great program!", offering_id=offering.id)
    db.session.add(testimonial)
    db.session.commit()

    assert testimonial.offering.name == "Career Coaching"
    assert offering.testimonials.count() == 1


def test_offering_inquiry_relationship(db):
    offering = Offering(name="Team Training", slug="team-training",
                         description="Workshops", type=OfferingType.SERVICE)
    db.session.add(offering)
    db.session.commit()

    inquiry = Inquiry(name="Visitor", email="visitor@example.com",
                       message="Interested", offering_id=offering.id)
    db.session.add(inquiry)
    db.session.commit()

    assert inquiry.offering.name == "Team Training"
    assert inquiry.status == InquiryStatus.NEW  # default status


def test_deleting_offering_cascades_to_testimonials(db):
    """Testimonials are dependent on their offering; deleting the offering
    should clean up its testimonials rather than leaving orphaned rows."""
    offering = Offering(name="Youth Leadership", slug="youth-leadership",
                         description="For schools", type=OfferingType.PROGRAM)
    db.session.add(offering)
    db.session.commit()

    testimonial = Testimonial(author_name="A Parent", quote="Loved it", offering_id=offering.id)
    db.session.add(testimonial)
    db.session.commit()

    db.session.delete(offering)
    db.session.commit()

    assert Testimonial.query.count() == 0


def test_post_author_relationship(db, admin_user):
    post = Post(title="Welcome", slug="welcome", content="First post", author_id=admin_user.id)
    db.session.add(post)
    db.session.commit()

    assert post.author.username == "mum"
    assert admin_user.posts.count() == 1