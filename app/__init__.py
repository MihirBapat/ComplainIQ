"""Flask application factory."""

from flask import Flask, render_template

from config import Config


def create_app(test_config=None):
    """Create and configure the complaint analyzer application."""
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

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
