from datetime import datetime, timedelta, timezone

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from sqlalchemy import func

import theming
from extensions import db
from models import (
    BOOKING_STATUSES,
    Booking,
    Category,
    Service,
    Setting,
    Testimonial,
    User,
    slugify,
)
from security import admin_required, delete_image, save_image, validate_csrf

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.before_request
@admin_required
def guard():
    return None


def _page():
    try:
        return max(1, int(request.args.get("page", 1)))
    except (TypeError, ValueError):
        return 1


def _form_ok(redirect_to):
    if validate_csrf():
        return None
    flash("Form expire ho gaya. Dobara koshish karein.", "error")
    return redirect(redirect_to)


def _int_or_none(raw):
    try:
        value = int(raw)
        return value if value >= 0 else None
    except (TypeError, ValueError):
        return None


# ------------------------------------------------------------- dashboard


@bp.get("/")
def dashboard():
    now = datetime.now(timezone.utc)
    month_start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
    week_start = now - timedelta(days=7)

    total = db.session.scalar(db.select(func.count(Booking.id))) or 0
    new_count = db.session.scalar(
        db.select(func.count(Booking.id)).where(Booking.status == "new")
    ) or 0
    this_week = db.session.scalar(
        db.select(func.count(Booking.id)).where(Booking.created_at >= week_start)
    ) or 0
    completed = db.session.scalar(
        db.select(func.count(Booking.id)).where(Booking.status == "completed")
    ) or 0
    clients = db.session.scalar(
        db.select(func.count(User.id)).where(User.role == "client")
    ) or 0
    revenue = db.session.scalar(
        db.select(func.coalesce(func.sum(Booking.quoted_price), 0)).where(
            Booking.status == "completed", Booking.created_at >= month_start
        )
    ) or 0

    status_rows = db.session.execute(
        db.select(Booking.status, func.count(Booking.id)).group_by(Booking.status)
    ).all()

    top_rows = db.session.execute(
        db.select(Service.name, func.count(Booking.id).label("n"))
        .join(Booking, Booking.service_id == Service.id)
        .group_by(Service.id)
        .order_by(func.count(Booking.id).desc())
        .limit(6)
    ).all()

    # Bookings per day for the last 14 days.
    days, counts = [], []
    for offset in range(13, -1, -1):
        day = (now - timedelta(days=offset)).date()
        days.append(day.strftime("%d %b"))
        counts.append(
            db.session.scalar(
                db.select(func.count(Booking.id)).where(
                    func.date(Booking.created_at) == day.isoformat()
                )
            )
            or 0
        )

    recent = db.session.scalars(
        db.select(Booking).order_by(Booking.created_at.desc()).limit(8)
    ).all()

    return render_template(
        "admin/dashboard.html",
        page_title="Overview",
        stats={
            "total": total,
            "new": new_count,
            "week": this_week,
            "completed": completed,
            "clients": clients,
            "revenue": revenue,
        },
        breakdown={s: c for s, c in status_rows},
        trend={"labels": days, "values": counts},
        top_services=[{"name": r[0], "count": int(r[1])} for r in top_rows],
        recent=recent,
        statuses=BOOKING_STATUSES,
    )


# -------------------------------------------------------------- bookings


@bp.get("/bookings")
def bookings():
    q = (request.args.get("q") or "").strip()
    status = request.args.get("status") or ""

    query = db.select(Booking)
    if q:
        like = f"%{q}%"
        query = query.where(
            db.or_(
                Booking.reference.ilike(like),
                Booking.name.ilike(like),
                Booking.phone.ilike(like),
                Booking.city.ilike(like),
            )
        )
    if status in BOOKING_STATUSES:
        query = query.where(Booking.status == status)

    pagination = db.paginate(
        query.order_by(Booking.created_at.desc()),
        page=_page(),
        per_page=current_app.config["PER_PAGE"],
        error_out=False,
    )

    return render_template(
        "admin/bookings.html",
        page_title="Bookings",
        pagination=pagination,
        statuses=BOOKING_STATUSES,
        filters={"q": q, "status": status},
    )


# -------------------------------------------------------------- services


@bp.get("/services")
def services():
    categories = db.session.scalars(
        db.select(Category).order_by(Category.sort_order)
    ).all()
    return render_template(
        "admin/services.html",
        page_title="Services",
        categories=categories,
        services=db.session.scalars(
            db.select(Service).order_by(Service.category_id, Service.sort_order)
        ).all(),
    )


@bp.post("/services/save")
def save_service():
    bail = _form_ok(url_for("admin.services"))
    if bail:
        return bail

    service_id = _int_or_none(request.form.get("id"))
    service = db.session.get(Service, service_id) if service_id else None

    name = (request.form.get("name") or "").strip()
    category_id = _int_or_none(request.form.get("category_id"))

    if not name or not category_id:
        flash("Service ka naam aur category zaroori hai.", "error")
        return redirect(url_for("admin.services"))

    if service is None:
        service = Service()
        db.session.add(service)

    slug = (request.form.get("slug") or "").strip() or slugify(name)
    clash = db.session.scalar(db.select(Service).filter_by(slug=slug))
    if clash and clash.id != service.id:
        slug = f"{slug}-{db.session.scalar(db.select(func.count(Service.id))) + 1}"

    service.name = name[:120]
    service.slug = slug[:140]
    service.category_id = category_id
    service.summary = (request.form.get("summary") or "").strip()[:300]
    service.description = (request.form.get("description") or "").strip()
    service.includes = (request.form.get("includes") or "").strip()
    service.price_from = _int_or_none(request.form.get("price_from")) or 0
    service.old_price = _int_or_none(request.form.get("old_price"))
    service.duration = (request.form.get("duration") or "").strip()[:60]
    service.icon = (request.form.get("icon") or "spray").strip()[:40]
    service.sort_order = _int_or_none(request.form.get("sort_order")) or 0
    service.is_featured = request.form.get("is_featured") == "on"
    service.is_active = request.form.get("is_active") == "on"

    upload = request.files.get("image")
    if upload and upload.filename:
        try:
            stored = save_image(upload, prefix="service")
        except ValueError as err:
            flash(str(err), "error")
            return redirect(url_for("admin.services"))
        delete_image(service.image)
        service.image = stored

    db.session.commit()
    flash(f"'{service.name}' save ho gaya.", "info")
    return redirect(url_for("admin.services"))


@bp.post("/services/<int:service_id>/duplicate")
def duplicate_service(service_id):
    """Copy a service so a similar one is three fields away, not twelve."""
    bail = _form_ok(url_for("admin.services"))
    if bail:
        return bail

    source = db.session.get(Service, service_id)
    if source is None:
        flash("Yeh service nahi mili.", "error")
        return redirect(url_for("admin.services"))

    name = f"{source.name} (copy)"[:120]
    slug = slugify(name)
    n = 2
    while db.session.scalar(db.select(Service).filter_by(slug=slug)):
        slug = f"{slugify(source.name)}-copy-{n}"
        n += 1

    copy = Service(
        category_id=source.category_id,
        name=name,
        slug=slug[:140],
        summary=source.summary,
        description=source.description,
        includes=source.includes,
        price_from=source.price_from,
        old_price=source.old_price,
        duration=source.duration,
        icon=source.icon,
        rating=source.rating,
        is_featured=False,
        is_active=False,  # off until the copy has been edited
        sort_order=source.sort_order + 1,
    )
    db.session.add(copy)
    db.session.commit()

    flash(f"'{source.name}' ki copy ban gayi — naam aur qeemat badal kar live karein.", "info")
    return redirect(url_for("admin.services"))


@bp.post("/categories/save")
def save_category():
    bail = _form_ok(url_for("admin.services"))
    if bail:
        return bail

    category_id = _int_or_none(request.form.get("id"))
    category = db.session.get(Category, category_id) if category_id else None

    name = (request.form.get("name") or "").strip()
    if not name:
        flash("Category ka naam zaroori hai.", "error")
        return redirect(url_for("admin.services"))

    if category is None:
        category = Category()
        db.session.add(category)

    slug = (request.form.get("slug") or "").strip() or slugify(name)
    clash = db.session.scalar(db.select(Category).filter_by(slug=slug))
    if clash and clash.id != category.id:
        slug = f"{slug}-2"

    category.name = name[:90]
    category.slug = slug[:90]
    category.tagline = (request.form.get("tagline") or "").strip()[:200]
    category.description = (request.form.get("description") or "").strip()
    category.accent = (request.form.get("accent") or "green").strip()[:20]
    category.sort_order = _int_or_none(request.form.get("sort_order")) or 0

    db.session.commit()
    flash(f"'{category.name}' save ho gayi.", "info")
    return redirect(url_for("admin.services"))


# --------------------------------------------------------------- clients


@bp.get("/clients")
def clients():
    q = (request.args.get("q") or "").strip()

    query = db.select(User).where(User.role == "client")
    if q:
        like = f"%{q}%"
        query = query.where(
            db.or_(User.name.ilike(like), User.email.ilike(like), User.phone.ilike(like))
        )

    pagination = db.paginate(
        query.order_by(User.created_at.desc()),
        page=_page(),
        per_page=current_app.config["PER_PAGE"],
        error_out=False,
    )
    return render_template(
        "admin/clients.html",
        page_title="Clients",
        pagination=pagination,
        filters={"q": q},
    )


@bp.get("/team")
def team():
    members = db.session.scalars(
        db.select(User).where(User.role == "admin").order_by(User.name)
    ).all()
    return render_template("admin/team.html", page_title="Admin users", members=members)


# ---------------------------------------------------------- testimonials


@bp.get("/reviews")
def reviews():
    items = db.session.scalars(
        db.select(Testimonial).order_by(Testimonial.id.desc())
    ).all()
    return render_template("admin/reviews.html", page_title="Reviews", items=items)


@bp.post("/reviews/save")
def save_review():
    bail = _form_ok(url_for("admin.reviews"))
    if bail:
        return bail

    review_id = _int_or_none(request.form.get("id"))
    review = db.session.get(Testimonial, review_id) if review_id else None

    name = (request.form.get("name") or "").strip()
    body = (request.form.get("body") or "").strip()
    if not name or not body:
        flash("Customer ka naam aur review zaroori hai.", "error")
        return redirect(url_for("admin.reviews"))

    if review is None:
        review = Testimonial()
        db.session.add(review)

    review.name = name[:90]
    review.city = (request.form.get("city") or "").strip()[:80]
    review.service = (request.form.get("service") or "").strip()[:120]
    review.rating = min(5, max(1, _int_or_none(request.form.get("rating")) or 5))
    review.body = body[:800]
    review.is_published = request.form.get("is_published") == "on"

    db.session.commit()
    flash("Review save ho gaya.", "info")
    return redirect(url_for("admin.reviews"))


# --------------------------------------------------------------- settings


@bp.get("/settings")
def settings():
    return render_template(
        "admin/settings.html",
        page_title="Site settings",
        s=Setting.all_as_dict(),
    )


@bp.post("/settings")
def save_settings():
    bail = _form_ok(url_for("admin.settings"))
    if bail:
        return bail

    text_fields = [
        "brand_name", "tagline", "whatsapp_number", "phone", "phone_alt",
        "email", "address", "city", "hours", "facebook", "instagram",
        "hero_title", "hero_subtitle", "about_body", "map_embed",
        "stat_rating", "stat_jobs", "stat_staff", "stat_warranty",
        "chat_agent", "chat_role", "chat_reply_time", "chat_greeting", "chat_away",
    ]
    for field in text_fields:
        if field in request.form:
            Setting.put(field, (request.form.get(field) or "").strip())

    # Appearance — only accept keys that exist in the catalogue.
    if "theme" in request.form:
        Setting.put("theme", theming.get_theme(request.form.get("theme"))["key"])

    for field, fallback in (
        ("font_heading", theming.DEFAULT_HEADING_FONT),
        ("font_body", theming.DEFAULT_BODY_FONT),
    ):
        if field in request.form:
            chosen = (request.form.get(field) or "").strip()
            Setting.put(field, chosen if chosen in theming.FONT_MAP else fallback)

    if "chat_form" in request.form:
        Setting.put("chat_enabled", "1" if request.form.get("chat_enabled") == "on" else "0")

    for field, prefix in (("logo", "logo"), ("favicon", "favicon"), ("hero_image", "hero")):
        upload = request.files.get(field)
        if upload and upload.filename:
            try:
                stored = save_image(upload, prefix=prefix)
            except ValueError as err:
                flash(str(err), "error")
                return redirect(url_for("admin.settings"))
            delete_image(Setting.get(field))
            Setting.put(field, stored)

    for field in ("logo", "favicon", "hero_image"):
        if request.form.get(f"remove_{field}") == "on":
            delete_image(Setting.get(field))
            Setting.put(field, "")

    db.session.commit()
    flash("Settings save ho gayi.", "info")
    return redirect(url_for("admin.settings"))
