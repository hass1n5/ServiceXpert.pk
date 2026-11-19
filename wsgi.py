import os
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("FLASK_ENV", "production")

from app import create_app
from extensions import db

app = create_app()

# Auto-seed database if empty (ensures services, categories, users exist on fresh deploys)
with app.app_context():
    try:
        from models import User
        db.create_all()
        if not db.session.scalar(db.select(db.func.count(User.id))):
            from seed import seed
            seed(reset=False)
    except Exception as e:
        app.logger.warning(f"Database initialization warning: {e}")

# Expose both app and application for WSGI compatibility
application = app

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
