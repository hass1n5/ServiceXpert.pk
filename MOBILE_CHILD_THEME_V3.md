# ServiceXpert.pk — Mobile Child Theme v4

This package keeps the existing Flask backend, routes, database, and desktop layout. The mobile child layer activates at `max-width: 860px`.

## Mobile header
- Logo stays on the left.
- Client Login icon and hamburger stay on the right.
- No forced 40px logo gap; flex layout uses available space safely.
- Desktop phone and quote controls are hidden only on mobile.
- Hamburger opens the dedicated `#mobileNav` drawer.
- Drawer closes by X, backdrop, Escape, or navigation link.
- Services expands inside the drawer.

## Mobile home
- Dedicated `templates/public/mobile/home.html` is used on mobile.
- Responsive hero, stats, service cards, steps, reviews, quote form, CTA and floating widgets.
- Existing Flask data and booking form are reused.

## Files changed for the child layer
- `templates/public/base.html`
- `templates/public/home.html` (already contains desktop/mobile split)
- `templates/public/mobile/home.html`
- `static/css/mobile-theme.css`
- `static/js/mobile-theme.js`
- `static/js/site.js` (legacy mobile drawer handler is skipped when child drawer exists)

## Deployment
Upload/extract the complete ZIP into the existing project directory. Do not replace the database or backend configuration. After deployment, restart the Flask/WSGI application and hard-refresh the phone browser.
