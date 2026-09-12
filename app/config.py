import os
from datetime import timedelta


class Config:
    """Base config. All secrets come from environment variables - never hardcode them."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key-change-me")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///" + os.path.join(os.getcwd(), "dev.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail (used for inquiry notifications + admin password reset)
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", MAIL_USERNAME)

    # Where inquiry notifications should be sent (your mum's real inbox)
    ADMIN_NOTIFICATION_EMAIL = os.environ.get("ADMIN_NOTIFICATION_EMAIL")

    # Password reset token expiry
    RESET_TOKEN_MAX_AGE = int(timedelta(hours=1).total_seconds())

    # Cloud image storage (Cloudinary). If not set, falls back to local static/uploads
    # for local dev only - do NOT rely on local disk storage in production.
    CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.environ.get("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET")

    # Image processing
    MAX_IMAGE_DIMENSION = 1600  # px, longest side
    IMAGE_QUALITY = 82  # JPEG/WebP compression quality

    # WhatsApp contact button
    WHATSAPP_NUMBER = os.environ.get("WHATSAPP_NUMBER", "")  # e.g. 2547XXXXXXXX

    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8MB upload limit


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False

    def __init__(self):
        # Fail loudly in production if critical secrets are missing,
        # rather than silently running insecurely.
        required = ["SECRET_KEY", "DATABASE_URL"]
        missing = [k for k in required if not os.environ.get(k)]
        if missing:
            raise RuntimeError(f"Missing required env vars: {', '.join(missing)}")

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    SECRET_KEY = "test-secret-key"

config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
