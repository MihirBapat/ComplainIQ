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
    from app.routes.complaints import bp as complaints_bp
    from app.routes.fraud import bp as fraud_bp
    from app.routes.reports import bp as reports_bp
    from app.routes.model_info import bp as model_bp
    app.register_blueprint(auth_bp); app.register_blueprint(customers_bp)
    app.register_blueprint(accounts_bp); app.register_blueprint(transactions_bp)
    app.register_blueprint(complaints_bp); app.register_blueprint(fraud_bp)
    app.register_blueprint(reports_bp); app.register_blueprint(model_bp)

    @app.get("/")
    def index():
        from app.db import query_one, query_all
        stats = {
            "open_count": query_one("SELECT COUNT(*) AS n FROM complaints WHERE status IN ('OPEN','IN_REVIEW')")["n"],
            "high_urgency": query_one("SELECT COUNT(*) AS n FROM complaints WHERE urgency='HIGH' AND status!='RESOLVED'")["n"],
            "flags": query_one("SELECT COUNT(*) AS n FROM fraud_flags WHERE status='PENDING'")["n"],
            "transactions": query_one("SELECT COUNT(*) AS n FROM transactions")["n"],
        }
        return render_template("home.html", stats=stats, categories=query_all("SELECT * FROM v_category_stats"),
            sentiment=query_all("SELECT COALESCE(sentiment_label,'NEUTRAL') label, COUNT(*) total FROM complaints GROUP BY sentiment_label"),
            monthly=query_all("SELECT month, SUM(complaint_count) total FROM v_monthly_complaints GROUP BY month ORDER BY month"),
            recent=query_all("SELECT * FROM v_complaint_overview ORDER BY submitted_at DESC LIMIT 6"))

    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(error):
        return render_template("errors/500.html"), 500

    return app
