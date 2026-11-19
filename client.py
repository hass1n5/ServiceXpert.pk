from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from extensions import db
from models import Booking, Service
from security import validate_csrf

bp = Blueprint("client", __name__, url_prefix="/my")


@bp.before_request
@login_required
def guard():
    if current_user.is_admin:
        return redirect(url_for("admin.dashboard"))
    return None


@bp.get("/")
def dashboard():
    bookings = db.session.scalars(
        db.select(Booking)
        .where(Booking.user_id == current_user.id)
        .order_by(Booking.created_at.desc())
    ).all()

    counts = {
        "total": len(bookings),
        "open": sum(1 for b in bookings if b.status in ("new", "contacted", "scheduled")),
        "done": sum(1 for b in bookings if b.status == "completed"),
    }

    services = db.session.scalars(
        db.select(Service).where(Service.is_active.is_(True)).order_by(Service.name)
    ).all()

    return render_template(
        "client/dashboard.html",
        page_title="Meri bookings",
        bookings=bookings,
        counts=counts,
        services=services,
    )


@bp.route("/profile", methods=["GET", "POST"])
def profile():
    if request.method == "POST":
        if not validate_csrf():
            flash("Form expire ho gaya. Dobara koshish karein.", "error")
            return redirect(url_for("client.profile"))

        name = (request.form.get("name") or "").strip()
        phone = (request.form.get("phone") or "").strip()

        if not name or not phone:
            flash("Naam aur phone khali nahi ho sakte.", "error")
            return redirect(url_for("client.profile"))

        current_user.name = name[:90]
        current_user.phone = phone[:30]
        current_user.city = (request.form.get("city") or "").strip()[:80]
        current_user.address = (request.form.get("address") or "").strip()[:255]

        new_password = request.form.get("new_password") or ""
        if new_password:
            if not current_user.check_password(request.form.get("current_password") or ""):
                flash("Mojooda password ghalat hai.", "error")
                return redirect(url_for("client.profile"))
            if len(new_password) < 8:
                flash("Naya password kam az kam 8 characters ka ho.", "error")
                return redirect(url_for("client.profile"))
            current_user.set_password(new_password)

        db.session.commit()
        flash("Profile update ho gayi.", "info")
        return redirect(url_for("client.profile"))

    return render_template("client/profile.html", page_title="Profile")
