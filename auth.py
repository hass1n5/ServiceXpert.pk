from datetime import timedelta

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user

from extensions import db
from models import User, utcnow
from security import validate_csrf

bp = Blueprint("auth", __name__)

MAX_ATTEMPTS = 6


def _safe_next(default):
    nxt = request.args.get("next", "")
    if nxt.startswith("/") and not nxt.startswith("//"):
        return nxt
    return default


def _home_for(user):
    return url_for("admin.dashboard") if user.is_admin else url_for("client.dashboard")


# ------------------------------------------------------------- client side


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(_home_for(current_user))

    if request.method == "POST":
        user, error = _authenticate()
        if error:
            flash(error, "error")
            return render_template("auth/login.html", email=request.form.get("email", "")), 401
        _finish_login(user)
        return redirect(_safe_next(_home_for(user)))

    return render_template("auth/login.html")


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(_home_for(current_user))

    if request.method == "POST":
        if not validate_csrf():
            flash("Your session has expired. Please try again.", "error")
            return redirect(url_for("auth.register"))

        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        phone = (request.form.get("phone") or "").strip()
        city = (request.form.get("city") or "").strip()
        password = request.form.get("password") or ""

        form = {"name": name, "email": email, "phone": phone, "city": city}

        if not name or not email or not phone:
            flash("Name, email, and phone are required.", "error")
            return render_template("auth/register.html", form=form), 422

        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "error")
            return render_template("auth/register.html", form=form), 422

        if db.session.scalar(db.select(User).filter_by(email=email)):
            flash("An account with this email already exists. Please sign in.", "error")
            return render_template("auth/register.html", form=form), 409

        user = User(name=name, email=email, phone=phone, city=city, role="client")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        login_user(user, duration=timedelta(days=14))
        flash(f"Welcome, {name.split()[0]}!", "info")
        return redirect(url_for("client.dashboard"))

    return render_template("auth/register.html", form={})


# -------------------------------------------------------------- admin side


@bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if current_user.is_authenticated and current_user.is_admin:
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        user, error = _authenticate()
        if error:
            flash(error, "error")
            return render_template("auth/admin_login.html"), 401
        if not user.is_admin:
            flash("This is not an administrator account.", "error")
            return render_template("auth/admin_login.html"), 403
        _finish_login(user)
        return redirect(_safe_next(url_for("admin.dashboard")))

    return render_template("auth/admin_login.html")


# ------------------------------------------------------------------ shared


def _authenticate():
    if not validate_csrf():
        return None, "Your session has expired. Please try again."

    if session.get("login_attempts", 0) >= MAX_ATTEMPTS:
        return None, "Too many failed attempts. Please try again later."

    email = (request.form.get("email") or "").strip().lower()
    password = request.form.get("password") or ""

    user = db.session.scalar(db.select(User).filter_by(email=email))
    if user is None or not user.check_password(password):
        session["login_attempts"] = session.get("login_attempts", 0) + 1
        return None, "Incorrect email or password."

    if not user.is_active_user:
        return None, "This account has been disabled."

    return user, None


def _finish_login(user):
    session.pop("login_attempts", None)
    login_user(
        user, remember=request.form.get("remember") == "on", duration=timedelta(days=14)
    )
    user.last_login_at = utcnow()
    db.session.commit()


@bp.post("/logout")
@login_required
def logout():
    if validate_csrf():
        was_admin = current_user.is_admin
        logout_user()
        session.clear()
        flash("Aap sign out ho gaye.", "info")
        if was_admin:
            return redirect(url_for("auth.admin_login"))
    return redirect(url_for("public.home"))
