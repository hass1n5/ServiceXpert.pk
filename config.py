import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "static" / "uploads"


def _secret_key():
    """Return a stable secret key without hard-coding a production secret.

    DirectAdmin users should set SECRET_KEY in Python App environment variables.
    For development only, a local fallback is used so the app can still start.
    """
    value = os.environ.get("SECRET_KEY")
    if value:
        return value
    return "dev-secret-change-me-in-production"


class Config:
    SECRET_KEY = _secret_key()

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'sparkle.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "0") == "1"

    UPLOAD_FOLDER = str(UPLOAD_DIR)
    MAX_CONTENT_LENGTH = 4 * 1024 * 1024
    # SVG is intentionally excluded: user-uploaded SVG can contain active content.
    ALLOWED_IMAGE_EXT = {"png", "jpg", "jpeg", "webp", "ico", "gif"}

    PER_PAGE = 12


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True


class DevelopmentConfig(Config):
    DEBUG = True


configs = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    # Safe default for hosted imports such as Passenger. Local development can
    # explicitly set FLASK_ENV=development.
    "default": ProductionConfig,
}
