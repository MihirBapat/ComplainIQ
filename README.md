# ComplainIQ — Fraud-Aware Transaction Complaint Analyzer

ComplainIQ is a final-year DBMS + AI/NLP project. It stores normalized banking data in SQLite,
classifies free-text complaints, performs sentiment/urgency analysis, and raises explainable
rule-based fraud flags.

## Quick start (works without a dataset)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/seed_db.py --reset
python run.py
```

Open `http://127.0.0.1:5000`.

- Admin: `admin` / `admin123`
- Agent: `agent` / `agent123`

These credentials are demo-only. The seed command creates 200 customers, accounts,
transactions, complaints, and example fraud signals. It also works without the CFPB export by
using clearly labelled built-in demonstration complaints.

## Train with the CFPB data (optional)

Place the CFPB export at `data/raw/complaints.csv`, then run:

```powershell
python ml/prepare_data.py
python ml/train.py
python scripts/seed_db.py --reset
```

The trained TF-IDF + Logistic Regression model is used automatically. Without it, ComplainIQ
uses an explainable keyword fallback so the complaint workflow remains usable for demonstration.

## Verification

```powershell
python -m pytest -v
```

## Demo flow

1. Sign in as admin and open the dashboard to explain the DBMS records and AI analytics.
2. Add/filter transactions; adding an anomalous debit can trigger transparent fraud rules.
3. Open **Submit a complaint** and file an unauthorized-transaction complaint to show category,
   sentiment and urgency classification.
4. Review the created case and the Fraud queue. Use Reports to show SQL-backed summaries.
