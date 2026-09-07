import re
import unicodedata


def slugify(value: str) -> str:
    """Turn 'Career Coaching Program!' into 'career-coaching-program'."""
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    return re.sub(r"[-\s]+", "-", value)


def unique_slug(base_slug: str, model, exclude_id=None) -> str:
    """Append -2, -3, etc. if the base slug is already taken by another row."""
    slug = base_slug
    counter = 2
    while True:
        query = model.query.filter_by(slug=slug)
        if exclude_id is not None:
            query = query.filter(model.id != exclude_id)
        if not query.first():
            return slug
        slug = f"{base_slug}-{counter}"
        counter += 1
