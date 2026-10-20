"""SQLite connection, schema initialization, and query helpers."""

import sqlite3
from pathlib import Path

from flask import current_app, g


SQL_DIR = Path(__file__).resolve().parent.parent / "sql"
FIXED_CATEGORIES = (
    "Fraud / Unauthorized Transaction", "Credit Card Issue", "Loan / Mortgage Issue",
    "Bank Account / Service Issue", "Credit Reporting / Other",
)


def get_db():
    """Return the request-local connection with foreign keys enforced."""
    if "db" not in g:
        connection = sqlite3.connect(current_app.config["DATABASE"])
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        g.db = connection
    return g.db


def close_db(_error=None):
    """Close the request-local database connection."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query_all(sql, params=()):
    """Execute a parameterized select and return rows."""
    return get_db().execute(sql, params).fetchall()


def query_one(sql, params=()):
    """Execute a parameterized select and return one row."""
    return get_db().execute(sql, params).fetchone()


def execute(sql, params=()):
    """Execute a parameterized write, commit, and return its cursor."""
    cursor = get_db().execute(sql, params)
    get_db().commit()
    return cursor


def init_db(app=None):
    """Create all tables, indexes, triggers, views, and lookup categories."""
    if app is None:
        app = current_app
    db_path = Path(app.config["DATABASE"])
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        exists = connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='account_types'"
        ).fetchone()
        if not exists:
            for filename in ("schema.sql", "indexes.sql", "triggers.sql", "views.sql"):
                connection.executescript((SQL_DIR / filename).read_text(encoding="utf-8"))
        connection.executemany("INSERT OR IGNORE INTO complaint_categories (name) VALUES (?)", [(x,) for x in FIXED_CATEGORIES])
        connection.commit()
    finally:
        connection.close()


def init_app(app):
    """Register database lifecycle hooks and CLI initialization command."""
    app.teardown_appcontext(close_db)
    app.cli.add_command(_init_db_command)


import click
from flask.cli import with_appcontext


@click.command("init-db")
@with_appcontext
def _init_db_command():
    """Initialize the configured database."""
    init_db()
    click.echo("Database initialized.")
