# AgroPlan
Crop Rotation Pattern Recognition and Planning using CSP
 # Fraud-Aware Transaction Complaint Analyzer

## Setup
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
Place the CFPB export at `data/raw/complaints.csv`, then run:
```powershell
python ml/prepare_data.py
python ml/train.py
python scripts/seed_db.py --reset
python run.py
```
Open `http://127.0.0.1:5000`. Demo-only staff credentials: `admin/admin123` and `agent/agent123`. Run tests with `python -m pytest -v`.
