"""Image upload handling: resize + compress before storage.

This directly addresses the bloat problem from the original project, where
multi-megabyte, unresized images were committed straight into the repo.
Every image uploaded through the admin panel is normalized here first.
"""
from __future__ import annotations

import io
import os
import uuid

from PIL import Image, ImageOps

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def process_image(file_storage, max_dimension: int = 1600, quality: int = 82) -> tuple[bytes, str]:
    """Resize an uploaded image so its longest side is <= max_dimension,
    strip EXIF/orientation issues, and re-encode as compressed WebP.

    Returns (bytes, filename) ready to hand off to storage (local disk in dev,
    Cloudinary/S3 in production - see storage.py).
    """
    image = Image.open(file_storage.stream)
    image = ImageOps.exif_transpose(image)  # fix phone-camera rotation issues
    image = image.convert("RGB")

    width, height = image.size
    if max(width, height) > max_dimension:
        scale = max_dimension / max(width, height)
        image = image.resize((int(width * scale), int(height * scale)), Image.LANCZOS)

    buffer = io.BytesIO()
    image.save(buffer, format="WEBP", quality=quality, method=6)
    buffer.seek(0)

    filename = f"{uuid.uuid4().hex}.webp"
    return buffer.read(), filename


def save_locally(image_bytes: bytes, filename: str, upload_dir: str) -> str:
    """Fallback for local dev only. In production, use Cloudinary/S3 instead -
    a container filesystem is ephemeral and gets wiped on redeploy."""
    os.makedirs(upload_dir, exist_ok=True)
    path = os.path.join(upload_dir, filename)
    with open(path, "wb") as f:
        f.write(image_bytes)
    return f"/static/uploads/{filename}"
