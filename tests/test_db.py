"""Database constraints, triggers, and views."""

import sqlite3

import pytest

from app import create_app
from app.db import init_db


@pytest.fixture
def app(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": tmp_path / "test.db"})
    init_db(app)
    return app


@pytest.fixture
def db(app):
    connection = sqlite3.connect(app.config["DATABASE"])
    connection.execute("PRAGMA foreign_keys = ON")
    yield connection
    connection.close()


def setup_account(db):
    db.execute("INSERT INTO account_types (type_name) VALUES (?)", ("Savings",))
    db.execute("INSERT INTO customers (full_name, email) VALUES (?, ?)", ("Ada", "ada@example.com"))
    db.execute("INSERT INTO accounts (customer_id, type_id, account_number) VALUES (?, ?, ?)", (1, 1, "A-1"))
    db.commit()


def test_constraints_and_foreign_keys(db):
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("INSERT INTO customers (full_name, email) VALUES (?, ?)", ("Bad", "bad"))
    setup_account(db)
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("INSERT INTO transactions (account_id, txn_type, amount) VALUES (?, ?, ?)", (1, "DEBIT", -1))
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("INSERT INTO transactions (account_id, txn_type, amount) VALUES (?, ?, ?)", (99, "DEBIT", 1))


def test_triggers_and_cascade(db):
    setup_account(db)
    db.execute("INSERT INTO transactions (account_id, txn_type, amount) VALUES (?, ?, ?)", (1, "CREDIT", 50))
    assert db.execute("SELECT balance FROM accounts WHERE account_id=1").fetchone()[0] == 50
    fraud_category = db.execute("SELECT category_id FROM complaint_categories WHERE name=?", ("Fraud / Unauthorized Transaction",)).fetchone()[0]
    db.execute("INSERT INTO complaints (customer_id, account_id, txn_id, complaint_text, category_id, urgency) VALUES (?, ?, ?, ?, ?, ?)", (1, 1, 1, "This is an unauthorized transaction and I need help.", fraud_category, "HIGH"))
    assert db.execute("SELECT source FROM fraud_flags").fetchone()[0] == "NLP"
    assert db.execute("SELECT status FROM transactions WHERE txn_id=1").fetchone()[0] == "DISPUTED"
    db.execute("UPDATE complaints SET status=? WHERE complaint_id=1", ("RESOLVED",))
    assert db.execute("SELECT action FROM complaint_actions").fetchone()[0] == "STATUS_CHANGED"
    db.execute("DELETE FROM customers WHERE customer_id=1")
    assert db.execute("SELECT count(1) FROM accounts").fetchone()[0] == 0


def test_views_exist_and_query(db):
    setup_account(db)
    for query in (
        "SELECT * FROM v_complaint_overview", "SELECT * FROM v_fraud_dashboard",
        "SELECT * FROM v_category_stats", "SELECT * FROM v_monthly_complaints",
    ):
        db.execute(query).fetchall()
