import random
import string

from flask import Blueprint, abort, jsonify, render_template, request, url_for
from flask_login import current_user

from extensions import db
from messaging import booking_message, whatsapp_url
from models import Booking, Category, Service, Setting, Testimonial
from security import csrf_protect

bp = Blueprint("public", __name__)


def new_reference():
    while True:
        ref = "BK-" + "".join(random.choices(string.digits, k=6))
        if not db.session.scalar(db.select(Booking).filter_by(reference=ref)):
            return ref


def load_categories():
    return db.session.scalars(
        db.select(Category).order_by(Category.sort_order, Category.name)
    ).all()


@bp.get("/")
def home():
    categories = load_categories()
    featured = db.session.scalars(
        db.select(Service)
        .where(Service.is_active.is_(True), Service.is_featured.is_(True))
        .order_by(Service.sort_order)
        .limit(6)
    ).all()
    reviews = db.session.scalars(
        db.select(Testimonial)
        .where(Testimonial.is_published.is_(True))
        .order_by(Testimonial.id.desc())
        .limit(6)
    ).all()

    return render_template(
        "public/home.html",
        categories=categories,
        featured=featured,
        reviews=reviews,
        all_services=db.session.scalars(
            db.select(Service).where(Service.is_active.is_(True)).order_by(Service.name)
        ).all(),
    )


@bp.get("/about-us")
def about():
    return render_template("public/about.html", categories=load_categories())


@bp.get("/services")
def services():
    return render_template(
        "public/services.html",
        categories=load_categories(),
        all_services=db.session.scalars(
            db.select(Service).where(Service.is_active.is_(True)).order_by(Service.name)
        ).all(),
    )


@bp.get("/services/<slug>")
def category_detail(slug):
    category = db.session.scalar(db.select(Category).filter_by(slug=slug))
    if category is None:
        abort(404)
    return render_template(
        "public/category.html",
        category=category,
        categories=load_categories(),
        all_services=db.session.scalars(
            db.select(Service).where(Service.is_active.is_(True)).order_by(Service.name)
        ).all(),
    )


@bp.get("/<slug>")
def service_detail(slug):
    service = db.session.scalar(
        db.select(Service).filter_by(slug=slug, is_active=True)
    )
    if service is None:
        abort(404)

    related = db.session.scalars(
        db.select(Service)
        .where(
            Service.category_id == service.category_id,
            Service.id != service.id,
            Service.is_active.is_(True),
        )
        .limit(4)
    ).all()

    return render_template(
        "public/service.html",
        service=service,
        related=related,
        categories=load_categories(),
        all_services=db.session.scalars(
            db.select(Service).where(Service.is_active.is_(True)).order_by(Service.name)
        ).all(),
    )


@bp.get("/contact-us")
def contact():
    return render_template(
        "public/contact.html",
        categories=load_categories(),
        all_services=db.session.scalars(
            db.select(Service).where(Service.is_active.is_(True)).order_by(Service.name)
        ).all(),
    )


@bp.post("/book")
@csrf_protect
def submit_booking():
    """Saves the enquiry, then hands back a WhatsApp link for the browser."""
    data = request.get_json(silent=True) or request.form

    name = (data.get("name") or "").strip()
    phone = (data.get("phone") or "").strip()

    if len(name) < 2:
        return jsonify(error="Apna poora naam likhein."), 422
    if len("".join(ch for ch in phone if ch.isdigit())) < 10:
        return jsonify(error="Sahi phone number likhein, jaise 0300-1234567."), 422

    service = None
    raw_service = data.get("service_id")
    if raw_service:
        try:
            service = db.session.get(Service, int(raw_service))
        except (TypeError, ValueError):
            service = None

    booking = Booking(
        reference=new_reference(),
        name=name[:90],
        phone=phone[:30],
        email=(data.get("email") or "").strip()[:120] or None,
        city=(data.get("city") or "").strip()[:80] or None,
        address=(data.get("address") or "").strip()[:255] or None,
        preferred_date=(data.get("preferred_date") or "").strip()[:30] or None,
        message=(data.get("message") or "").strip()[:1500] or None,
        service=service,
        user=current_user if current_user.is_authenticated else None,
        source=(data.get("source") or "website")[:30],
    )

    db.session.add(booking)
    db.session.commit()

    brand = Setting.get("brand_name", "Sparkle Care")
    link = whatsapp_url(
        Setting.get("whatsapp_number", ""), booking_message(booking, brand)
    )

    return jsonify(
        reference=booking.reference,
        whatsapp_url=link,
        message=f"Shukriya {name.split()[0]}! Aapki request {booking.reference} "
        "darj ho gayi. Hamari team jald raabta karegi.",
    ), 201


@bp.get("/sitemap.xml")
def sitemap():
    urls = [url_for("public.home", _external=True),
            url_for("public.about", _external=True),
            url_for("public.services", _external=True),
            url_for("public.contact", _external=True)]
    for cat in load_categories():
        urls.append(url_for("public.category_detail", slug=cat.slug, _external=True))
    for svc in db.session.scalars(db.select(Service).where(Service.is_active.is_(True))):
        urls.append(url_for("public.service_detail", slug=svc.slug, _external=True))

    body = "".join(f"<url><loc>{u}</loc></url>" for u in urls)
    xml = ('<?xml version="1.0" encoding="UTF-8"?>'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
           f"{body}</urlset>")
    return xml, 200, {"Content-Type": "application/xml"}
