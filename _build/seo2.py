"""SEO rounds 3+ : more content, internal links and structured data.
Pages and helpers used by build.py / tools.py / parts_pages.py / extras.py.
"""
import re, html, json, collections
import build as B
esc = html.escape

KIND_PLURAL = {"adapter": ("adapter", "adapters"), "nozzle": ("nozzle or tool", "nozzles and tools"), "brush": ("brush", "brushes"),
               "separator": ("dust separator", "dust separators"), "clip": ("clip, cap or cover", "clips, caps and covers"), "roller": ("roller or wheel", "rollers and wheels")}

def _T():
    import tools as T
    return T

# ---------- sizes per part (from the hose table) ----------
_SIZES = None
def part_sizes():
    global _SIZES
    if _SIZES is None:
        T = _T(); _SIZES = {}
        for it in B.CAT["items"]:
            if not it["oem"]:
                continue
            for r in T.HOSE:
                if r["mc"].split(" / ")[0] == it["oem"] or r["m"] == it["oem"]:
                    _SIZES[it["slug"]] = r["s"]; break
    return _SIZES

# R6: same size from other brands
def same_size(c, it):
    S = part_sizes(); mine = set(S.get(it["slug"], []))
    if not mine:
        return ""
    picks = [x for x in B.CAT["items"] if x["b"] != it["b"] and x["i"] == it["i"] and mine & set(S.get(x["slug"], []))]
    seen_b, out = set(), []
    for x in picks:
        if x["b"] in seen_b:
            continue
        seen_b.add(x["b"]); out.append(x)
        if len(out) == 4:
            break
    if not out:
        return ""
    links = "".join(f'<a href="{c.link("parts/" + x["slug"] + "/")}">{esc(x["n"])}<span>{esc(B.rp(x))}</span></a>' for x in out)
    sz = ", ".join(sorted(mine))
    return f'<div class="head" style="margin:44px 0 22px"><div class="label">Same size ({esc(sz)}), other brands</div></div><div class="rel">{links}</div>'

# R4: richer, unique part descriptions (<=160)
def part_desc(it):
    ref = it["oem"] or it.get("for", "")
    lead = f"Compatible {it['b']} {ref} replacement: {it['n']}."
    if lead.lower().count(it["b"].lower()) > 1:
        lead = f"Compatible {ref} replacement: {it['n']}."
    S = part_sizes().get(it["slug"])
    tail = []
    if S:
        tail.append(f"{', '.join(S)}.")
    tail.append("Fit confirmed." if it["f"] else "We confirm fit first.")
    tail.append(f"Made in {it['mat'].split('/')[0].strip()} in Modesto, CA. Free reprint if it doesn't fit.")
    d = lead
    for t in tail:
        if len(d) + 1 + len(t) <= 160:
            d += " " + t
    if len(d) > 160:
        d = d[:157].rsplit(" ", 1)[0] + "…"
    return d

# R1: brand page extras
def brand_extra(c, b):
    T = _T()
    slug, cat, intro = T.BRANDS[b]
    items = [x for x in B.CAT["items"] if x["b"] == b]
    out = []
    if items:
        cnt = collections.Counter(x["i"] for x in items)
        parts = [f"{n} {KIND_PLURAL.get(k, (k, k + 's'))[0 if n == 1 else 1]}" for k, n in cnt.most_common()]
        fit = sum(1 for x in items if x["f"])
        out.append(f'<p>Our {esc(b)} list has {len(items)} parts: {esc(", ".join(parts[:-1]) + (" and " if len(parts) > 1 else "") + parts[-1])}. '
                   f'{fit} {"has" if fit == 1 else "have"} a confirmed fit for the listed models; for the rest, send your model number and we check before we make it.</p>')
    first = intro.split(". ")[0].rstrip(".") + "."
    q = [(f"What size hose do {b} vacuums use?" if b not in ("Samsung", "Hampton Bay") else f"Which {b} parts can you make?",
          f'{esc(first)} Look up a specific model in the <a href="{c.link("tools/hose-size-finder/")}?brand={esc(b).replace(" ", "%20")}">hose size finder</a>.' if b not in ("Samsung", "Hampton Bay")
          else f'{esc(first)} Browse the list above, or send a photo of the part you need.'),
         (f"Are these genuine {b} parts?", f'No. They are compatible <a href="{c.link("glossary/aftermarket-part/")}">aftermarket parts</a> that we design and make in Modesto, California, with a free reprint if one doesn\'t fit.'),
         (f"Can you make a {b} part that isn't listed?", f'Often, yes, if it\'s plastic and not safety-critical. Send the part or photos with a ruler and the model number. The <a href="{c.link("guides/how-to-measure-a-part/")}">measuring guide</a> shows what to send.')]
    dl = "".join(f"<dt>{esc(a)}</dt><dd>{bb}</dd>" for a, bb in q)
    return (f'<section class="about-part brand-faq" aria-labelledby="bfaq"><h2 id="bfaq">{esc(b)} parts: common questions</h2>' + "".join(out) + f'<dl class="pq">{dl}</dl></section>')

# R7: glossary term -> parts
GLOSS_KIND = {"roller": "roller", "clips-and-covers": "clip", "dust-port-hose-sizes": "adapter", "fit-types": "adapter"}
GLOSS_MAT = {"petg": "PETG", "tpu": "TPU", "asa": "ASA", "pa-cf": "PA-CF", "pla": "PLA", "abs": "ABS"}
def gloss_extra(c, t):
    s = t["slug"]
    if s in GLOSS_MAT:
        m = GLOSS_MAT[s]; items = [x for x in B.CAT["items"] if m in [p.strip() for p in x["mat"].split("/")]]
        head = f"Parts we make in {m}"
    elif s in GLOSS_KIND:
        k = GLOSS_KIND[s]; items = [x for x in B.CAT["items"] if x["i"] == k]
        head = f"Example {KIND_PLURAL[k][1]} in our catalog"
    else:
        return ""
    if not items:
        return ""
    items = sorted(items, key=lambda x: (not x["f"], x["b"]))
    seen, pick = set(), []
    for x in items:
        if x["b"] not in seen:
            seen.add(x["b"]); pick.append(x)
        if len(pick) == 6:
            break
    li = "".join(f'<li><a href="{c.link("parts/" + x["slug"] + "/")}">{esc(x["b"])} {esc(x["oem"] or x.get("for", ""))}: {esc(x["n"])}</a></li>' for x in pick)
    return f'<div class="box"><h2>{esc(head)}</h2><ul>{li}</ul><p style="margin-top:10px"><a href="{c.link("parts/")}">All {len(items)} in the parts catalog →</a></p></div>'

# R8: service -> extra related links
SERVICE_LINKS = {
    "replacement-parts": [("Parts catalog", "parts/"), ("Hose size finder", "tools/hose-size-finder/"), ("Shop vac hose sizes by brand", "guides/shop-vac-hose-sizes/"), ("Replacing a discontinued part", "guides/replacing-a-discontinued-plastic-part/"), ("DeWalt parts", "brands/dewalt/"), ("Milwaukee parts", "brands/milwaukee/"), ("RYOBI parts", "brands/ryobi/"), ("Shark parts", "brands/shark/")],
    "custom-fabrication": [("Industrial shops", "industries/industrial-shops/"), ("Agriculture", "industries/agriculture/"), ("Material picker", "tools/material-picker/"), ("How to measure a part", "guides/how-to-measure-a-part/")],
    "small-batch-manufacturing": [("Food processing", "industries/food-processing/"), ("Warehouse & cold storage", "industries/warehouse-cold-storage/"), ("Pricing", "pricing/"), ("Reorder a part", "reorder/")],
    "electronics-enclosures": [("Material picker", "tools/material-picker/"), ("Heat deflection temperature", "glossary/heat-deflection-temperature/"), ("UV resistance", "glossary/uv-resistance/"), ("Pricing", "pricing/")],
}
# R9: industry -> services and guides
IND_LINKS = {
    "food-processing": [("Custom fabrication", "services/custom-fabrication/"), ("Small-batch manufacturing", "services/small-batch-manufacturing/"), ("How to measure a part", "guides/how-to-measure-a-part/")],
    "agriculture": [("Replacement parts", "services/replacement-parts/"), ("Custom fabrication", "services/custom-fabrication/"), ("Replacing a discontinued part", "guides/replacing-a-discontinued-plastic-part/")],
    "warehouse-cold-storage": [("Custom fabrication", "services/custom-fabrication/"), ("Small-batch manufacturing", "services/small-batch-manufacturing/"), ("Material picker", "tools/material-picker/")],
    "industrial-shops": [("Custom fabrication", "services/custom-fabrication/"), ("Replacement parts", "services/replacement-parts/"), ("Adapter builder", "tools/adapter-builder/"), ("Shop vac hose sizes by brand", "guides/shop-vac-hose-sizes/")],
}
def links_strip(c, label, links, top=28):
    a = "".join(f'<a href="{c.link(p)}">{esc(t)}</a>' for t, p in links)
    return f'<div style="margin-top:{top}px"><div class="label" style="margin-bottom:14px">{esc(label)}</div><div class="terms-strip">{a}</div></div>'

# R10: footer brand column
def footer_brands(c):
    T = _T()
    li = "".join(f'<li><a href="{c.link("brands/" + s + "/")}">{esc(b)}</a></li>' for b, (s, *_) in list(T.BRANDS.items())[:9])
    return f'<div><h2 class="fh">Parts by brand</h2><ul>{li}<li><a href="{c.link("parts/")}">All brands</a></li></ul></div>'

# ---------- R11/R12: guides ----------
def _guide(c, path, title, h1, lead, sections, desc, crumb):
    T = _T()
    body_html = "".join(f'<h2 id="{sid}">{esc(h)}</h2>{content}' for sid, h, content in sections)
    toc = "".join(f'<li><a href="#{sid}">{esc(h)}</a></li>' for sid, h, _ in sections)
    body = f"""<main id="main">
{T.page_hero(c, [('Home',''),('Resources','resources/'),(crumb, path)], h1, esc(lead))}
<div class="wrap"><div class="prose guide" style="padding-block:40px 70px;max-width:760px">
  <nav aria-label="On this page" class="toc"><ol style="margin:0 0 28px;padding-left:20px;display:grid;gap:6px">{toc}</ol></nav>
  {body_html}
  <p style="color:var(--faint);font-size:.88rem;margin-top:36px">Published October 2026 by True Part Fabrication, Modesto, California.</p>
</div></div>
{T.cta(c)}
</main>"""
    art = {"@context": "https://schema.org", "@type": "Article", "headline": h1, "description": desc, "inLanguage": "en", "datePublished": "2026-10-31", "dateModified": "2026-10-31",
           "author": {"@id": B.BASE + "/#business"}, "publisher": {"@id": B.BASE + "/#business"}, "mainEntityOfPage": B.BASE + "/" + path,
           "image": B.BASE + "/assets/img/og-image.jpg"}
    return B.doc(c, B.head(c, title, desc, [art, B.crumbs_ld([("Home", ""), ("Resources", "resources/"), (crumb, path)])], og_type="article"), body)

def guide_hose_sizes(c):
    T = _T()
    by = collections.defaultdict(collections.Counter)
    for r in T.HOSE:
        if r["g"] in ("Vacuums & collectors", "Hoses"):
            for s in r["s"]:
                by[r["b"]][s] += 1
    def order(s):
        m = re.match(r"([\d\-/\.]+)\s*(in|mm)", s)
        if not m: return 999
        v = m.group(1)
        try:
            if "-" in v and "/" in v: w, f = v.split("-"); a, b2 = f.split("/"); val = int(w) + int(a) / int(b2)
            elif "/" in v: a, b2 = v.split("/"); val = int(a) / int(b2)
            else: val = float(v)
        except Exception: return 999
        return val * (1 if m.group(2) == "in" else 1 / 25.4)
    rows = ""
    for b, (slug, *_r) in T.BRANDS.items():
        if b not in by: continue
        sizes = sorted(by[b], key=order)
        rows += f'<tr><td><a href="{c.link("brands/" + slug + "/")}">{esc(b)}</a></td><td>{"".join(f"<span class=sz>{esc(s)}</span> " for s in sizes)}</td><td><a href="{c.link("tools/hose-size-finder/")}?brand={esc(b).replace(" ", "%20")}">Look up a model</a></td></tr>'
    n = len([r for r in T.HOSE if r["g"] in ("Vacuums & collectors", "Hoses")])
    sections = [
        ("three", "The three common sizes", f'<p>Most wet/dry vacuums use one of three nominal hose sizes: <b>1-1/4 inch</b> on small and handheld vacs, <b>1-7/8 inch</b> on mid-size vacs, and <b>2-1/2 inch</b> on large shop vacs. Woodworking dust collectors step up to <b>4 inch</b>. Some brands, especially for dust extractors and commercial vacuums, use metric sizes such as 32, 35, or 38 mm.</p><p>The size names are nominal. A "2-1/2 inch" hose does not measure exactly 2.5 inches anywhere, and actual cuff and port diameters differ between brands. That is why a "universal" adapter often fits loosely or not at all. See <a href="{c.link("glossary/dust-port-hose-sizes/")}">shop vac hose sizes</a> in the glossary.</p>'),
        ("brands", "Sizes by brand", f'<p>These are the vacuum and hose sizes in our size finder, which covers {n} vacs, collectors and hoses. Use the finder to check your exact model before buying an adapter or accessory.</p><div class="ftable"><table style="min-width:520px"><thead><tr><th>Brand</th><th>Hose and vac sizes listed</th><th><span class="sr-only">Size finder</span></th></tr></thead><tbody>{rows}</tbody></table></div>'),
        ("measure", "How to measure your hose or port", f'<p>Measure across the end with calipers if you have them, or a ruler with millimeter marks. For a hose cuff that slides into something, measure the outside. For a port that a hose slides over, measure the outside of the port; if the hose slides into it, measure the inside. Note whether the end is straight or tapered, and measure both ends of a taper. The <a href="{c.link("guides/how-to-measure-a-part/")}">measuring guide</a> walks through it with photos.</p>'),
        ("adapters", "Connecting two different sizes", f'<p>A step adapter has several diameters and can be cut down to fit, which works for a quick fix. A custom adapter is sized to the exact hose and port you own, so it fits snugly on both without tape. The <a href="{c.link("tools/adapter-builder/")}">adapter builder</a> lets you pick both ends and request one, and <a href="{c.link("glossary/fit-types/")}">fit types</a> explains slip and press fits.</p>'),
        ("parts", "Compatible parts by size", f'<p>Our <a href="{c.link("parts/")}">parts catalog</a> lists compatible adapters, nozzles, brushes, and separators by brand and part number, each with its connection size where we know it.</p>'),
    ]
    return _guide(c, "guides/shop-vac-hose-sizes/", "Shop Vac Hose Sizes by Brand: 1-1/4, 1-7/8, 2-1/2 in",
                  "Shop vac hose sizes by brand", "The common wet/dry vac hose sizes, what they actually measure, and which sizes each major brand uses, from our size finder data.",
                  sections, "Shop vac hose sizes explained: 1-1/4, 1-7/8, 2-1/2 and 4 inch, how to measure a hose or port, and the sizes DeWalt, Milwaukee, RYOBI, RIDGID and others use.", "Shop vac hose sizes")

def guide_discontinued(c):
    sections = [
        ("number", "1. Find the exact part number", '<p>Look for a number molded into the part, or find it in the parts diagram in the owner\'s manual or on the maker\'s website. Search with the equipment\'s model number, not just the brand. A part number is the fastest way to find a replacement, and it is the first thing a parts counter or a fabricator will ask for.</p>'),
        ("supersede", "2. Check for a newer replacement", '<p>Manufacturers often replace an old part number with a new one (a "superseded" part) that fits the same machine. A dealer or authorized parts distributor can look this up. If the part is only sold inside a large, expensive assembly, ask whether the small piece is sold separately.</p>'),
        ("used", "3. Look for used or surplus parts", f'<p>Online marketplaces, repair shops, and salvage dealers often have parts from retired machines. Check the part number and condition carefully. Our own <a href="{B.EBAY}" target="_blank" rel="noopener">eBay store</a> lists some ready-made parts.</p>'),
        ("aftermarket", "4. Consider a compatible aftermarket part", f'<p>An <a href="{{AM}}">aftermarket part</a> is made by another company to fit the same equipment. For plastic parts such as adapters, clips, covers, caps, nozzles, and rollers, a well-made aftermarket part can match the original and is sometimes stronger where the original failed. Browse our <a href="{{PARTS}}">compatible parts catalog</a> by brand or part number.</p>'),
        ("remake", "5. Have it remade from the original", '<p>When there is no replacement at all, a broken part can be measured and rebuilt in CAD, then made in a material suited to the job. This is called <a href="{RE}">reverse engineering</a>. Send the original part, even in pieces, or clear photos with a ruler in the frame and the equipment\'s model number. The <a href="{MEASURE}">measuring guide</a> shows what to send.</p>'),
        ("safety", "When not to replace it yourself", '<p>Some parts should only be replaced with genuine, certified parts: anything safety-critical, pressurized, load-bearing, electrical, or part of a braking or steering system, and anything that touches food or is used for medical or child-safety purposes. We don\'t make those parts. See <a href="{TERMS}">what we won\'t make</a>.</p>'),
    ]
    rep = {"{AM}": c.link("glossary/aftermarket-part/"), "{PARTS}": c.link("parts/"), "{RE}": c.link("glossary/reverse-engineering/"), "{MEASURE}": c.link("guides/how-to-measure-a-part/"), "{TERMS}": c.link("terms/") + "#t4"}
    fixed = []
    for sid, h, t in sections:
        t = t.replace("{{AM}}", "{AM}").replace("{{PARTS}}", "{PARTS}")
        for k, v in rep.items(): t = t.replace(k, v)
        fixed.append((sid, h, t))
    return _guide(c, "guides/replacing-a-discontinued-plastic-part/", "How to Replace a Discontinued Plastic Part: 5 Options",
                  "How to replace a discontinued plastic part", "Five ways to find or replace a plastic part the manufacturer no longer sells, from tracking the part number to having it remade.",
                  fixed, "Five ways to replace a discontinued plastic part: find the part number, check for a superseded part, buy used, use a compatible aftermarket part, or have it remade.", "Replacing a discontinued part")

GUIDES = [("guides/shop-vac-hose-sizes/", "Shop vac hose sizes by brand", "The common hose sizes, how to measure, and which sizes each brand uses.", guide_hose_sizes),
          ("guides/replacing-a-discontinued-plastic-part/", "Replacing a discontinued plastic part", "Five ways to find or replace a part the manufacturer no longer sells.", guide_discontinued)]

# R14: more FAQ entries
def extra_faqs(c):
    L = c.link
    return [
        ("Can you replace a discontinued plastic part?", f'<p>Usually, if it\'s plastic and not safety-critical. Send the original part, even broken, or photos with a ruler and the model number. We measure it, model it, and make a new one. See <a href="{L("guides/replacing-a-discontinued-plastic-part/")}">how to replace a discontinued part</a> for other options too.</p>'),
        ("Do you make shop vac and dust collection adapters?", f'<p>Yes. We make adapters between hose, wand, and dust port sizes, including 1-1/4, 1-7/8, 2-1/2, and 4 inch and common metric sizes. Look up your sizes in the <a href="{L("tools/hose-size-finder/")}">hose size finder</a> or request one with the <a href="{L("tools/adapter-builder/")}">adapter builder</a>.</p>'),
        ("What materials do you use?", f'<p>Mostly <a href="{L("glossary/petg/")}">PETG</a> for everyday parts, <a href="{L("glossary/asa/")}">ASA</a> for outdoor and hot spaces, <a href="{L("glossary/tpu/")}">TPU</a> for flexible parts, and carbon-fiber nylon for stiff, strong parts. The <a href="{L("tools/material-picker/")}">material picker</a> compares them.</p>'),
    ]

# R22: llms.txt
def llms_txt():
    T = _T()
    lines = ["# True Part Fabrication", "",
             "> True Part Fabrication LLC makes compatible aftermarket replacement parts, custom parts, and small production runs in Modesto, California. Opening January 1, 2027. Ships anywhere in the United States. Phone (209) 554-4800.", "",
             "Parts are plastic, made to order, and not genuine brand parts. We do not make safety-critical, pressurized, electrical, braking or steering, child-safety, medical, pool, code-compliance, or food-contact parts.", "",
             "## Main pages",
             f"- [Services]({B.BASE}/services/): replacement parts, custom fabrication, electronics enclosures, small-batch manufacturing",
             f"- [Compatible parts catalog]({B.BASE}/parts/): {len(B.CAT['items'])} parts by brand and part number",
             f"- [Pricing]({B.BASE}/pricing/): how quotes are priced",
             f"- [FAQ]({B.BASE}/faq/)",
             f"- [Terms of Service]({B.BASE}/terms/)", "", "## Tools and guides",
             f"- [Hose and dust port size finder]({B.BASE}/tools/hose-size-finder/)",
             f"- [Adapter builder]({B.BASE}/tools/adapter-builder/)",
             f"- [Material picker]({B.BASE}/tools/material-picker/)",
             f"- [Hose and port size chart, one page per model]({B.BASE}/sizes/)",
             f"- [Inch to mm converter]({B.BASE}/tools/inch-mm-converter/)",
             f"- [How to measure a part]({B.BASE}/guides/how-to-measure-a-part/)"]
    lines += [f"- [{t}]({B.BASE}/{p})" for p, t, _d, _f in GUIDES]
    lines += [f"- [Glossary]({B.BASE}/glossary/)", "", "## Parts by brand"]
    lines += [f"- [{b}]({B.BASE}/brands/{s}/)" for b, (s, *_) in T.BRANDS.items()]
    lines += ["", "## Spanish", f"- [Página en español]({B.BASE}/es/)", ""]
    return "\n".join(lines)

def pages():
    return {p: f for p, _t, _d, f in GUIDES}

CSS = """
.foot{grid-template-columns:1.2fr 1fr 1fr 1fr}
@media (max-width:900px){.foot{grid-template-columns:1fr 1fr}}
@media (max-width:560px){.foot{grid-template-columns:1fr}}
.guide h2{font-size:1.3rem;margin:36px 0 10px}
.guide p{color:var(--muted)}
.guide a{color:var(--ink)}
.guide .ftable{position:relative;overflow-x:auto;max-width:100%;-webkit-overflow-scrolling:touch}
.guide .ftable td a{color:var(--ink)}
.parts-top h2{font-size:1.1rem;font-stretch:115%;margin:0}
.h1sub{display:block;font:500 .78rem var(--f-mono);letter-spacing:.12em;text-transform:uppercase;color:var(--accent-hi);margin-top:12px}
"""
