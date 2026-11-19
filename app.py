"""Sparkle Care — cleaning & pest control website with client + admin areas.

Quick start:
    pip install -r requirements.txt
    python seed.py --reset
    python app.py        ->  http://127.0.0.1:5000
"""

import os

from flask import Flask, jsonify, render_template, request, url_for

import theming
from config import configs
from extensions import db, login_manager
from security import get_csrf_token

DEFAULT_SETTINGS = {
    "brand_name": "ServiceXpert.pk",
    "tagline": "Professional Property Services",
    "whatsapp_number": "03001234567",
    "phone": "0300-1234567",
    "phone_alt": "042-35000000",
    "email": "info@servicexpert.pk",
    "address": "12-A Gulberg III, Main Boulevard",
    "city": "Lahore",
    "hours": "Roz subah 8 se raat 9 baje tak",
    "facebook": "",
    "instagram": "",
    "hero_title": "Professional Home & Business Services You Can Trust",
    "hero_subtitle": (
        "Reliable, professional, and convenient services for your home, office, and business. "
        "From deep cleaning and pest control to specialized property care, ServiceXpert helps you keep your space clean, healthy, safe, and well maintained."
    ),
    "about_body": "",
    "map_embed": "",
    "logo": "",
    "favicon": "",
    "hero_image": "",

    # Appearance — see theming.py for the full catalogue.
    "theme": theming.DEFAULT_THEME,
    "font_heading": theming.DEFAULT_HEADING_FONT,
    "font_body": theming.DEFAULT_BODY_FONT,

    # Numbers shown in the strip under the hero. These count up on scroll.
    "stat_rating": "4.8",
    "stat_jobs": "8800",
    "stat_staff": "120",
    "stat_warranty": "30–60 din",

    # WhatsApp chat widget.
    "chat_enabled": "1",
    "chat_agent": "ServiceXpert AI",
    "chat_role": "AI Service Assistant",
    "chat_reply_time": "Aam tor par 5 minute mein jawab",
    "chat_greeting": (
        "Hello! I'm ServiceXpert AI. Tell me what service you need and I'll help you find the right option, estimated starting price, and booking next step."
    ),
    "chat_away": "Abhi auqat-e-kaar ke baad hain — message chhor dein, subah raabta hoga.",
}


def create_app(config_name=None):
    app = Flask(__name__)
    app.config.from_object(configs.get(config_name or os.environ.get("FLASK_ENV", "default"),
                                       configs["default"]))

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Pehle sign in karein."
    login_manager.login_message_category = "info"

    import admin as admin_bp
    import api as api_bp
    import auth as auth_bp
    import client as client_bp
    import public_site

    app.register_blueprint(public_site.bp)
    app.register_blueprint(auth_bp.bp)
    app.register_blueprint(client_bp.bp)
    app.register_blueprint(admin_bp.bp)
    app.register_blueprint(api_bp.bp)

    register_helpers(app)
    register_errors(app)
    register_cli(app)

    with app.app_context():
        try:
            db.create_all()
            from models import Category
            if not db.session.scalar(db.select(db.func.count(Category.id))):
                import seed
                seed.seed(reset=False, app=app)
        except Exception as e:
            app.logger.warning(f"Database setup warning: {e}")

    @app.get("/healthz")
    def healthz():
        return jsonify(status="ok"), 200

    return app


def register_helpers(app):
    from flask_login import current_user
    from sqlalchemy import func

    from models import Booking, Category, Setting

    @app.context_processor
    def inject_globals():
        site = dict(DEFAULT_SETTINGS)
        new_bookings = 0
        try:
            saved = Setting.all_as_dict()
            site.update({k: v for k, v in saved.items() if v not in (None, "")})
            if current_user.is_authenticated and current_user.is_admin:
                new_bookings = db.session.scalar(
                    db.select(func.count(Booking.id)).where(Booking.status == "new")
                ) or 0
        except Exception:  # database not created yet
            pass

        def upload_url(filename):
            return url_for("static", filename=f"uploads/{filename}") if filename else ""

        bot_catalog = []
        try:
            cats = (
                Category.query.order_by(Category.sort_order)
                .all()
            )
            for cat in cats:
                for svc in cat.active_services:
                    bot_catalog.append({
                        "id": svc.id,
                        "name": svc.name,
                        "slug": svc.slug,
                        "category": cat.name,
                        "category_slug": cat.slug,
                        "summary": svc.summary or "",
                        "price_from": svc.price_from or 0,
                        "old_price": svc.old_price or 0,
                        "duration": svc.duration or "",
                        "url": url_for("public.service_detail", slug=svc.slug),
                    })
        except Exception:  # database not created yet
            pass

        return {
            "csrf_token": get_csrf_token(),
            "site": site,
            "upload_url": upload_url,
            "new_bookings": new_bookings,
            "bot_catalog": bot_catalog,
            "appearance_css": theming.appearance_css(
                site.get("theme"), site.get("font_heading"), site.get("font_body")
            ),
            "admin_appearance_css": theming.admin_appearance_css(
                site.get("theme"), site.get("font_heading"), site.get("font_body")
            ),
            "font_links": theming.font_links(
                site.get("font_heading"), site.get("font_body")
            ),
            "themes": theming.THEMES,
            "active_theme": theming.get_theme(site.get("theme")),
            "font_groups": theming.font_groups(),
        }

    @app.template_filter("money")
    def money(value):
        try:
            return f"Rs {int(value):,}"
        except (TypeError, ValueError):
            return "Rs 0"

    @app.template_filter("shortdate")
    def shortdate(value):
        return value.strftime("%d %b %Y") if value else "—"

    @app.template_filter("datetime")
    def datetime_filter(value):
        return value.strftime("%d %b %Y, %I:%M %p") if value else "—"

    @app.template_filter("wadigits")
    def wadigits(value):
        from messaging import normalise_number

        return normalise_number(value)


def register_errors(app):
    def wants_json():
        return request.path.startswith("/api/")

    @app.errorhandler(401)
    def unauthorised(_):
        if wants_json():
            return jsonify(error="Pehle sign in karein."), 401
        return render_template("error.html", code=401,
                               message="Yeh page dekhne ke liye sign in karein."), 401

    @app.errorhandler(403)
    def forbidden(_):
        if wants_json():
            return jsonify(error="Is page ka access nahi hai."), 403
        return render_template("error.html", code=403,
                               message="Is page ka access aapke paas nahi hai."), 403

    @app.errorhandler(404)
    def not_found(_):
        if wants_json():
            return jsonify(error="Yeh resource nahi mila."), 404
        return render_template("error.html", code=404,
                               message="Yeh page maujood nahi hai."), 404

    @app.errorhandler(413)
    def too_large(_):
        if wants_json():
            return jsonify(error="File bohat bari hai (4 MB tak allowed)."), 413
        return render_template("error.html", code=413,
                               message="File bohat bari hai. 4 MB tak allowed hai."), 413

    @app.errorhandler(500)
    def server_error(_):
        db.session.rollback()
        if wants_json():
            return jsonify(error="Server par kuch ghalat ho gaya."), 500
        return render_template("error.html", code=500,
                               message="Server par kuch ghalat ho gaya."), 500


def register_cli(app):
    @app.cli.command("init-db")
    def init_db():
        """Create all tables."""
        db.create_all()
        print("Tables ban gaye.")

    @app.cli.command("create-admin")
    def create_admin():
        """Create an admin account interactively."""
        from getpass import getpass

        from models import User

        name = input("Name: ").strip()
        email = input("Email: ").strip().lower()
        password = getpass("Password: ")

        if db.session.scalar(db.select(User).filter_by(email=email)):
            print("Yeh email pehle se registered hai.")
            return

        user = User(name=name, email=email, role="admin")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print(f"Admin bana diya: {email}")


app = create_app()


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="127.0.0.1", port=5000, debug=app.config.get("DEBUG", False))
