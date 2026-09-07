import uuid
from datetime import datetime
import enum

from app.extensions import db


class OfferingType(str, enum.Enum):
    PROGRAM = "program"
    SERVICE = "service"


class Offering(db.Model):
    """Unified table for what used to be separate Program / Service models.

    Kept as one table with a `type` field for the first build. If the business
    later needs genuinely different fields/behavior for programs vs services,
    this is the natural place to split into two tables (migrate by filtering
    on `type`).
    """

    __tablename__ = "offerings"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(170), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    type = db.Column(db.Enum(OfferingType), nullable=False, default=OfferingType.SERVICE)
    image_url = db.Column(db.String(500), nullable=True)
    is_published = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    testimonials = db.relationship(
        "Testimonial", back_populates="offering", cascade="all, delete-orphan", lazy="dynamic"
    )
    inquiries = db.relationship(
        "Inquiry", back_populates="offering", lazy="dynamic"
    )

    def __repr__(self):
        return f"<Offering {self.name} ({self.type})>"
