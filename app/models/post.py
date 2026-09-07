import uuid
from datetime import datetime

from app.extensions import db


class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    author_id = db.Column(db.String(36), db.ForeignKey("admins.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), unique=True, nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500), nullable=True)
    is_published = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    author = db.relationship("Admin", back_populates="posts")

    def __repr__(self):
        return f"<Post {self.title}>"
