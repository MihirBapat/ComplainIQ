"""Prepare a balanced labelled dataset from the CFPB complaint export."""

import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "complaints.csv"
OUTPUT_PATH = ROOT / "data" / "processed.csv"
LABELS = (
    "Fraud / Unauthorized Transaction", "Credit Card Issue", "Loan / Mortgage Issue",
    "Bank Account / Service Issue", "Credit Reporting / Other",
)
FRAUD_PATTERN = re.compile(r"fraud|unauthorized|scam|stolen|identity theft|did not authorize|not my transaction", re.I)


def clean_text(text):
    """Apply the shared lightweight cleaning policy to complaint text."""
    text = "" if pd.isna(text) else str(text).lower()
    text = re.sub(r"xxxx|\{\$.*?\}", " ", text, flags=re.I)
    text = re.sub(r"\d+|[^a-z\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def map_label(product, issue, sub_issue, text):
    """Map CFPB fields to one of the fixed application categories."""
    combined = " ".join(str(value or "") for value in (issue, sub_issue, text))
    if FRAUD_PATTERN.search(combined):
        return LABELS[0]
    product = str(product or "").lower()
    if "credit card" in product:
        return LABELS[1]
    if "mortgage" in product or "loan" in product:
        return LABELS[2]
    if "bank account" in product or "checking" in product or "savings" in product:
        return LABELS[3]
    return LABELS[4]


def narrative_column(columns):
    """Return a narrative column name when present in this export."""
    return next((column for column in columns if "narrative" in column.lower()), None)


def prepare_data():
    """Create a balanced processed CSV, capped at 3,000 rows per class."""
    if not RAW_PATH.exists():
        raise FileNotFoundError(f"Required CFPB CSV is missing: {RAW_PATH}")
    header = pd.read_csv(RAW_PATH, nrows=0).columns.tolist()
    narrative = narrative_column(header)
    required = {"Product", "Issue", "Sub-issue"}
    missing = required.difference(header)
    if missing:
        raise ValueError(f"CFPB export lacks required columns: {sorted(missing)}")
    usecols = ["Product", "Issue", "Sub-issue"] + ([narrative] if narrative else [])
    buckets = {label: [] for label in LABELS}
    for chunk in pd.read_csv(RAW_PATH, usecols=usecols, chunksize=100_000, low_memory=False):
        for row in chunk.itertuples(index=False, name=None):
            values = dict(zip(usecols, row))
            source_text = values.get(narrative, "") if narrative else " ".join(
                str(values.get(column, "")) for column in ("Product", "Issue", "Sub-issue")
            )
            text = clean_text(source_text)
            if not text:
                continue
            label = map_label(values["Product"], values["Issue"], values["Sub-issue"], text)
            if len(buckets[label]) < 3000:
                buckets[label].append({"text": text, "label": label})
        if all(len(rows) >= 3000 for rows in buckets.values()):
            break
    processed = pd.DataFrame([item for rows in buckets.values() for item in rows])
    if processed.empty or processed["label"].nunique() < len(LABELS):
        raise ValueError("The export did not provide enough rows for all fixed labels.")
    processed.to_csv(OUTPUT_PATH, index=False)
    print("Narrative column:", narrative or "NONE (using Product/Issue/Sub-issue metadata)")
    print(processed["label"].value_counts().sort_index().to_string())
    print(f"Saved {len(processed)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    prepare_data()
