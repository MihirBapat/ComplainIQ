"""Train and evaluate the complaint classifier."""

import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, ConfusionMatrixDisplay
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from prepare_data import LABELS


ROOT = Path(__file__).resolve().parents[1]


def train():
    """Fit the configured pipeline, save artifacts, and record its version."""
    data = pd.read_csv(ROOT / "data" / "processed.csv")
    x_train, x_test, y_train, y_test = train_test_split(
        data["text"], data["label"], test_size=0.2, random_state=42, stratify=data["label"]
    )
    model = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=5, max_df=0.9, stop_words="english")),
        ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced")),
    ])
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)
    accuracy = accuracy_score(y_test, predictions)
    macro_f1 = f1_score(y_test, predictions, average="macro")
    report = classification_report(y_test, predictions, labels=list(LABELS), output_dict=True, zero_division=0)
    models_dir = ROOT / "ml" / "models"
    models_dir.mkdir(exist_ok=True)
    joblib.dump(model, models_dir / "complaint_clf.joblib")
    metrics = {"accuracy": accuracy, "macro_f1": macro_f1, "per_class": report}
    (models_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    figure, axis = plt.subplots(figsize=(10, 8))
    ConfusionMatrixDisplay(confusion_matrix(y_test, predictions, labels=list(LABELS)), display_labels=LABELS).plot(ax=axis, xticks_rotation=45)
    figure.tight_layout(); figure.savefig(ROOT / "docs" / "confusion_matrix.png", dpi=160); plt.close(figure)
    vectorizer, classifier = model.named_steps["tfidf"], model.named_steps["classifier"]
    terms = vectorizer.get_feature_names_out()
    lines = ["# Top TF-IDF terms by class", ""]
    for label, weights in zip(classifier.classes_, classifier.coef_):
        top = terms[weights.argsort()[-10:][::-1]]
        lines.extend((f"## {label}", "", ", ".join(top), ""))
    (ROOT / "docs" / "top_terms.md").write_text("\n".join(lines), encoding="utf-8")
    from app import create_app
    from app.db import init_db
    app = create_app(); init_db(app)
    import sqlite3
    connection = sqlite3.connect(app.config["DATABASE"])
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("INSERT INTO model_versions (name, accuracy, macro_f1) VALUES (?, ?, ?)", ("TF-IDF + Logistic Regression", accuracy, macro_f1))
    connection.commit(); connection.close()
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Macro-F1: {macro_f1:.4f}")


if __name__ == "__main__":
    train()
