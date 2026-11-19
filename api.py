"""JSON API used by the admin panel for inline edits and deletions."""

from flask import Blueprint, jsonify, request
from flask_login import current_user

from extensions import db
from messaging import booking_message, whatsapp_url
from models import BOOKING_STATUSES, Booking, Category, Service, Setting, Testimonial, User
from security import admin_required, csrf_protect, delete_image

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.before_request
@admin_required
def guard():
    return None


class Invalid(Exception):
    pass


@bp.errorhandler(Invalid)
def on_invalid(err):
    return jsonify(error=str(err)), 422


def body():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise Invalid("Request body JSON hona chahiye.")
    return data


def get_or_fail(model, pk, label):
    obj = db.session.get(model, pk)
    if obj is None:
        raise Invalid(f"{label} nahi mila.")
    return obj


def to_int(raw, label, minimum=0, maximum=100_000_000):
    if raw in (None, ""):
        return None
    try:
        value = int(raw)
    except (TypeError, ValueError):
        raise Invalid(f"{label} ek number hona chahiye.")
    if value < minimum or value > maximum:
        raise Invalid(f"{label} {minimum}–{maximum} ke darmiyan hona chahiye.")
    return value


# -------------------------------------------------------------- bookings


@bp.get("/bookings/<int:booking_id>")
def get_booking(booking_id):
    booking = get_or_fail(Booking, booking_id, "Booking")
    return jsonify(booking=booking.to_dict())


@bp.patch("/bookings/<int:booking_id>")
@csrf_protect
def update_booking(booking_id):
    booking = get_or_fail(Booking, booking_id, "Booking")
    data = body()

    if "status" in data:
        status = (data.get("status") or "").strip().lower()
        if status not in BOOKING_STATUSES:
            raise Invalid("Yeh status valid nahi hai.")
        booking.status = status

    if "admin_note" in data:
        booking.admin_note = (data.get("admin_note") or "").strip()[:1500]

    if "quoted_price" in data:
        booking.quoted_price = to_int(data.get("quoted_price"), "Quoted price")

    db.session.commit()
    return jsonify(booking=booking.to_dict(), message="Booking update ho gayi.")


@bp.get("/bookings/<int:booking_id>/whatsapp")
def booking_whatsapp(booking_id):
    """Link to message *the customer* about their booking."""
    booking = get_or_fail(Booking, booking_id, "Booking")
    brand = Setting.get("brand_name", "Sparkle Care")

    text = (
        f"Assalam o Alaikum {booking.name},\n\n"
        f"{brand} ki taraf se raabta. Aapki request {booking.reference} "
        f"({booking.service_name}) hamein mil gayi hai."
    )
    if booking.quoted_price:
        text += f"\nHamara quote: Rs {booking.quoted_price:,}"
    text += "\n\nKya waqt aapke liye munasib rahega?"

    link = whatsapp_url(booking.phone, text)
    if not link:
        raise Invalid("Is booking par valid phone number nahi hai.")
    return jsonify(url=link)


@bp.get("/bookings/<int:booking_id>/forward")
def forward_booking(booking_id):
    """Link to forward the enquiry to the business WhatsApp number."""
    booking = get_or_fail(Booking, booking_id, "Booking")
    brand = Setting.get("brand_name", "Sparkle Care")
    link = whatsapp_url(Setting.get("whatsapp_number", ""), booking_message(booking, brand))
    if not link:
        raise Invalid("Settings mein WhatsApp number set karein.")
    return jsonify(url=link)


@bp.delete("/bookings/<int:booking_id>")
@csrf_protect
def delete_booking(booking_id):
    booking = get_or_fail(Booking, booking_id, "Booking")
    db.session.delete(booking)
    db.session.commit()
    return jsonify(message="Booking delete ho gayi.")


# -------------------------------------------------------------- services


@bp.patch("/services/<int:service_id>")
@csrf_protect
def toggle_service(service_id):
    service = get_or_fail(Service, service_id, "Service")
    data = body()

    if "is_active" in data:
        service.is_active = bool(data["is_active"])
    if "is_featured" in data:
        service.is_featured = bool(data["is_featured"])

    db.session.commit()
    return jsonify(service=service.to_dict(), message="Service update ho gayi.")


@bp.delete("/services/<int:service_id>")
@csrf_protect
def delete_service(service_id):
    service = get_or_fail(Service, service_id, "Service")
    if service.bookings:
        raise Invalid(
            "Is service par bookings maujood hain. Delete ke bajaye ise off kar dein."
        )
    delete_image(service.image)
    db.session.delete(service)
    db.session.commit()
    return jsonify(message="Service delete ho gayi.")


@bp.delete("/categories/<int:category_id>")
@csrf_protect
def delete_category(category_id):
    category = get_or_fail(Category, category_id, "Category")
    if category.services:
        raise Invalid("Pehle is category ki services hatayein ya move karein.")
    db.session.delete(category)
    db.session.commit()
    return jsonify(message="Category delete ho gayi.")


# --------------------------------------------------------- clients / team


@bp.patch("/users/<int:user_id>")
@csrf_protect
def update_user(user_id):
    user = get_or_fail(User, user_id, "User")
    data = body()

    if "active" in data:
        if user.id == current_user.id and not data["active"]:
            raise Invalid("Apna hi account band nahi kar sakte.")
        user.is_active_user = bool(data["active"])

    if "role" in data:
        role = (data.get("role") or "").lower()
        if role not in ("admin", "client"):
            raise Invalid("Role sirf admin ya client ho sakta hai.")
        if user.id == current_user.id and role != "admin":
            raise Invalid("Apna hi admin access nahi hata sakte.")
        user.role = role

    db.session.commit()
    return jsonify(user=user.to_dict(), message="User update ho gaya.")


@bp.post("/users")
@csrf_protect
def create_user():
    data = body()

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    role = (data.get("role") or "admin").lower()

    if not name:
        raise Invalid("Naam zaroori hai.")
    if "@" not in email or "." not in email.split("@")[-1]:
        raise Invalid("Email sahi nahi lag rahi.")
    if len(password) < 8:
        raise Invalid("Password kam az kam 8 characters ka hona chahiye.")
    if role not in ("admin", "client"):
        raise Invalid("Role sirf admin ya client ho sakta hai.")
    if db.session.scalar(db.select(User).filter_by(email=email)):
        raise Invalid("Is email ka account pehle se hai.")

    user = User(
        name=name[:90],
        email=email,
        phone=(data.get("phone") or "").strip()[:30],
        role=role,
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify(user=user.to_dict(), message="Account ban gaya."), 201


@bp.delete("/users/<int:user_id>")
@csrf_protect
def delete_user(user_id):
    user = get_or_fail(User, user_id, "User")
    if user.id == current_user.id:
        raise Invalid("Apna hi account delete nahi kar sakte.")
    for booking in user.bookings:
        booking.user_id = None
    db.session.delete(user)
    db.session.commit()
    return jsonify(message="Account delete ho gaya.")


# ------------------------------------------------------------- reviews


@bp.patch("/reviews/<int:review_id>")
@csrf_protect
def toggle_review(review_id):
    review = get_or_fail(Testimonial, review_id, "Review")
    data = body()
    if "is_published" in data:
        review.is_published = bool(data["is_published"])
    db.session.commit()
    return jsonify(review=review.to_dict(), message="Review update ho gaya.")


@bp.delete("/reviews/<int:review_id>")
@csrf_protect
def delete_review(review_id):
    review = get_or_fail(Testimonial, review_id, "Review")
    db.session.delete(review)
    db.session.commit()
    return jsonify(message="Review delete ho gaya.")
