"""SEO pass applied to every built page (after improve.post).

- Search-result titles kept to 60 characters or less (og:title keeps the full title).
- Utility pages (cart, order pages, search) are always noindex and left out of sitemap.xml.
- Correct hreflang pairs between English and Spanish pages.
- Self-hosted fonts (no Google Fonts request), with the two main fonts preloaded.
- ItemList structured data on brand pages.
Indexing itself is still controlled only by build.INDEX.
"""
import re, json, os, shutil, html
import build as B

MAX_TITLE = 60
SUFFIX = " | True Part Fabrication"

TITLE_OVERRIDES = {
    "": "True Part Fabrication | Custom & Replacement Parts, Modesto",
    "industries/warehouse-cold-storage/": "Custom Parts for Warehouses & Cold Storage | Modesto",
    "industries/industrial-shops/": "Jigs, Fixtures & Parts for Industrial Shops | Modesto",
    "industries/agriculture/": "Custom Parts for Farms & Ag Equipment | Modesto, CA",
    "industries/food-processing/": "Custom Parts for Food Processing Plants | Modesto, CA",
    "parts/": "Compatible Replacement Parts: DeWalt, Milwaukee, Ryobi",
    "tools/material-picker/": "Material Picker: PLA vs PETG vs ASA vs ABS vs Nylon",
    "tools/hose-size-finder/": "Shop Vac Hose Size Finder: Hoses & Dust Ports by Brand",
    "es/": "Piezas de repuesto y a medida en Modesto | True Part",
}
DESC_OVERRIDES = {
    "privacy/": "How True Part Fabrication handles the information you share: quote requests, part files, online payments through Stripe, and deletion requests.",
}

# Never indexed, never in sitemap.xml
NOINDEX = {"cart/", "order/success/", "order/cancelled/", "request-list/", "search/"}

# English page <-> Spanish page
HREFLANG = {"": "es/", "faq/": "es/preguntas-frecuentes/", "parts/": "es/piezas/"}

FONTS = [  # (file in package, family, style, weight range, stretch)
    ("fontsource-variable-instrument-sans", "instrument-sans-latin-wght-normal.woff2", "Instrument Sans", "normal", "400 700", None),
    ("fontsource-variable-archivo", "archivo-latin-wdth-normal.woff2", "Archivo", "normal", "100 900", "62% 125%"),
    ("fontsource-variable-jetbrains-mono", "jetbrains-mono-latin-wght-normal.woff2", "JetBrains Mono", "normal", "100 800", None),
    ("fontsource-instrument-serif", "instrument-serif-latin-400-normal.woff2", "Instrument Serif", "normal", "400", None),
    ("fontsource-instrument-serif", "instrument-serif-latin-400-italic.woff2", "Instrument Serif", "italic", "400", None),
]
PRELOAD = ["instrument-sans-latin-wght-normal.woff2", "archivo-latin-wdth-normal.woff2"]
FONT_SRC = "/home/claude/site_src/fonts"
RANGE = "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD"

def font_css():
    out = []
    for _, f, fam, style, wt, st in FONTS:
        out.append("@font-face{font-family:\"%s\";font-style:%s;font-weight:%s;%sfont-display:swap;src:url(fonts/%s) format(\"woff2\");unicode-range:%s}"
                   % (fam, style, wt, ("font-stretch:%s;" % st) if st else "", f, RANGE))
    return "\n".join(out) + "\n"

def copy_fonts(root):
    os.makedirs(root + "/assets/fonts", exist_ok=True)
    for _, f, *_r in FONTS:
        shutil.copy(os.path.join(FONT_SRC, f), root + "/assets/fonts/" + f)

def short_title(t):
    if len(t) <= MAX_TITLE:
        return t
    if t.endswith(SUFFIX) and len(t) - len(SUFFIX) <= MAX_TITLE:
        return t[:-len(SUFFIX)]
    s = t[:-len(SUFFIX)] if t.endswith(SUFFIX) else t
    s = re.sub(r"\s*\([^)]*\)", "", s)
    if len(s) <= MAX_TITLE:
        return s
    cut = s[:MAX_TITLE + 1].rsplit(" ", 1)[0].rstrip(" ,:;/-&|")
    return cut

def part_title(it):
    """Part number first: that's what people search for."""
    b, oem, n = it["b"], it["oem"], it["n"]
    ref = oem or it.get("for", "")
    lead = ref if ref.lower().startswith(b.lower()) else f"{b} {ref}"
    name = re.sub(r"\s*\([^)]*\)", "", n).strip()
    name = re.split(r":\s", name)[0]
    t = f"{lead} {name}"
    if len(t) <= MAX_TITLE - 13:
        t += " Replacement"
    if len(t) > MAX_TITLE:
        t = t[:MAX_TITLE + 1].rsplit(" ", 1)[0].rstrip(" ,:;/-&|")
        t = re.sub(r"\s+(w/|with|for|and|to|in\.?|of|the|a|&)$", "", t, flags=re.I)
    return t

def _path(h):
    m = re.search(r'<link rel="canonical" href="([^"]+)"', h)
    return m.group(1)[len(B.BASE) + 1:] if m else None

def post(h):
    path = _path(h)
    if path is None:
        return h
    # titles
    m = re.search(r"<title>(.*?)</title>", h, re.S)
    if m:
        full = html.unescape(m.group(1))
        new = TITLE_OVERRIDES.get(path) or short_title(full)
        if new != full:
            h = h.replace(m.group(0), "<title>" + html.escape(new, quote=False) + "</title>", 1)
    if path in DESC_OVERRIDES:
        d = html.escape(DESC_OVERRIDES[path])
        h = re.sub(r'(<meta (?:name="description"|property="og:description") content=")[^"]*"', lambda mm: mm.group(1) + d + '"', h)
    # utility pages: always noindex
    if path in NOINDEX:
        h = re.sub(r'<meta name="robots" content="[^"]*">', '<meta name="robots" content="noindex,follow">', h, 1)
    if path == "cart/":
        h = h.replace(f'<link rel="canonical" href="{B.BASE}/cart/">', f'<link rel="canonical" href="{B.BASE}/request-list/">')
    # hreflang: remove generic ones, add correct pairs where a translation exists
    h = re.sub(r'\n?<link rel="alternate" hreflang="[^"]+" href="[^"]*">', "", h)
    pair = None
    for en, es in HREFLANG.items():
        if path in (en, es):
            pair = (en, es)
    if pair:
        alt = (f'\n<link rel="alternate" hreflang="en" href="{B.BASE}/{pair[0]}">'
               f'\n<link rel="alternate" hreflang="es" href="{B.BASE}/{pair[1]}">'
               f'\n<link rel="alternate" hreflang="x-default" href="{B.BASE}/{pair[0]}">')
        h = h.replace('<link rel="canonical"', alt.lstrip("\n") + '\n<link rel="canonical"', 1)
    # fonts: self-hosted, preload the two main ones
    mm = re.search(r'href="([^"]*)site\.css', h)
    pre = mm.group(1) if mm else "assets/"
    pl = "".join(f'<link rel="preload" href="{pre}fonts/{f}" as="font" type="font/woff2" crossorigin>\n' for f in PRELOAD)
    h = re.sub(r'<link rel="preconnect" href="https://fonts\.googleapis\.com">\s*<link rel="preconnect" href="https://fonts\.gstatic\.com" crossorigin>\s*<link rel="stylesheet" href="https://fonts\.googleapis\.com/[^"]*">\n?', pl, h)
    # brand pages: list their parts as structured data
    if path.startswith("brands/") and path != "brands/":
        main = h[h.find('<main'):h.find('</main>')]
        seen, items = set(), []
        for href, name in re.findall(r'<a href="[^"]*?(parts/[a-z0-9-]+/)"[^>]*>([^<]+)</a>', main):
            if href not in seen:
                seen.add(href); items.append({"@type": "ListItem", "position": len(items) + 1, "url": f"{B.BASE}/{href}", "name": html.unescape(name)})
        if items:
            ld = {"@context": "https://schema.org", "@type": "ItemList", "name": html.unescape(re.sub(r"<[^>]+>", "", re.search(r"<h1[^>]*>(.*?)</h1>", h, re.S).group(1))).strip() if "<h1" in h else "Parts", "itemListElement": items}
            h = h.replace("</head>", B.ld(ld) + "\n</head>", 1)
    return h
