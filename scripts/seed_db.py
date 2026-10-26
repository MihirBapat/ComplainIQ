"""Create repeatable demo data for the application."""

import argparse
import random
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from faker import Faker
from werkzeug.security import generate_password_hash

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def seed(reset=False):
    """Seed the database with the project-required deterministic demo data."""
    from app import create_app
    from app.db import FIXED_CATEGORIES, init_db
    database = ROOT / "data" / "complaints.db"
    if reset and database.exists():
        database.unlink()
    app = create_app(); init_db(app)
    random.seed(42); fake = Faker(); Faker.seed(42)
    connection = sqlite3.connect(database); connection.execute("PRAGMA foreign_keys = ON")
    cursor = connection.cursor()
    types = ("Savings", "Current", "Credit Card", "Loan", "Business")
    cursor.executemany("INSERT OR IGNORE INTO account_types (type_name) VALUES (?)", [(name,) for name in types])
    cursor.executemany("INSERT OR IGNORE INTO complaint_categories (name) VALUES (?)", [(name,) for name in FIXED_CATEGORIES])
    cursor.executemany("INSERT OR IGNORE INTO staff (username, password_hash, role) VALUES (?, ?, ?)", [
        ("admin", generate_password_hash("admin123"), "ADMIN"), ("agent", generate_password_hash("agent123"), "AGENT")])
    customers = [(fake.name(), f"customer{number}@example.com", fake.msisdn()[:10], fake.city()) for number in range(1, 201)]
    cursor.executemany("INSERT INTO customers (full_name, email, phone, city) VALUES (?, ?, ?, ?)", customers)
    accounts = []
    for customer_id in range(1, 201):
        for number in range(1 + (customer_id % 2)):
            accounts.append((customer_id, (customer_id + number) % 5 + 1, f"AC{customer_id:04d}{number:02d}"))
    cursor.executemany("INSERT INTO accounts (customer_id, type_id, account_number) VALUES (?, ?, ?)", accounts)
    transactions = []
    base = datetime.now() - timedelta(days=180)
    locations = ("Delhi", "Mumbai", "Bengaluru", "Kolkata")
    for number in range(5000):
        account_id = number % len(accounts) + 1
        txn_type = "CREDIT" if number % 5 == 0 else "DEBIT"
        transactions.append((account_id, txn_type, round(random.uniform(50, 2500), 2), fake.company(), locations[account_id % 4], (base + timedelta(minutes=number * 45)).strftime("%Y-%m-%d %H:%M:%S")))
    cursor.executemany("INSERT INTO transactions (account_id, txn_type, amount, merchant, location, txn_time) VALUES (?, ?, ?, ?, ?, ?)", transactions)
    connection.commit()
    # Inject anomaly examples after normal history.
    for account_id, amount, location in ((1, 25000, "London"), (2, 18000, "Dubai"), (3, 30000, "Singapore")):
        cursor.execute("INSERT INTO transactions (account_id, txn_type, amount, merchant, location) VALUES (?, ?, ?, ?, ?)", (account_id, "DEBIT", amount, "Injected anomaly", location))
    connection.commit(); connection.close()
    processed_path = ROOT / "data" / "processed.csv"
    if processed_path.exists():
        processed = pd.read_csv(processed_path)
        processed = processed.sample(n=min(150, len(processed)), random_state=42)
    else:
        # This keeps the project demonstrable from a clean clone. The real CFPB
        # pipeline can replace these samples with `ml/prepare_data.py` later.
        samples = [
            "There is an unauthorized card transaction on my account and I need it investigated immediately.",
            "My bank account transfer is pending and I cannot access my money through the mobile application.",
            "My credit card was charged twice for the same purchase and customer service has not helped.",
            "The loan payment calculation and interest rate on my statement appear to be incorrect.",
            "My credit report contains an account that does not belong to me and needs correction.",
        ]
        processed = pd.DataFrame({"text": (samples * 30)[:150]})
    from app.db import execute, query_one
    from app.services.nlp_service import predict
    with app.app_context():
        for index, row in enumerate(processed.itertuples(index=False), start=1):
            account_id = (index - 1) % len(accounts) + 1
            txn_id = (index - 1) % 5000 + 1
            amount = query_one("SELECT amount FROM transactions WHERE txn_id=?", (txn_id,))["amount"]
            result = predict(row.text, amount)
            category = query_one("SELECT category_id FROM complaint_categories WHERE name=?", (result["category"],))["category_id"]
            status = "IN_REVIEW" if result["confidence"] < 0.45 else "OPEN"
            execute("INSERT INTO complaints (customer_id, account_id, txn_id, complaint_text, status, category_id, confidence, sentiment_score, sentiment_label, urgency, model_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (accounts[account_id - 1][0], account_id, txn_id, row.text[:1000], status, category, result["confidence"], result["sentiment_score"], result["sentiment_label"], result["urgency"], result["model_id"]))
    print("Seeded 200 customers, 300 accounts, 5,003 transactions, and 150 complaints.")
    if not processed_path.exists():
        print("Used built-in demonstration complaint samples (no CFPB dataset/model found).")
    print("Demo credentials only: admin/admin123 and agent/agent123")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--reset", action="store_true")
    seed(parser.parse_args().reset)
