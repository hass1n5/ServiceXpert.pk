"""Database models.

Money is stored as whole rupees (Integer) so totals never drift.
"""

import re
from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db, login_manager

BOOKING_STATUSES = ("new", "contacted", "scheduled", "completed", "cancelled")
ROLES = ("admin", "client")


def utcnow():
    return datetime.now(timezone.utc)


def slugify(text):
    text = re.sub(r"[^a-zA-Z0-9\s-]", "", (text or "").lower()).strip()
    text = re.sub(r"[\s_-]+", "-", text)
    return text or "item"


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(90), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(30))
    city = db.Column(db.String(80))
    address = db.Column(db.String(255))
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="client")
    is_active_user = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=utcnow)
    last_login_at = db.Column(db.DateTime)

    bookings = db.relationship("Booking", back_populates="user")

    def set_password(self, raw):
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self.password_hash, raw)

    @property
    def is_admin(self):
        return self.role == "admin"

    @property
    def initials(self):
        parts = [p for p in self.name.split() if p]
        return "".join(p[0].upper() for p in parts[:2]) or "?"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "city": self.city,
            "role": self.role,
            "active": self.is_active_user,
            "bookings": len(self.bookings),
        }


class Category(db.Model):
    """Deep Cleaning / Pest Control — the two top-level service families."""

    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(90), nullable=False)
    slug = db.Column(db.String(90), unique=True, nullable=False, index=True)
    tagline = db.Column(db.String(200))
    description = db.Column(db.Text)
    accent = db.Column(db.String(20), default="green")  # green | blue
    sort_order = db.Column(db.Integer, default=0)

    services = db.relationship(
        "Service",
        back_populates="category",
        cascade="all, delete-orphan",
        order_by="Service.sort_order",
    )

    @property
    def active_services(self):
        return [s for s in self.services if s.is_active]

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "tagline": self.tagline,
            "services": len(self.services),
        }


class Service(db.Model):
    __tablename__ = "services"

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(
        db.Integer, db.ForeignKey("categories.id"), nullable=False, index=True
    )
    name = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(140), unique=True, nullable=False, index=True)
    summary = db.Column(db.String(300))
    description = db.Column(db.Text)
    includes = db.Column(db.Text)  # one bullet per line
    price_from = db.Column(db.Integer, default=0)
    old_price = db.Column(db.Integer)
    duration = db.Column(db.String(60))
    icon = db.Column(db.String(40), default="spray")
    image = db.Column(db.String(255))
    rating = db.Column(db.Float, default=4.8)
    is_featured = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)

    category = db.relationship("Category", back_populates="services")
    bookings = db.relationship("Booking", back_populates="service")

    @property
    def bullet_list(self):
        return [line.strip() for line in (self.includes or "").splitlines() if line.strip()]

    @property
    def discount_percent(self):
        if self.old_price and self.price_from and self.old_price > self.price_from:
            return round((self.old_price - self.price_from) / self.old_price * 100)
        return 0

    def to_dict(self):
        return {
            "id": self.id,
            "category_id": self.category_id,
            "category": self.category.name if self.category else None,
            "name": self.name,
            "slug": self.slug,
            "summary": self.summary,
            "description": self.description,
            "includes": self.includes,
            "price_from": self.price_from,
            "old_price": self.old_price,
            "duration": self.duration,
            "icon": self.icon,
            "image": self.image,
            "is_featured": self.is_featured,
            "is_active": self.is_active,
            "bookings": len(self.bookings),
        }


class Booking(db.Model):
    """A quote request / booking. Created from the public form or by a client."""

    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    reference = db.Column(db.String(20), unique=True, nullable=False, index=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), index=True)
    service_id = db.Column(db.Integer, db.ForeignKey("services.id"), index=True)

    name = db.Column(db.String(90), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(120))
    city = db.Column(db.String(80))
    address = db.Column(db.String(255))
    preferred_date = db.Column(db.String(30))
    message = db.Column(db.Text)

    status = db.Column(db.String(20), nullable=False, default="new", index=True)
    quoted_price = db.Column(db.Integer)
    admin_note = db.Column(db.Text)
    source = db.Column(db.String(30), default="website")
    created_at = db.Column(db.DateTime, default=utcnow, index=True)

    user = db.relationship("User", back_populates="bookings")
    service = db.relationship("Service", back_populates="bookings")

    @property
    def service_name(self):
        return self.service.name if self.service else "General enquiry"

    @property
    def whatsapp_digits(self):
        return re.sub(r"\D", "", self.phone or "")

    def to_dict(self):
        return {
            "id": self.id,
            "reference": self.reference,
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "city": self.city,
            "address": self.address,
            "preferred_date": self.preferred_date,
            "message": self.message,
            "service": self.service_name,
            "service_id": self.service_id,
            "status": self.status,
            "quoted_price": self.quoted_price,
            "admin_note": self.admin_note,
            "created_at": self.created_at.strftime("%d %b %Y, %I:%M %p")
            if self.created_at
            else None,
        }


class Testimonial(db.Model):
    __tablename__ = "testimonials"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(90), nullable=False)
    city = db.Column(db.String(80))
    service = db.Column(db.String(120))
    rating = db.Column(db.Integer, default=5)
    body = db.Column(db.Text, nullable=False)
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "city": self.city,
            "service": self.service,
            "rating": self.rating,
            "body": self.body,
            "is_published": self.is_published,
        }


class Setting(db.Model):
    """Editable site settings — brand name, logo, favicon, contact details."""

    __tablename__ = "settings"

    key = db.Column(db.String(60), primary_key=True)
    value = db.Column(db.Text)

    @staticmethod
    def get(key, default=None):
        row = db.session.get(Setting, key)
        return row.value if row and row.value not in (None, "") else default

    @staticmethod
    def put(key, value):
        row = db.session.get(Setting, key)
        if row:
            row.value = value
        else:
            db.session.add(Setting(key=key, value=value))

    @staticmethod
    def all_as_dict():
        return {row.key: row.value for row in db.session.scalars(db.select(Setting))}


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
