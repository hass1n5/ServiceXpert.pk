"""DirectAdmin/Passenger WSGI entry point.

Python App settings:
  Startup file: passenger_wsgi.py
  Entry point : application
"""
import os
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

os.environ.setdefault("FLASK_ENV", "production")
os.environ.setdefault("SESSION_COOKIE_SECURE", "1")

from app import app as application  # noqa: E402
