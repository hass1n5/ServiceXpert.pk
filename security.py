"""CSRF tokens, role guards and safe image uploads."""

import hmac
import os
import secrets
import uuid
from functools import wraps

from flask import abort, current_app, jsonify, request, session
from flask_login import current_user
from werkzeug.utils import secure_filename

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


def get_csrf_token():
    token = session.get("_csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["_csrf_token"] = token
    return token


def validate_csrf():
    if request.method in SAFE_METHODS:
        return True
    sent = request.headers.get("X-CSRF-Token") or request.form.get("csrf_token", "")
    expected = session.get("_csrf_token", "")
    return bool(expected) and hmac.compare_digest(sent, expected)


def csrf_protect(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not validate_csrf():
            return jsonify(error="Session expire ho gaya. Page refresh karein."), 400
        return view(*args, **kwargs)

    return wrapper


def admin_required(view):
    """Admin-only. Returns JSON for /api/ paths, an error page otherwise."""

    @wraps(view)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            if request.path.startswith("/api/"):
                return jsonify(error="Pehle sign in karein."), 401
            abort(401)
        if not current_user.is_admin:
            if request.path.startswith("/api/"):
                return jsonify(error="Sirf admin yeh kaam kar sakta hai."), 403
            abort(403)
        return view(*args, **kwargs)

    return wrapper


def save_image(file_storage, prefix="img"):
    """Validate and store an uploaded image. Returns the stored filename."""
    if not file_storage or not file_storage.filename:
        return None

    name = secure_filename(file_storage.filename)
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""

    if ext not in current_app.config["ALLOWED_IMAGE_EXT"]:
        allowed = ", ".join(sorted(current_app.config["ALLOWED_IMAGE_EXT"]))
        raise ValueError(f"Sirf yeh formats chalte hain: {allowed}")

    folder = current_app.config["UPLOAD_FOLDER"]
    os.makedirs(folder, exist_ok=True)

    stored = f"{prefix}-{uuid.uuid4().hex[:10]}.{ext}"
    file_storage.save(os.path.join(folder, stored))
    return stored


def delete_image(filename):
    if not filename:
        return
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    if os.path.isfile(path):
        try:
            os.remove(path)
        except OSError:
            pass
