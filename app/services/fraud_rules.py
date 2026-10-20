"""Deterministic rule-based transaction fraud checks."""

from app.db import execute, query_one


RULES = (
    ("Amount spike", "HIGH"), ("Transaction velocity", "MEDIUM"), ("Location change", "MEDIUM"),
)


def _add_flag(txn_id, reason, severity):
    """Insert a rule flag only if this transaction/reason has not been flagged."""
    exists = query_one("SELECT flag_id FROM fraud_flags WHERE txn_id=? AND reason=?", (txn_id, reason))
    if not exists:
        execute("INSERT INTO fraud_flags (txn_id, source, reason, severity) VALUES (?, ?, ?, ?)", (txn_id, "RULE", reason, severity))
        return True
    return False


def run_rules(txn_id):
    """Run all rule checks for a newly saved transaction and return created reasons."""
    txn = query_one("SELECT * FROM transactions WHERE txn_id=?", (txn_id,))
    if not txn:
        raise ValueError("Transaction does not exist.")
    created = []
    prior = query_one("SELECT COUNT(*) AS count, AVG(amount) AS avg_amount FROM transactions WHERE account_id=? AND txn_type='DEBIT' AND txn_id<>?", (txn["account_id"], txn_id))
    if txn["txn_type"] == "DEBIT" and prior["count"] >= 5 and txn["amount"] > 5 * prior["avg_amount"]:
        if _add_flag(txn_id, "Amount spike", "HIGH"): created.append("Amount spike")
    velocity = query_one("SELECT COUNT(*) AS count FROM transactions WHERE account_id=? AND txn_type='DEBIT' AND txn_time BETWEEN datetime(?, '-10 minutes') AND ?", (txn["account_id"], txn["txn_time"], txn["txn_time"]))
    if txn["txn_type"] == "DEBIT" and velocity["count"] >= 4:
        if _add_flag(txn_id, "Transaction velocity", "MEDIUM"): created.append("Transaction velocity")
    location = query_one("SELECT location, COUNT(*) AS count FROM transactions WHERE account_id=? AND txn_id<>? AND txn_time >= datetime(?, '-30 days') AND location IS NOT NULL GROUP BY location ORDER BY count DESC LIMIT 1", (txn["account_id"], txn_id, txn["txn_time"]))
    if txn["location"] and location and txn["location"] != location["location"]:
        if _add_flag(txn_id, "Location change", "MEDIUM"): created.append("Location change")
    return created
