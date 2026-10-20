"""Flask application factory."""

from flask import Flask, render_template

from config import Config
from app.db import init_app


def create_app(test_config=None):
    """Create and configure the complaint analyzer application."""
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
    init_app(app)
    from app.auth import bp as auth_bp
    from app.routes.customers import bp as customers_bp
    from app.routes.accounts import bp as accounts_bp
    from app.routes.transactions import bp as transactions_bp
    app.register_blueprint(auth_bp); app.register_blueprint(customers_bp)
    app.register_blueprint(accounts_bp); app.register_blueprint(transactions_bp)

    @app.get("/")
    def index():
        return render_template("home.html")

    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(error):
        return render_template("errors/500.html"), 500

    return app
