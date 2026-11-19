# ServiceXpert.pk — DirectAdmin / Passenger deployment

## Python App settings

Use these values in **Setup Python App** (paths vary by hosting account):

- Python version: 3.11 or newer
- Application root: the folder containing `app.py` and `passenger_wsgi.py`
- Application URL: `https://servicexpert.pk/`
- Application startup file: `passenger_wsgi.py`
- Application entry point: `application`

Do not point the app at the ZIP's parent folder. The application root must be the
`sparkle` folder itself (or rename that folder and use the renamed folder).

## Environment variables

Set these in DirectAdmin's Python App environment section before first start:

- `FLASK_ENV=production`
- `SESSION_COOKIE_SECURE=1`
- `SECRET_KEY=<long-random-secret>`
- `ADMIN_EMAIL=<your-admin-email>`
- `ADMIN_PASSWORD=<a-strong-password-at-least-12-characters>`
- optional: `ADMIN_NAME=Site Admin`

For SQLite, no `DATABASE_URL` is required. The default database is `sparkle.db`
in the application root. If MySQL/PostgreSQL is used later, set `DATABASE_URL`.

## Install packages

Activate the virtualenv shown by DirectAdmin, then from the app root run:

```bash
pip install -r requirements.txt
python production_setup.py
```

`production_setup.py` is safe to re-run: it creates missing tables/content and
does not duplicate existing services or admin accounts. It does **not** create
demo clients, demo bookings, or the old public demo password.

## Restart

Use DirectAdmin's **Restart** button after installation/bootstrap. Then verify:

- `/healthz` returns JSON with `status: ok`
- `/` loads the frontend
- `/services` loads the service catalogue
- `/admin/login` loads the admin login
- log in with `ADMIN_EMAIL` / `ADMIN_PASSWORD`
- submit one test booking and confirm it appears under Admin → Bookings

## Common 404 cause

If DirectAdmin shows its own 404 rather than the website's styled 404 page, the
request is not reaching Flask. Re-check Application URL, Application root,
startup file `passenger_wsgi.py`, entry point `application`, and restart the app.
