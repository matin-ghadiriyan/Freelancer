"""Application factory with security hardening."""
#imports
import os

from flask import Flask , render_template , request , jsonify , abort
from app.extensions import db , csrf
from app.rate_limit_function import rate_limit
from config import config

def create_app(config_name: str | None = None) -> Flask:

    app = Flask(__name__)

    # --- Configuration --------------------------------------------------- #
    config_name = config_name or os.getenv("FLASK_ENV", "development")
    app.config.from_object(config.get(config_name, config["development"]))

    # --- Extensions ------------------------------------------------------ #
    db.init_app(app)
    csrf.init_app(app)

    #--- rait limit --------------------------------------------------------#
    @app.before_request
    def before_request():
        if not rate_limit(limit=120 , ip=request.remote_addr , limit_time=120):
            abort(429)

    # --- Blueprints ------------------------------------------------------ #
    from app.routes import all_blueprints

    for blueprint in all_blueprints:
        app.register_blueprint(blueprint)

    # --- Template helpers ------------------------------------------------ #
    from app.routes.auth import current_user as _current_user

    @app.context_processor
    def inject_globals():
        return {
            "current_user": _current_user(),
            "site_name": "فریلنسرینو",
        }

    @app.template_filter("money")
    def money_filter(value):
        try:
            return f"${float(value):,.0f}"
        except (TypeError, ValueError):
            return "توافقی"

    @app.template_filter("stars")
    def stars_filter(value):
        try:
            score = int(round(float(value)))
        except (TypeError, ValueError):
            score = 0
        return "\u2605" * score + "\u2606" * (5 - score)

    @app.template_filter("jalali")
    def jalali_filter(value):
        return value.strftime("%Y-%m-%d") if value else ""


    # --- Error handlers -------------------------------------------------- #
    '''400 - Bad request'''
    @app.errorhandler(400)
    def bad_request(
        _: Exception
    ) -> str|dict:
        if request.path.startswith("/api/"):
            return jsonify(error="درخواست نامعتبر"), 400
        return render_template("errors/400.html"), 400

    '''403 - Forbidden'''
    @app.errorhandler(403)
    def forbidden(
        _: Exception
    ) -> str|dict:
        if request.path.startswith("/api/"):
            return jsonify(error="دسترسی مجاز نیست"), 403
        return render_template("errors/403.html"), 403

    '''404 - Not found'''
    @app.errorhandler(404)
    def not_found(
        _: Exception
    ) -> str|dict:
        if request.path.startswith("/api/"):
            return jsonify(error="یافت نشد"), 404
        return render_template("errors/404.html"), 404

    '''429 - Too many requests'''
    @app.errorhandler(429)
    def ratelimit_handler(
        _: Exception
    ) -> str|dict:
        if request.path.startswith("/api/"):
            return jsonify(error="تعداد درخواست‌ها بیش از حد مجاز"), 429
        return render_template("errors/429.html"), 429

    '''500 - Internal server error'''
    @app.errorhandler(500)
    def internal_error(
        _: Exception
    ) -> str|dict:
        db.session.rollback()
        if request.path.startswith("/api/"):
            return jsonify(error="خطای داخلی سرور"), 500
        return render_template("errors/500.html"), 500

    # --- Create tables automatically (first run without migrations) ------- #
    with app.app_context():
        db.create_all()

    # --- return app ------------------------------------------------------ #
    return app
