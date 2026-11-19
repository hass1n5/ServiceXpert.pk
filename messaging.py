"""Turn a booking into a ready-to-send WhatsApp message.

The browser opens https://wa.me/<number>?text=<message>, so the enquiry
lands in the business WhatsApp inbox the moment the form is submitted.
The booking is saved in the database first, so nothing is lost if the
customer never taps send.
"""

import re
from urllib.parse import quote


def normalise_number(raw, default_country="92"):
    """'0300-1234567' -> '923001234567' (wa.me wants digits only)."""
    digits = re.sub(r"\D", "", raw or "")
    if not digits:
        return ""
    if digits.startswith("00"):
        digits = digits[2:]
    if digits.startswith("0"):
        digits = default_country + digits[1:]
    elif len(digits) == 10 and not digits.startswith(default_country):
        digits = default_country + digits
    return digits


def booking_message(booking, brand="Our team"):
    lines = [
        f"*Nayi booking — {brand}*",
        "",
        f"Ref: {booking.reference}",
        f"Service: {booking.service_name}",
        f"Naam: {booking.name}",
        f"Phone: {booking.phone}",
    ]
    if booking.email:
        lines.append(f"Email: {booking.email}")
    if booking.city:
        lines.append(f"Shehar: {booking.city}")
    if booking.address:
        lines.append(f"Pata: {booking.address}")
    if booking.preferred_date:
        lines.append(f"Pasandeeda din: {booking.preferred_date}")
    if booking.message:
        lines += ["", f"Tafseel: {booking.message}"]
    return "\n".join(lines)


def whatsapp_url(number, message):
    target = normalise_number(number)
    if not target:
        return ""
    return f"https://wa.me/{target}?text={quote(message)}"
