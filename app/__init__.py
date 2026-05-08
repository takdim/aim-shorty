import os
from flask import Flask
from config import config
from app.extensions import db, migrate, login_manager, bcrypt, mail, csrf, cache, limiter, jwt


def create_app(config_name: str | None = None) -> Flask:
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(config[config_name])

    # ── Extensions ─────────────────────────────────────────────────────────────
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)
    jwt.init_app(app)

    # ── Models (import agar Migrate bisa detect) ────────────────────────────────
    with app.app_context():
        from app.models import user, subscription, short_link, qr_code, landing_page, click_event, audit_log  # noqa: F401

    # ── Blueprints ─────────────────────────────────────────────────────────────
    from app.blueprints.public import public_bp
    from app.blueprints.auth import auth_bp
    from app.blueprints.dashboard import dashboard_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.api import api_bp
    from app.blueprints.billing import billing_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(billing_bp)

    # ── Context processors ─────────────────────────────────────────────────────
    @app.context_processor
    def inject_globals():
        from datetime import datetime
        return {"now": datetime.utcnow()}

    # ── Error handlers ─────────────────────────────────────────────────────────
    register_error_handlers(app)

    return app


def register_error_handlers(app: Flask) -> None:
    from flask import render_template

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(429)
    def too_many_requests(e):
        return render_template("errors/429.html"), 429

    @app.errorhandler(500)
    def internal_error(e):
        return render_template("errors/500.html"), 500
