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
    'industries/warehouse-cold-storage/': 'Scanner holsters, label holders, cable guides, organizers and bumpers made to fit your racks and carts, for warehouses and cold storage in the Central Valley.',
    'industries/industrial-shops/': 'Printed jigs, fixtures, brackets and dust collection fittings for machine shops, fabricators and maintenance teams in Modesto and the Central Valley.',
    'industries/agriculture/': 'Covers, clips, spacers, sensor mounts and cab organizers for growers, packers and equipment dealers in Stanislaus and San Joaquin counties.',
    'industries/food-processing/': 'Non-food-contact sensor mounts, guides, holders and changeover jigs for food processing plants in Modesto and the Central Valley. Made to order, fast.',
    'business/': 'Replacement and custom parts for food processing, agriculture, warehouses, cold storage and industrial shops in Modesto, Turlock, Stockton and nearby.',
    '': 'Replacement parts, custom brackets, jigs, fixtures and small-batch runs, designed and made in Modesto, CA, for businesses across the Central Valley.',
    'parts/': '@N made-to-order aftermarket parts for DeWalt, Milwaukee, RYOBI, RIDGID, WEN, Shark and more: adapters, nozzles, brushes and clips. Search by part number.',
    'guides/replacing-a-discontinued-plastic-part/': 'Five ways to replace a discontinued plastic part: find the part number, check for a newer one, buy used, go aftermarket, or have it remade.',
    'tools/material-picker/': 'Free material picker for custom parts. Compare PLA, PETG, ASA, ABS, carbon-fiber nylon and TPU for heat, sun, toughness and flexibility.',
    'about/': 'True Part Fabrication is a manufacturing company in Modesto, California, making replacement parts, custom components and small-batch runs.',
    'es/': 'Piezas de repuesto, soportes, plantillas y lotes pequeños hechos a medida en Modesto, CA, para negocios del Valle Central. Reimpresión gratis si no queda.',
    'es/piezas/': '@N piezas compatibles hechas a pedido para DeWalt, Milwaukee, RYOBI, Makita y más: adaptadores, boquillas, cepillos y clips. Hechas en Modesto, CA.',
    "privacy/": "How True Part Fabrication handles the information you share: quote requests, part files, online payments through Stripe, and deletion requests.",
}

# Never indexed, never in sitemap.xml
NOINDEX = {"my-shop/", "cart/", "order/success/", "order/cancelled/", "request-list/", "search/"}

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
    name = name[:1].upper() + name[1:]
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
    # one look (black): set it on <html> and serve the black images directly
    h = re.sub(r'<html lang="([a-z]+)"(?! data-tpf-theme)', r'<html lang="\1" data-tpf-theme="black"', h, 1)
    if "<html" not in h and "data-tpf-theme" not in h[:400]:
        h = '<script>document.documentElement.setAttribute("data-tpf-theme","black")</script>\n' + h
    def _img(m):
        tag = m.group(0); bl = re.search(r'data-black="([^"]*)"', tag)
        if bl:
            tag = re.sub(r'\ssrc="[^"]*"', ' src="' + bl.group(1) + '"', tag, 1)
        return re.sub(r'\sdata-(?:light|black|dark)="[^"]*"', '', tag)
    h = re.sub(r"<img\b[^>]*>", _img, h)
    # titles
    m = re.search(r"<title>(.*?)</title>", h, re.S)
    if m:
        full = html.unescape(m.group(1))
        new = TITLE_OVERRIDES.get(path) or short_title(full)
        if new != full:
            h = h.replace(m.group(0), "<title>" + html.escape(new, quote=False) + "</title>", 1)
    if path in DESC_OVERRIDES:
        d = html.escape(DESC_OVERRIDES[path].replace("@N", str(len(B.CAT["items"]))))
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
    # og:image per section (service renders are 1000x750)
    OGI = {"services/replacement-parts/": "svc-adapter", "services/custom-fabrication/": "svc-bracket", "services/electronics-enclosures/": "svc-enclosure",
           "services/small-batch-manufacturing/": "svc-batch", "industries/industrial-shops/": "svc-bracket", "industries/agriculture/": "svc-bracket",
           "industries/food-processing/": "svc-batch", "industries/warehouse-cold-storage/": "svc-batch", "tools/adapter-builder/": "svc-adapter",
           "tools/hose-size-finder/": "svc-adapter", "guides/shop-vac-hose-sizes/": "svc-adapter"}
    img = OGI.get(path) or ("svc-adapter" if path.startswith("brands/") else None)
    if img and 'og-image.jpg' in h:
        h = h.replace(f'<meta property="og:image" content="{B.BASE}/assets/img/og-image.jpg">', f'<meta property="og:image" content="{B.BASE}/assets/img/{img}.jpg">', 1)
        h = h.replace('<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">', '<meta property="og:image:width" content="1000"><meta property="og:image:height" content="750">', 1)
        h = re.sub(r'<meta property="og:image:alt" content="[^"]*">', '<meta property="og:image:alt" content="Rendering of a custom manufactured part">', h, 1)
    # LCP: on the home page the big logo is the first thing seen; header logo need not jump the queue
    if path in ("",):
        h = h.replace('<img class="hero-logo" src=', '<img class="hero-logo" fetchpriority="high" src=', 1)
        h = re.sub(r'(<a class="brand"[^>]*><img) fetchpriority="high"', r'\1', h, 1)
    # opening banner as a labelled landmark
    h = re.sub(r'<div class="opening" role="note"><div class="wrap">(.*?)</div></div>', lambda m: '<aside class="opening" aria-label="' + ('Apertura' if '<html lang="es"' in h else 'Opening') + '"><div class="wrap">' + m.group(1) + '</div></aside>', h, count=1, flags=re.S)
    # catalog: give the part rows (h3) a section heading
    if path in ("parts/", "es/piezas/") and 'id="plist-h"' not in h:
        lbl = "Lista de piezas" if path.startswith("es/") else "All parts"
        h = h.replace('<div class="list" id="plist"', f'<h2 id="plist-h" class="sr-only">{lbl}</h2>\n  <div class="list" id="plist"', 1)
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
    # share images: black versions
    h = re.sub(r'(<meta property="og:image" content="[^"]*/assets/img/(?:svc|sample)-[a-z]+)\.jpg"', r'\1-black.jpg"', h)
    # bookmark hint on tool pages that don't have one yet
    if path in ("tools/hose-size-finder/", "tools/material-picker/", "tools/adapter-builder/", "guides/how-to-measure-a-part/", "guides/shop-vac-hose-sizes/") and "data-bm-hint" not in h:
        i = h.find('<div class="page-hero">')
        if i > -1:
            j = h.find("</div></div>", i)
            if j > -1:
                h = h[:j] + __import__("bm").HINT + h[j:]
    # scrollable tables: give each region a unique name (from the heading before it)
    if h.count('aria-label="Scrollable table"') > 1:
        out, pos, n = [], 0, 0
        for m in re.finditer(r'aria-label="Scrollable table"', h):
            n += 1
            hd = re.findall(r"<h[23][^>]*>(.*?)</h[23]>", h[:m.start()], re.S)
            name = re.sub(r"<[^>]+>", "", hd[-1]).strip() if hd else ""
            out.append(h[pos:m.start()] + f'aria-label="{name + " table" if name else "Table " + str(n)}"'); pos = m.end()
        out.append(h[pos:]); h = "".join(out)
    # phone QR library only where the bookmark hint lives
    if "data-phone-qr" in h and "qrcode.min.js" not in h:
        mm2 = re.search(r'<script src="([^"]*)site\.js', h)
        if mm2:
            h = h.replace(mm2.group(0), f'<script src="{mm2.group(1)}qrcode.min.js" defer></script>\n' + mm2.group(0), 1)
    # light HTML minify: drop indentation and blank lines outside <pre>/<textarea>/<script>
    parts = re.split(r"(<script[\s\S]*?</script>|<textarea[\s\S]*?</textarea>|<pre[\s\S]*?</pre>)", h)
    h = "".join(p if p.startswith(("<script", "<textarea", "<pre")) else re.sub(r"\n[ \t]+", "\n", re.sub(r"\n\s*\n+", "\n", p)) for p in parts)
    return h

# ---------- unique copy for each part page ----------
KIND_COPY = {
    "adapter": ("What this part does", "An adapter joins two hoses, wands, tools or ports that don't connect on their own. This one is made to the same connection sizes as the {b} {ref}, so it fits where the original does."),
    "nozzle": ("What this part does", "A nozzle or tool attachment goes on the end of a wand or hose for a specific cleaning job. This one is made to the same connection as the {b} {ref}, so it attaches the way the original does."),
    "brush": ("What this part does", "A brush attachment goes on the end of a wand or hose for dusting and loosening debris. This one is made to the same connection as the {b} {ref}, so it attaches the way the original does."),
    "separator": ("What this part does", "Dust separators and collectors catch dust and debris before it reaches the vacuum, filter or work area. This one is made to the same fit as the {b} {ref}."),
    "clip": ("What this part does", "Clips, caps, covers and holders are small parts that crack, snap or get lost, and are often hard to buy on their own. This one is made to the same shape and fit as the {b} {ref}."),
    "roller": ("What this part does", "Rollers and wheels wear out or break long before the rest of the machine. This one is made to the same size and fit as the {b} {ref}."),
}
MAT_COPY = {
    "PETG": ("petg", "PETG is tough and slightly flexible, and it holds up to moisture and common cleaners, which makes it a good everyday material for vacuum and shop parts."),
    "TPU": ("tpu", "TPU is a flexible, rubber-like material. It grips, seals and bends without cracking."),
    "ASA": ("asa", "ASA resists sunlight and heat better than most plastics, so it suits parts used outdoors or in hot spaces."),
    "PA-CF": ("pa-cf", "PA-CF is nylon reinforced with carbon fiber. It is stiff and strong for parts that take load or wear."),
    "PLA": ("pla", "PLA is rigid and holds fine detail. It suits indoor parts that stay away from heat."),
    "ABS": ("abs", "ABS is tough and handles more heat than PLA, the same family of plastic many original parts are molded from."),
}

def part_about(c, it, sizes, kind_label):
    e = html.escape
    b, ref = it["b"], (it["oem"] or it.get("for", ""))
    head, txt = KIND_COPY.get(it["i"], ("What this part does", "This part is made to the same fit as the {b} {ref}."))
    out = [f'<h2>{head}</h2><p>{e(txt.format(b=b, ref=ref))}</p>']
    if it["f"]:
        out.append(f'<h2>Will it fit?</h2><p>Confirmed to fit: {e(it["f"])}. Not on the list? Send your model number with the request and we\'ll check before we make it.</p>')
    else:
        out.append(f'<h2>Will it fit?</h2><p>We haven\'t confirmed this part on a real {e(b)} machine yet. Send your model number, or a photo with a ruler, and we\'ll confirm the fit before we make it. Not sure how to measure? Use the <a href="{c.link("guides/how-to-measure-a-part/")}">measuring guide</a>.</p>')
    if sizes:
        out.append(f'<p>Connection size: {e(", ".join(sizes))} (see <a href="{c.link("glossary/dust-port-hose-sizes/")}">how hose and port sizes are measured</a>). Every {e(b)} hose, wand and port size we know is in the <a href="{c.link("tools/hose-size-finder/")}?brand={e(b).replace(" ", "%20")}">hose size finder</a>.</p>')
    if it["i"] == "adapter":
        out.append(f'<p>Need two sizes this part doesn\'t join? The <a href="{c.link("tools/adapter-builder/")}">adapter builder</a> makes one to order, and the guide to <a href="{c.link("glossary/fit-types/")}">fit types</a> explains slip-over versus slide-in ends.</p>')
    mats = [m.strip() for m in it["mat"].split("/")]
    mc = [MAT_COPY[m] for m in mats if m in MAT_COPY]
    if mc:
        sl, t = mc[0]
        out.append(f'<h2>Material</h2><p>Made in <a href="{c.link("glossary/" + sl + "/")}">{e(mats[0])}</a>. {e(t)}' + (f' Also available in {e(" or ".join(mats[1:]))}; tell us in your request.' if len(mats) > 1 else '') + f' Compare materials in the <a href="{c.link("tools/material-picker/")}">material picker</a>.</p>')
    out.append(f'<h2>Questions</h2><dl class="pq"><dt>Is this a genuine {e(b)} part?</dt><dd>No. It is a compatible <a href="{c.link("glossary/aftermarket-part/")}">aftermarket part</a> that we design and make in Modesto, California.</dd>'
               f'<dt>What if it doesn\'t fit?</dt><dd>Tell us within 30 days of delivery and we\'ll adjust it and make a new one at no charge. See the <a href="{c.link("terms/")}">Terms of Service</a>.</dd>'
               f'<dt>Can I order more than one?</dt><dd>Yes. Set a quantity in your <a href="{c.link("request-list/")}">cart</a>, or ask about <a href="{c.link("services/small-batch-manufacturing/")}">small-batch runs</a> for larger orders.</dd></dl>')
    return '<section class="about-part prose" aria-label="About this part">' + "".join(out) + '</section>'

PART_CSS = """
.about-part{max-width:760px;margin:10px 0 44px}
.about-part h2{font-size:1.15rem;margin:28px 0 8px}
.about-part p{margin:0 0 10px;color:var(--muted)}
.about-part a{color:var(--ink)}
.about-part .pq dt{font-weight:600;color:var(--ink);margin-top:14px}
.about-part .pq dd{margin:4px 0 0;color:var(--muted)}
.foot .fh{margin:0 0 14px;font:500 .68rem var(--f-mono);letter-spacing:.16em;text-transform:uppercase;color:var(--faint)}
"""
