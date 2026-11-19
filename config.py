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


def _database_uri():
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        return db_url
    if os.environ.get("VERCEL"):
        import shutil
        tmp_db = Path("/tmp/sparkle.db")
        source_db = BASE_DIR / "sparkle.db"
        if not tmp_db.exists() and source_db.exists():
            try:
                shutil.copy2(source_db, tmp_db)
            except Exception:
                pass
        return f"sqlite:///{tmp_db}"
    return f"sqlite:///{BASE_DIR / 'sparkle.db'}"


def _upload_folder():
    if os.environ.get("VERCEL"):
        tmp_upload = Path("/tmp/uploads")
        tmp_upload.mkdir(parents=True, exist_ok=True)
        return str(tmp_upload)
    return str(UPLOAD_DIR)


class Config:
    SECRET_KEY = _secret_key()

    SQLALCHEMY_DATABASE_URI = _database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "0") == "1"

    UPLOAD_FOLDER = _upload_folder()
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
