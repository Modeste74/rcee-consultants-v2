import uuid
from datetime import datetime
import enum

from app.extensions import db


class InquiryStatus(str, enum.Enum):
    NEW = "new"
    RESPONDED = "responded"
    ARCHIVED = "archived"


class Inquiry(db.Model):
    __tablename__ = "inquiries"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    offering_id = db.Column(db.String(36), db.ForeignKey("offerings.id"), nullable=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(30), nullable=True)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum(InquiryStatus), default=InquiryStatus.NEW, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    offering = db.relationship("Offering", back_populates="inquiries")

    def __repr__(self):
        return f"<Inquiry from {self.name} ({self.status})>"
