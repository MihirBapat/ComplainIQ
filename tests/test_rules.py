"""Rule-based fraud check tests."""

from app import create_app
from app.db import execute, init_db, query_one
from app.services.fraud_rules import run_rules


def make_app(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": tmp_path / "rules.db"})
    init_db(app)
    return app


def add_account():
    execute("INSERT INTO account_types (type_name) VALUES (?)", ("Savings",))
    execute("INSERT INTO customers (full_name, email) VALUES (?, ?)", ("Rule User", "rule@example.com"))
    execute("INSERT INTO accounts (customer_id, type_id, account_number) VALUES (?, ?, ?)", (1, 1, "RULE-1"))


def add_transaction(amount, location="Delhi", timestamp="2026-10-20 12:00:00"):
    return execute("INSERT INTO transactions (account_id, txn_type, amount, location, txn_time) VALUES (?, ?, ?, ?, ?)", (1, "DEBIT", amount, location, timestamp)).lastrowid


def test_amount_spike_and_no_duplicate(tmp_path):
    app = make_app(tmp_path)
    with app.app_context():
        add_account()
        for number in range(5): add_transaction(100, timestamp=f"2026-10-19 12:0{number}:00")
        target = add_transaction(600, timestamp="2026-10-20 12:00:00")
        assert "Amount spike" in run_rules(target)
        assert run_rules(target) == []


def test_velocity_and_location_change(tmp_path):
    app = make_app(tmp_path)
    with app.app_context():
        add_account()
        for number in range(3): add_transaction(20, timestamp=f"2026-10-20 11:5{number}:00")
        target = add_transaction(20, timestamp="2026-10-20 12:00:00")
        assert "Transaction velocity" in run_rules(target)
        for number in range(5): add_transaction(20, "Delhi", f"2026-10-10 10:0{number}:00")
        foreign = add_transaction(20, "London", "2026-10-20 13:00:00")
        assert "Location change" in run_rules(foreign)
        assert query_one("SELECT COUNT(*) AS count FROM fraud_flags WHERE txn_id=?", (foreign,))["count"] == 1
