"""Application configuration."""

from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent


class Config:
    """Default Flask configuration."""

    SECRET_KEY = "development-only-change-me"
    DATABASE = ROOT_DIR / "data" / "complaints.db"
    MODEL_PATH = ROOT_DIR / "ml" / "models" / "complaint_clf.joblib"
    TESTING = False
