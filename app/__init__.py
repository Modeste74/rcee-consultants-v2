import os

from flask import Flask, render_template

from app.config import config_by_name
from app.extensions import db, migrate, login_manager, mail


def create_app(config_name=None):
    config_name = config_name or os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)

    from app.admin import admin_bp
    from app.public import public_bp

    app.register_blueprint(admin_bp)
    app.register_blueprint(public_bp)

    @app.context_processor
    def inject_globals():
        return {"whatsapp_number": app.config.get("WHATSAPP_NUMBER", "")}

    @app.errorhandler(404)
    def not_found(e):
        return render_template("public/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("public/500.html"), 500

    return app
