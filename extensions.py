"""Shared extension instances.

Kept in their own module so models and blueprints can import them
without creating a circular import with app.py.
"""

from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Pehle sign in karein."
login_manager.login_message_category = "info"
