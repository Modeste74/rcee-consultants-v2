# RCEE Consultants — v2

A rebuild of the RCEE Consultants site: Flask + PostgreSQL, planned data model,
proper repo hygiene from commit one.

## Why this rebuild exists

The original version (Flask + MongoDB) was built impromptu without planning
the data model first. It worked, but:
- Programs and services had no relationships to inquiries/testimonials
- The repo shipped with its virtual environment and unresized images baked
  in (~32MB, most of it avoidable)
- No password recovery, spam protection, or error pages

This version fixes those specifically, rather than changing the stack for
its own sake.

## Stack

- Flask (app factory pattern, blueprints)
- PostgreSQL + SQLAlchemy + Flask-Migrate (chosen because Offerings now have
  real foreign-key relationships to Testimonials and Inquiries — see the ERD
  discussed during planning)
- Flask-Login for admin auth, itsdangerous for password-reset tokens
- Flask-Mail for inquiry notifications + password reset emails
- Pillow for automatic image resize/compression on upload
- Cloudinary for production image storage (local disk is only a dev fallback)

## Local setup

```bash
python -m venv venv
source venv/bin/activate        # venv/Scripts/activate on Windows
pip install -r requirements.txt

cp .env.example .env            # then fill in real values
# For quick local testing you can leave DATABASE_URL unset - it falls back
# to a local sqlite file (dev only, not for production).

flask --app wsgi db init         # first time only
flask --app wsgi db migrate -m "initial schema"
flask --app wsgi db upgrade

flask --app wsgi run
```

## Project structure

```
app/
  admin/          # admin auth + (soon) CRUD routes
  public/         # public-facing routes
  models/         # SQLAlchemy models, one file per entity
  utils/          # image processing, email sending
  templates/      # Jinja templates, split public/admin
  static/         # CSS/JS, local upload fallback (dev only)
config.py         # env-var driven config, fails loudly if secrets missing in prod
extensions.py     # shared extension instances (avoids circular imports)
wsgi.py           # entrypoint for local run + gunicorn in production
```

## Status

Skeleton stage: models, auth, contact form (with honeypot spam protection),
password reset flow, and image processing utility are in place. Admin CRUD
screens for offerings/testimonials/posts/hero content, and real page styling,
are the next phase.

## Deployment (planned)

Render or Railway: web service running `gunicorn wsgi:app`, managed Postgres
add-on, environment variables set from `.env.example`, Cloudinary for image
storage so uploads survive redeploys.
