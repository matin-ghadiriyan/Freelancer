"""Application factory with security hardening."""
#imports
from flask import Flask , render_template , request , jsonify , abort
from app.extensions import db , csrf
from app.rate_limit_function import rate_limit

def create_app() -> Flask:

    app = Flask(__name__)

    # --- Extensions ------------------------------------------------------ #
    db.init_app(app)
    csrf.init_app(app)

    #--- rait limit --------------------------------------------------------#
    @app.before_request
    def before_request():
        if not rate_limit():
            abort(429)

    # --- Blueprints ------------------------------------------------------ #



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
