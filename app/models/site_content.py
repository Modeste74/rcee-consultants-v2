import uuid
from datetime import datetime

from app.extensions import db


class HeroSection(db.Model):
    """Only one row is expected to exist at a time - the admin edits it in place
    rather than creating new ones, but modeled as a table (not hardcoded config)
    so it stays editable from the admin panel without a deploy."""

    __tablename__ = "hero_section"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    heading = db.Column(db.String(200), nullable=False)
    subheading = db.Column(db.String(300), nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AboutUs(db.Model):
    __tablename__ = "about_us"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class OpeningStatement(db.Model):
    __tablename__ = "opening_statement"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    content = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
