"""Colour themes and font catalogue.

The whole site is painted from a handful of CSS custom properties. Instead of
writing twelve near-identical blocks into site.css, each theme declares six
anchor colours here and the tints (wash / line / soft shadow) are mixed from
them, so a new theme is six hex values and nothing else.

Fonts are plain Google Fonts families. Only weights that actually exist for a
family are requested — css2 rejects the entire URL if one weight is wrong, so
the catalogue stays conservative: "400;700" for families that ship a bold,
"400" for single-weight display faces.
"""

DEFAULT_THEME = "emerald"
DEFAULT_HEADING_FONT = "Outfit"
DEFAULT_BODY_FONT = "Plus Jakarta Sans"


# --------------------------------------------------------------- colours


def _rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i: i + 2], 16) for i in (0, 2, 4))


def _hex(rgb):
    return "#" + "".join(f"{max(0, min(255, int(round(c)))):02x}" for c in rgb)


def tint(colour, amount):
    """Mix `colour` with white. amount=0.9 -> 90% white."""
    r, g, b = _rgb(colour)
    return _hex((r + (255 - r) * amount, g + (255 - g) * amount, b + (255 - b) * amount))


def shade(colour, amount):
    """Mix `colour` with black."""
    r, g, b = _rgb(colour)
    return _hex((r * (1 - amount), g * (1 - amount), b * (1 - amount)))


def rgba(colour, alpha):
    r, g, b = _rgb(colour)
    return f"rgba({r}, {g}, {b}, {alpha})"


# key, label, primary, primary-deep, secondary, secondary-deep, gold, gold-deep
THEMES = [
    {
        "key": "emerald",
        "name": "Emerald & Gold",
        "note": "Default — cleaning ke liye classic sabz aur sunehra",
        "primary": "#1a7a50", "primary_deep": "#0f3d2e",
        "secondary": "#1b54b8", "secondary_deep": "#12336e",
        "gold": "#f4c430", "gold_deep": "#b8860b",
    },
    {
        "key": "ocean",
        "name": "Ocean Blue",
        "note": "Thanda, saaf pani wala ehsaas",
        "primary": "#0f6fb5", "primary_deep": "#0a3c63",
        "secondary": "#0d9488", "secondary_deep": "#115e56",
        "gold": "#f6a623", "gold_deep": "#b9741a",
    },
    {
        "key": "royal",
        "name": "Royal Purple",
        "note": "Premium aur alag dikhne wala",
        "primary": "#6d3bd1", "primary_deep": "#341b6b",
        "secondary": "#c026d3", "secondary_deep": "#701a75",
        "gold": "#f5b301", "gold_deep": "#9a6b00",
    },
    {
        "key": "sunset",
        "name": "Sunset Orange",
        "note": "Garam, energetic — offers aur discounts ke liye",
        "primary": "#e2662a", "primary_deep": "#7a2e12",
        "secondary": "#0ea5a4", "secondary_deep": "#0f4d4c",
        "gold": "#ffb703", "gold_deep": "#b07603",
    },
    {
        "key": "crimson",
        "name": "Crimson Red",
        "note": "Bold — pest control par zor dena ho to",
        "primary": "#c62828", "primary_deep": "#611212",
        "secondary": "#1f3a8a", "secondary_deep": "#16265c",
        "gold": "#f0b429", "gold_deep": "#a97b09",
    },
    {
        "key": "teal",
        "name": "Teal & Coral",
        "note": "Hospital jaisi safai ka feel",
        "primary": "#0f8a8a", "primary_deep": "#0a4747",
        "secondary": "#e4572e", "secondary_deep": "#7a2a13",
        "gold": "#ffc145", "gold_deep": "#b8860b",
    },
    {
        "key": "midnight",
        "name": "Midnight Navy",
        "note": "Corporate aur commercial clients ke liye",
        "primary": "#1e3a8a", "primary_deep": "#0b1a44",
        "secondary": "#0891b2", "secondary_deep": "#0a4d5c",
        "gold": "#e0b84e", "gold_deep": "#97771f",
    },
    {
        "key": "forest",
        "name": "Forest & Lime",
        "note": "Eco-friendly, organic chemicals wala message",
        "primary": "#2f6b34", "primary_deep": "#14331a",
        "secondary": "#4d7c0f", "secondary_deep": "#27400a",
        "gold": "#e8c547", "gold_deep": "#8a7212",
    },
    {
        "key": "rose",
        "name": "Rose Pink",
        "note": "Home aur maid services ke liye narm rang",
        "primary": "#be2a63", "primary_deep": "#611030",
        "secondary": "#7c3aed", "secondary_deep": "#3c1d7a",
        "gold": "#f7b32b", "gold_deep": "#a8730d",
    },
    {
        "key": "amber",
        "name": "Amber & Earth",
        "note": "Mitti jaise garam rang, dhool-mitti wale kaam ke liye",
        "primary": "#b45f06", "primary_deep": "#5c2f04",
        "secondary": "#2f6f4e", "secondary_deep": "#163827",
        "gold": "#f2b705", "gold_deep": "#a37a03",
    },
    {
        "key": "slate",
        "name": "Slate Corporate",
        "note": "Sanjeeda aur neutral — factories aur offices",
        "primary": "#334155", "primary_deep": "#0f172a",
        "secondary": "#0369a1", "secondary_deep": "#073f63",
        "gold": "#eab308", "gold_deep": "#9a7b0a",
    },
    {
        "key": "cyan",
        "name": "Fresh Aqua",
        "note": "Water tank aur washroom services ke liye",
        "primary": "#0891b2", "primary_deep": "#094a5c",
        "secondary": "#2563eb", "secondary_deep": "#14306f",
        "gold": "#fbbf24", "gold_deep": "#b07d06",
    },
]

THEME_MAP = {t["key"]: t for t in THEMES}


def get_theme(key):
    return THEME_MAP.get(key or "", THEME_MAP[DEFAULT_THEME])


def theme_variables(key):
    """The CSS custom properties a theme overrides."""
    t = get_theme(key)
    primary, secondary, gold = t["primary"], t["secondary"], t["gold"]

    return {
        "--green": primary,
        "--green-deep": t["primary_deep"],
        "--green-wash": tint(primary, 0.90),
        "--green-line": tint(primary, 0.74),
        "--blue": secondary,
        "--blue-deep": t["secondary_deep"],
        "--blue-wash": tint(secondary, 0.90),
        "--gold": gold,
        "--gold-deep": t["gold_deep"],
        "--gold-wash": tint(gold, 0.86),
        "--wash": tint(primary, 0.955),
        "--line": tint(primary, 0.88),
        "--line-strong": tint(primary, 0.76),
        "--ink": shade(tint(primary, 0.30), 0.80),
        "--ink-soft": shade(tint(primary, 0.42), 0.42),
        "--ink-faint": shade(tint(primary, 0.60), 0.25),
        "--shadow": f"0 20px 45px -28px {rgba(t['primary_deep'], 0.55)}",
        "--shadow-soft": f"0 10px 30px -22px {rgba(t['primary_deep'], 0.5)}",
        "--brand-rgb": ", ".join(str(c) for c in _rgb(primary)),
        "--gold-rgb": ", ".join(str(c) for c in _rgb(gold)),
    }


def theme_css(key):
    """`:root { ... }` block injected into every page."""
    rules = "".join(f"{k}:{v};" for k, v in theme_variables(key).items())
    return f":root{{{rules}}}"


def theme_swatch(key):
    """Three colours used for the little preview chip in the admin panel."""
    t = get_theme(key)
    return [t["primary"], t["secondary"], t["gold"]]


# ----------------------------------------------------------------- fonts

# (family, group, weights). Weights are exactly what Google Fonts serves.
FONTS = [
    # --- Modern sans ---
    ("Inter", "sans", "400;700"),
    ("Plus Jakarta Sans", "sans", "400;700"),
    ("Outfit", "sans", "400;700"),
    ("Manrope", "sans", "400;700"),
    ("Sora", "sans", "400;700"),
    ("Urbanist", "sans", "400;700"),
    ("Figtree", "sans", "400;700"),
    ("Lexend", "sans", "400;700"),
    ("DM Sans", "sans", "400;700"),
    ("Space Grotesk", "sans", "400;700"),
    ("Epilogue", "sans", "400;700"),
    ("Onest", "sans", "400;700"),
    ("Syne", "sans", "400;700"),
    ("Jost", "sans", "400;700"),
    ("Public Sans", "sans", "400;700"),
    ("Archivo", "sans", "400;700"),
    ("Chivo", "sans", "400;700"),
    ("Red Hat Display", "sans", "400;700"),
    ("Overpass", "sans", "400;700"),
    ("Schibsted Grotesk", "sans", "400;700"),
    ("Instrument Sans", "sans", "400;700"),
    ("Bricolage Grotesque", "sans", "400;700"),
    # --- Classic sans ---
    ("Roboto", "sans", "400;700"),
    ("Open Sans", "sans", "400;700"),
    ("Lato", "sans", "400;700"),
    ("Montserrat", "sans", "400;700"),
    ("Poppins", "sans", "400;700"),
    ("Raleway", "sans", "400;700"),
    ("Nunito", "sans", "400;700"),
    ("Nunito Sans", "sans", "400;700"),
    ("Work Sans", "sans", "400;700"),
    ("Rubik", "sans", "400;700"),
    ("Karla", "sans", "400;700"),
    ("Mulish", "sans", "400;700"),
    ("Barlow", "sans", "400;700"),
    ("Heebo", "sans", "400;700"),
    ("Hind", "sans", "400;700"),
    ("Cabin", "sans", "400;700"),
    ("Exo 2", "sans", "400;700"),
    ("Asap", "sans", "400;700"),
    ("Oxygen", "sans", "400;700"),
    ("Ubuntu", "sans", "400;700"),
    ("Fira Sans", "sans", "400;700"),
    ("Source Sans 3", "sans", "400;700"),
    ("IBM Plex Sans", "sans", "400;700"),
    ("Noto Sans", "sans", "400;700"),
    ("PT Sans", "sans", "400;700"),
    ("Titillium Web", "sans", "400;700"),
    ("Assistant", "sans", "400;700"),
    ("Catamaran", "sans", "400;700"),
    ("Saira", "sans", "400;700"),
    ("Signika", "sans", "400;700"),
    # --- Rounded / friendly ---
    ("Quicksand", "sans", "400;700"),
    ("Comfortaa", "sans", "400;700"),
    ("Josefin Sans", "sans", "400;700"),
    ("Dosis", "sans", "400;700"),
    ("Varela Round", "sans", "400"),
    ("Questrial", "sans", "400"),
    ("Baloo 2", "sans", "400;700"),
    ("Fredoka", "sans", "400;700"),
    # --- Condensed / headline ---
    ("Oswald", "display", "400;700"),
    ("Bebas Neue", "display", "400"),
    ("Anton", "display", "400"),
    ("Teko", "display", "400;700"),
    ("Kanit", "display", "400;700"),
    ("Prompt", "display", "400;700"),
    ("Fjalla One", "display", "400"),
    ("Archivo Black", "display", "400"),
    ("Staatliches", "display", "400"),
    ("Russo One", "display", "400"),
    ("Orbitron", "display", "400;700"),
    ("Audiowide", "display", "400"),
    ("Righteous", "display", "400"),
    ("Alfa Slab One", "display", "400"),
    ("Abril Fatface", "display", "400"),
    ("Poiret One", "display", "400"),
    ("Cinzel", "display", "400;700"),
    ("Monoton", "display", "400"),
    # --- Serif ---
    ("Playfair Display", "serif", "400;700"),
    ("Merriweather", "serif", "400;700"),
    ("Lora", "serif", "400;700"),
    ("PT Serif", "serif", "400;700"),
    ("Libre Baskerville", "serif", "400;700"),
    ("EB Garamond", "serif", "400;700"),
    ("Cormorant Garamond", "serif", "400;700"),
    ("Crimson Text", "serif", "400;700"),
    ("Spectral", "serif", "400;700"),
    ("Source Serif 4", "serif", "400;700"),
    ("IBM Plex Serif", "serif", "400;700"),
    ("Noto Serif", "serif", "400;700"),
    ("Literata", "serif", "400;700"),
    ("Fraunces", "serif", "400;700"),
    ("Newsreader", "serif", "400;700"),
    ("Frank Ruhl Libre", "serif", "400;700"),
    ("Vollkorn", "serif", "400;700"),
    ("Domine", "serif", "400;700"),
    ("Cardo", "serif", "400;700"),
    ("Old Standard TT", "serif", "400;700"),
    ("Marcellus", "serif", "400"),
    ("Prata", "serif", "400"),
    ("DM Serif Display", "serif", "400"),
    ("Instrument Serif", "serif", "400"),
    # --- Slab ---
    ("Roboto Slab", "serif", "400;700"),
    ("Bitter", "serif", "400;700"),
    ("Zilla Slab", "serif", "400;700"),
    ("Arvo", "serif", "400;700"),
    ("Rokkitt", "serif", "400;700"),
    ("Josefin Slab", "serif", "400;700"),
    ("Bree Serif", "serif", "400"),
    # --- Handwriting ---
    ("Caveat", "hand", "400;700"),
    ("Dancing Script", "hand", "400;700"),
    ("Pacifico", "hand", "400"),
    ("Lobster", "hand", "400"),
    ("Satisfy", "hand", "400"),
    ("Great Vibes", "hand", "400"),
    # --- Monospace ---
    ("JetBrains Mono", "mono", "400;700"),
    ("Fira Code", "mono", "400;700"),
    ("IBM Plex Mono", "mono", "400;700"),
    ("Source Code Pro", "mono", "400;700"),
    ("Roboto Mono", "mono", "400;700"),
    ("Space Mono", "mono", "400;700"),
    ("Inconsolata", "mono", "400;700"),
    # --- Urdu / Arabic script ---
    ("Noto Nastaliq Urdu", "urdu", "400;700"),
    ("Gulzar", "urdu", "400"),
    ("Amiri", "urdu", "400;700"),
    ("Cairo", "urdu", "400;700"),
    ("Almarai", "urdu", "400;700"),
    ("Tajawal", "urdu", "400;700"),
    ("Changa", "urdu", "400;700"),
    ("El Messiri", "urdu", "400;700"),
    ("Reem Kufi", "urdu", "400;700"),
    ("Markazi Text", "urdu", "400;700"),
    ("Noto Kufi Arabic", "urdu", "400;700"),
    ("Noto Naskh Arabic", "urdu", "400;700"),
    ("Scheherazade New", "urdu", "400;700"),
    ("Lalezar", "urdu", "400"),
    ("Rakkas", "urdu", "400"),
    ("Aref Ruqaa", "urdu", "400;700"),
]

# Families that ship the whole 400–700 range, so a heading can use a real
# semibold instead of snapping to bold. Anything not listed here stays on
# "400;700" — a weight Google doesn't serve fails the request for that family.
FULL_RANGE = {
    "Inter", "Plus Jakarta Sans", "Outfit", "Manrope", "Sora", "Urbanist",
    "Figtree", "Lexend", "DM Sans", "Space Grotesk", "Epilogue", "Onest",
    "Jost", "Public Sans", "Archivo", "Roboto", "Open Sans", "Montserrat",
    "Poppins", "Raleway", "Nunito", "Nunito Sans", "Work Sans", "Rubik",
    "Mulish", "Heebo", "Karla", "Barlow", "Quicksand", "Josefin Sans",
    "Kanit", "Oswald", "Playfair Display", "Lora", "Bitter", "Fraunces",
    "Literata", "Cairo",
}

FONTS = [
    (name, group, "400;500;600;700" if name in FULL_RANGE else weights)
    for name, group, weights in FONTS
]

GROUP_LABELS = {
    "sans": "Sans serif (aam istemal)",
    "display": "Display / headline",
    "serif": "Serif (classic)",
    "hand": "Handwriting",
    "mono": "Monospace",
    "urdu": "Urdu / Arabic script",
}

GROUP_ORDER = ["sans", "display", "serif", "hand", "mono", "urdu"]

FONT_MAP = {name: {"name": name, "group": group, "weights": weights}
            for name, group, weights in FONTS}

FALLBACKS = {
    "sans": 'ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif',
    "display": '"Trebuchet MS", ui-sans-serif, system-ui, sans-serif',
    "serif": 'ui-serif, Georgia, "Times New Roman", serif',
    "hand": '"Segoe Script", cursive',
    "mono": 'ui-monospace, "SF Mono", Menlo, monospace',
    "urdu": '"Noto Naskh Arabic", "Segoe UI", serif',
}


def font_groups():
    """Fonts arranged for <optgroup> rendering."""
    return [
        {
            "key": key,
            "label": GROUP_LABELS[key],
            "fonts": [f for f in FONT_MAP.values() if f["group"] == key],
        }
        for key in GROUP_ORDER
    ]


def font_stack(name, fallback_group="sans"):
    info = FONT_MAP.get(name or "")
    if not info:
        return FALLBACKS[fallback_group]
    return f'"{info["name"]}", {FALLBACKS[info["group"]]}'


def font_css_url(name):
    """One request per family, so a bad family can't break the other one."""
    info = FONT_MAP.get(name or "")
    if not info:
        return None
    family = info["name"].replace(" ", "+")
    return (
        f"https://fonts.googleapis.com/css2?family={family}"
        f":wght@{info['weights']}&display=swap"
    )


def font_links(heading, body):
    urls = []
    for name in (heading or DEFAULT_HEADING_FONT, body or DEFAULT_BODY_FONT):
        url = font_css_url(name)
        if url and url not in urls:
            urls.append(url)
    return urls


def appearance_css(theme, heading, body):
    """Theme colours + font families, ready to drop into a <style> tag."""
    variables = theme_variables(theme)
    variables["--font-head"] = font_stack(heading or DEFAULT_HEADING_FONT, "display")
    variables["--font-body"] = font_stack(body or DEFAULT_BODY_FONT, "sans")
    rules = "".join(f"{k}:{v};" for k, v in variables.items())
    return f":root{{{rules}}}"


def admin_appearance_css(theme, heading, body):
    """The admin panel reads the same theme but needs its own tints.

    On the public site --gold is the bright button colour; in the panel the
    same token is used as *text* on a pale wash, so it has to be the dark
    version or the badges become unreadable.
    """
    t = get_theme(theme)
    primary, secondary = t["primary"], t["secondary"]

    variables = {
        "--forest": t["primary_deep"],
        "--forest-lift": tint(t["primary_deep"], 0.12),
        "--green": primary,
        "--green-wash": tint(primary, 0.90),
        "--blue": secondary,
        "--blue-wash": tint(secondary, 0.90),
        "--gold": t["gold_deep"],
        "--gold-wash": tint(t["gold"], 0.86),
        "--paper": tint(primary, 0.935),
        "--sunk": tint(primary, 0.965),
        "--line": tint(primary, 0.86),
        "--line-strong": tint(primary, 0.76),
        "--ink": shade(tint(primary, 0.30), 0.80),
        "--ink-soft": shade(tint(primary, 0.42), 0.42),
        "--ink-faint": shade(tint(primary, 0.60), 0.25),
        "--shadow": f"0 18px 40px -22px {rgba(t['primary_deep'], 0.5)}",
        "--font-head": font_stack(heading or DEFAULT_HEADING_FONT, "display"),
        "--font-body": font_stack(body or DEFAULT_BODY_FONT, "sans"),
    }
    rules = "".join(f"{k}:{v};" for k, v in variables.items())
    return f":root{{{rules}}}"
