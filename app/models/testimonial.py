import uuid
from datetime import datetime

from app.extensions import db


class Testimonial(db.Model):
    __tablename__ = "testimonials"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    offering_id = db.Column(db.String(36), db.ForeignKey("offerings.id"), nullable=True)
    author_name = db.Column(db.String(120), nullable=False)
    quote = db.Column(db.Text, nullable=False)
    is_published = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    offering = db.relationship("Offering", back_populates="testimonials")

    def __repr__(self):
        return f"<Testimonial by {self.author_name}>"
