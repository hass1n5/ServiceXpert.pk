"""One-time production bootstrap for ServiceXpert.

Run from the application's virtualenv after setting ADMIN_EMAIL and
ADMIN_PASSWORD. Safe to run more than once: existing rows are not duplicated.
"""
import os
import secrets

from app import DEFAULT_SETTINGS, create_app
from extensions import db
from models import Category, Service, Setting, Testimonial, User, slugify
from seed import CLEANING, PEST, REVIEWS


def require_env(name):
    value = (os.environ.get(name) or "").strip()
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def setup():
    os.environ.setdefault("FLASK_ENV", "production")
    app = create_app("production")
    with app.app_context():
        db.create_all()

        # Site settings
        for key, value in DEFAULT_SETTINGS.items():
            if db.session.get(Setting, key) is None:
                Setting.put(key, value)

        # Categories
        category_specs = [
            ("Deep Cleaning Services", "deep-cleaning-services",
             "Ghar, office aur commercial jagahon ki mukammal safai",
             "Trained staff, professional machinery aur eco-friendly chemicals ke sath har qism ki deep cleaning.",
             "green", 1, CLEANING),
            ("Pest Control Services", "pest-control-services",
             "Keeray, deemak aur machharon ka mehfooz aur mukammal khatma",
             "Government-approved chemicals aur licensed operators — warranty ke sath fumigation aur pest control.",
             "blue", 2, PEST),
        ]

        for name, slug, tagline, description, accent, order, rows in category_specs:
            category = db.session.scalar(db.select(Category).filter_by(slug=slug))
            if category is None:
                category = Category(name=name, slug=slug, tagline=tagline,
                                    description=description, accent=accent, sort_order=order)
                db.session.add(category)
                db.session.flush()

            for sort_order, row in enumerate(rows, start=1):
                svc_name, summary, description, includes, price, old, duration, icon, featured = row
                svc_slug = slugify(svc_name)
                if db.session.scalar(db.select(Service).filter_by(slug=svc_slug)) is None:
                    db.session.add(Service(
                        category_id=category.id, name=svc_name, slug=svc_slug,
                        summary=summary, description=description, includes=includes,
                        price_from=price, old_price=old, duration=duration, icon=icon,
                        rating=4.8, is_featured=featured, is_active=True,
                        sort_order=sort_order,
                    ))

        # Reviews are seeded only if the review table is empty.
        if not db.session.scalar(db.select(db.func.count(Testimonial.id))):
            for name, city, service_name, rating, text in REVIEWS:
                db.session.add(Testimonial(name=name, city=city, service=service_name,
                                           rating=rating, body=text, is_published=True))

        # Create the initial admin only when there is no admin account yet.
        admin_count = db.session.scalar(
            db.select(db.func.count(User.id)).where(User.role == "admin")
        ) or 0
        if admin_count == 0:
            email = require_env("ADMIN_EMAIL").lower()
            password = require_env("ADMIN_PASSWORD")
            if len(password) < 12:
                raise SystemExit("ADMIN_PASSWORD must be at least 12 characters long.")
            name = (os.environ.get("ADMIN_NAME") or "Site Admin").strip()[:90]
            if db.session.scalar(db.select(User).filter_by(email=email)):
                raise SystemExit("ADMIN_EMAIL already belongs to a non-admin account.")
            admin = User(name=name, email=email, role="admin")
            admin.set_password(password)
            db.session.add(admin)

        db.session.commit()
        print("Production database ready.")
        print("Admin login: /admin/login")


if __name__ == "__main__":
    setup()
