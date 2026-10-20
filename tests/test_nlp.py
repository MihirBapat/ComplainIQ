"""NLP preprocessing, inference, sentiment, and urgency tests."""

from app import create_app
from app.db import init_db
from app.services.nlp_service import predict, sentiment, urgency_for
from ml.prepare_data import clean_text


def test_clean_text_removes_masks_digits_and_punctuation():
    assert clean_text("XXXX {$abc} Charge #123!") == "charge"


def test_sentiment_thresholds():
    assert sentiment("I hate this terrible service")[1] == "NEGATIVE"
    assert sentiment("This is okay.")[1] == "POSITIVE"


def test_urgency_heuristic():
    assert urgency_for("Fraud / Unauthorized Transaction", -0.7, "My stolen card was drained immediately", 11000) == "HIGH"
    assert urgency_for("Credit Card Issue", 0, "ordinary question") == "LOW"


def test_predict_returns_persistence_fields(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": tmp_path / "nlp.db"})
    init_db(app)
    with app.app_context():
        result = predict("This unauthorized fraud transaction has drained my account immediately.", 12000)
    assert {"category", "confidence", "sentiment_score", "sentiment_label", "urgency", "model_id"} <= result.keys()
    assert result["urgency"] in {"LOW", "MEDIUM", "HIGH"}
