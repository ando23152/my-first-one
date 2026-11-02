"""Bundles page (sets of parts that work together) and the one-page business flyer PDF."""
import html, json
import build as B
esc = html.escape

# Curated sets: parts from the same tool family or hose size. Only parts with a price are shown.
BUNDLES = [
    ("milwaukee-air-tip-detailing", "Milwaukee AIR-TIP detailing set",
     "Five AIR-TIP tools for corners, vents, seats and tight spots, all made for Milwaukee AIR-TIP hose sizes.",
     "Milwaukee", ["49-90-2028", "49-90-2027", "49-90-2032", "49-90-2034", "49-90-2021"]),
    ("milwaukee-dust-collection", "Milwaukee AIR-TIP drilling dust set",
     "Catch dust at the source: a wall suction funnel, a compact dust collector, and a bucket topper for overhead and wall drilling.",
     "Milwaukee", ["49-90-2022", "49-90-2044", "49-90-2041"]),
    ("milwaukee-2-1-2-floor", "Milwaukee 2-1/2 in. floor and wet set",
     "Floor brush, wet floor nozzle and two rocking utility nozzles for 2-1/2 in. Milwaukee hoses.",
     "Milwaukee", ["49-90-2002", "49-90-2005", "49-90-2039", "49-90-2040"]),
    ("milwaukee-automotive", "Milwaukee AIR-TIP automotive set",
     "The automotive kit plus a detail brush and a long-reach crevice tool, for full interior cleanups.",
     "Milwaukee", ["49-90-2019A", "49-90-2043", "49-90-2030Y"]),
    ("ridgid-2-1-2-locking", "RIDGID 2-1/2 in. locking floor set",
     "Locking floor brush and wet nozzle for RIDGID 2-1/2 in. locking hoses.",
     "RIDGID", ["LA2514", "LA2510"]),
    ("ridgid-1-7-8-starter", "RIDGID 1-7/8 in. starter set",
     "Crevice/dusting combo, floor brush and claw nozzle for RIDGID 1-7/8 in. vacs.",
     "RIDGID", ["VT1712", "VT1714", "VT2540"]),
    ("shark-fj140-tools", "Shark FJ140 tool set",
     "Crevice tool, upholstery tool, pet multi-tool and under-appliance wand from the same Shark FJ140 tool family.",
     "Shark", ["619FJ140", "627FJ140", "629FJ140", "632FJ140"]),
    ("samsung-jet-tools", "Samsung Jet stick tool set",
     "Combination tool, flex tool and crevice tool for Samsung Jet stick vacuums.",
     "Samsung", ["VCA-SAD95/AA", "VCA-SAF95/VAA", "DJ98-01130A"]),
    ("samsung-freezer-caps", "Samsung freezer handle end caps (left + right)",
     "Both freezer door handle end caps, so the pair matches.",
     "Samsung", ["DA67-02291A", "DA67-02292A"]),
    ("dewalt-wet-dry", "DeWalt wet/dry vac upgrade set",
     "The car cleaning kit plus a dust separator that keeps the filter clean, for DeWalt DXV-series vacs.",
     "DeWalt", ["DXVA13-0801", "DXVCS001"]),
]

def bundles():
    by = {(x["b"], x["oem"]): x for x in B.CAT["items"] if x.get("oem")}
    out = []
    for bid, name, blurb, brand, oems in BUNDLES:
        parts = [by[(brand, o)] for o in oems if (brand, o) in by and by[(brand, o)].get("price")]
        if len(parts) >= 2:
            out.append(dict(id=bid, name=name, blurb=blurb, brand=brand, parts=parts, total=round(sum(p["price"] for p in parts), 2)))
    return out

def page(c):
    cards = []
    for bd in bundles():
        rows = "".join(f'<li><a href="{c.link("parts/" + p["slug"] + "/")}">{esc(p["n"])}</a><span class="bd-ref">{esc(B.rp(p))}</span><span class="bd-p">${p["price"]:.2f}</span>'
                       f'{"" if p["f"] else "<span class=fitbadge>Fit to confirm</span>"}</li>' for p in bd["parts"])
        texts = json.dumps([B.part_text(p) for p in bd["parts"]])
        cards.append(f"""<article class="bd" id="{bd['id']}">
  <h2>{esc(bd['name'])}</h2>
  <p>{esc(bd['blurb'])}</p>
  <ul class="bd-list">{rows}</ul>
  <div class="bd-foot"><div class="bd-total"><span>{len(bd['parts'])} parts, bought separately</span><b>${bd['total']:.2f}</b><small>One order, one shipping charge.</small></div>
  <button type="button" class="btn" data-add-all="{esc(texts)}">Add the set to my cart</button></div>
</article>""")
    body = f"""<main id="main">
<div class="page-hero"><div class="wrap">
  {B.crumbs(c, [('Home', ''), ('Compatible parts', 'parts/'), ('Sets', 'bundles/')])}
  <h1>Part sets</h1>
  <p class="lead">Parts that work together, grouped by tool family and hose size. Add a whole set to your cart in one click and it ships as one order, with one shipping charge. Each part is made to order in Modesto, CA, with our free-reprint fit guarantee.</p>
</div></div>
<div class="wrap" style="padding-block:30px 80px">
  <div class="bd-grid">{''.join(cards)}</div>
  <p class="note" style="margin-top:30px">Need a set that isn't here, or the same tools in a different size? <a href="{c.link('', 'quote')}">Ask for a quote</a> and list the parts. Parts marked "Fit to confirm" are checked against your model before we print.</p>
  <div id="bd-live" role="status" class="sr-only"></div>
</div>
</main>
<script>document.addEventListener('click',function(e){{var b=e.target.closest('[data-add-all]');if(!b)return;var T=JSON.parse(b.getAttribute('data-add-all')),L;try{{L=JSON.parse(localStorage.getItem('tpf-list')||'[]')}}catch(x){{L=[]}}
var n=0;T.forEach(function(t){{if(!L.some(function(x){{return x.t===t}})){{L.push({{t:t,q:1}});n++}}}});try{{localStorage.setItem('tpf-list',JSON.stringify(L))}}catch(x){{}}
var p=document.getElementById('list-pill'),c=document.getElementById('list-n');if(p)p.hidden=!L.length;if(c)c.textContent=L.length;document.dispatchEvent(new CustomEvent('tpf-list'));
b.textContent='✓ Set added to your cart';var lv=document.getElementById('bd-live');if(lv)lv.textContent=n?n+' parts added to your cart.':'These parts are already in your cart.'}});</script>"""
    ld = [B.crumbs_ld([("Home", ""), ("Compatible parts", "parts/"), ("Sets", "bundles/")]),
          {"@context": "https://schema.org", "@type": "ItemList", "name": "Part sets",
           "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": bd["name"], "url": B.BASE + "/bundles/#" + bd["id"]} for i, bd in enumerate(bundles())]}]
    return B.doc(c, B.head(c, "Part Sets: Vacuum Tool Bundles by Brand | True Part Fabrication",
                           "Sets of compatible vacuum tools and attachments for Milwaukee, RIDGID, Shark, Samsung and DeWalt, grouped by tool family. One order, one shipping charge.", ld), body)

def pages():
    return {"bundles/": page}

CSS = """
.bd-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:20px}
.bd{border:1px solid var(--line);border-radius:14px;padding:22px;background:var(--panel,rgba(255,255,255,.03));display:flex;flex-direction:column}
.bd h2{font-size:1.15rem;margin:0 0 6px}
.bd>p{color:var(--muted);margin:0 0 14px;font-size:.95rem}
.bd-list{list-style:none;margin:0 0 16px;padding:0;display:grid;gap:8px}
.bd-list li{display:grid;grid-template-columns:1fr auto;gap:2px 12px;padding:8px 0;border-bottom:1px solid var(--line)}
.bd-list .bd-ref{grid-column:1;color:var(--faint);font-size:.82rem}
.bd-list .bd-p{grid-column:2;grid-row:1;font-family:var(--f-mono);font-size:.9rem}
.bd-list .fitbadge{grid-column:1}
.bd-foot{margin-top:auto;display:flex;flex-wrap:wrap;gap:12px;align-items:flex-end;justify-content:space-between}
.bd-total{display:grid}
.bd-total span{color:var(--faint);font-size:.82rem}
.bd-total b{font:600 1.35rem var(--f-body)}
.bd-total small{color:var(--faint);font-size:.8rem}
.sr-only{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}
@media (max-width:520px){.bd-grid{grid-template-columns:1fr}}
"""

def make_flyer(root):
    """One-page letter-size flyer for businesses (prints in black and white or color)."""
    import os
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas
    from reportlab.lib.colors import HexColor, white
    os.makedirs(root + "/assets/downloads", exist_ok=True)
    RED, INK, MUTED, LINE = HexColor("#B3261E"), HexColor("#111111"), HexColor("#555555"), HexColor("#DDDDDD")
    W, H = letter
    cv = canvas.Canvas(root + "/assets/downloads/TPF-business-flyer.pdf", pagesize=letter)
    cv.setTitle("True Part Fabrication: parts that keep the line running"); cv.setAuthor("True Part Fabrication LLC")
    # header band
    cv.setFillColor(INK); cv.rect(0, H - 1.55 * inch, W, 1.55 * inch, fill=1, stroke=0)
    logo = os.path.join(root, "assets/img/logo-black.png")
    if os.path.exists(logo):
        cv.drawImage(logo, 0.6 * inch, H - 1.35 * inch, width=1.15 * inch, height=1.15 * inch, preserveAspectRatio=True, mask="auto")
    cv.setFillColor(white); cv.setFont("Helvetica-Bold", 24); cv.drawString(1.95 * inch, H - 0.8 * inch, "True Part Fabrication")
    cv.setFont("Helvetica", 12); cv.drawString(1.95 * inch, H - 1.08 * inch, "Custom and replacement parts, manufactured in Modesto, CA")
    cv.setFillColor(RED); cv.rect(0, H - 1.62 * inch, W, 0.07 * inch, fill=1, stroke=0)
    y = H - 2.2 * inch
    cv.setFillColor(INK); cv.setFont("Helvetica-Bold", 20); cv.drawString(0.6 * inch, y, "Parts that keep the line running.")
    y -= 0.32 * inch
    cv.setFont("Helvetica", 11.5); cv.setFillColor(MUTED)
    for line in ["When a plastic part breaks and the replacement is backordered, discontinued, or sold",
                 "only in a 500-pack, we model it and make it. No molds, no large minimums."]:
        cv.drawString(0.6 * inch, y, line); y -= 0.2 * inch
    # two columns
    y -= 0.2 * inch; top = y
    def col(x, title, items):
        yy = top
        cv.setFillColor(RED); cv.setFont("Helvetica-Bold", 10); cv.drawString(x, yy, title.upper()); yy -= 0.26 * inch
        for head, sub in items:
            cv.setFillColor(INK); cv.setFont("Helvetica-Bold", 11.5); cv.drawString(x, yy, head); yy -= 0.18 * inch
            cv.setFillColor(MUTED); cv.setFont("Helvetica", 10)
            for s in sub: cv.drawString(x, yy, s); yy -= 0.16 * inch
            yy -= 0.1 * inch
        return yy
    a = col(0.6 * inch, "What we make", [
        ("Replacement parts", ["Discontinued, backordered or hard-to-find plastic parts,", "measured and reverse-engineered."]),
        ("Jigs and fixtures", ["Drilling guides, holders and alignment aids", "built to your drawings or a sample."]),
        ("Small-batch production", ["10 to 500 brackets, clips, covers or enclosures", "without paying for a mold."]),
        ("Dust collection fittings", ["Adapters and fittings for shop vacs,", "extractors and collectors."])])
    b = col(4.3 * inch, "Who we work with", [
        ("Food processing", ["Brackets, guides and line-side holders.", "Non-food-contact parts only."]),
        ("Agriculture", ["Equipment clips, covers, spacers and mounts."]),
        ("Warehouse and cold storage", ["Label holders, scanner mounts, cable guides."]),
        ("Industrial shops", ["Jigs, fixtures and workflow aids."])])
    y = min(a, b) - 0.1 * inch
    cv.setStrokeColor(LINE); cv.line(0.6 * inch, y, W - 0.6 * inch, y); y -= 0.32 * inch
    cv.setFillColor(RED); cv.setFont("Helvetica-Bold", 10); cv.drawString(0.6 * inch, y, "HOW IT WORKS"); y -= 0.26 * inch
    steps = [("1", "Send a photo or the part", "plus the machine's model number."),
             ("2", "Get a written quote", "with material, price and turnaround."),
             ("3", "We make it and test the fit", "then ship it or you pick it up.")]
    x = 0.6 * inch
    for n, h1, h2 in steps:
        cv.setFillColor(RED); cv.circle(x + 0.14 * inch, y - 0.02 * inch, 0.14 * inch, fill=1, stroke=0)
        cv.setFillColor(white); cv.setFont("Helvetica-Bold", 10); cv.drawCentredString(x + 0.14 * inch, y - 0.06 * inch, n)
        cv.setFillColor(INK); cv.setFont("Helvetica-Bold", 10); cv.drawString(x + 0.38 * inch, y, h1)
        cv.setFillColor(MUTED); cv.setFont("Helvetica", 9.5); cv.drawString(x + 0.38 * inch, y - 0.17 * inch, h2)
        x += 2.45 * inch
    y -= 0.62 * inch
    cv.setStrokeColor(LINE); cv.line(0.6 * inch, y, W - 0.6 * inch, y); y -= 0.32 * inch
    cv.setFillColor(RED); cv.setFont("Helvetica-Bold", 10); cv.drawString(0.6 * inch, y, "WHY US"); y -= 0.24 * inch
    why = ["Free reprint if a part doesn't fit.", "On-site measuring in the Modesto–Stockton corridor.",
           "Your part's model stays on file, so reorders take one message.", "Typical business job: $75 to $800+, quoted in writing first."]
    cv.setFillColor(INK); cv.setFont("Helvetica", 10.5)
    for w_ in why:
        cv.drawString(0.75 * inch, y, "•  " + w_); y -= 0.2 * inch
    # contact band
    cv.setFillColor(INK); cv.rect(0, 0, W, 1.25 * inch, fill=1, stroke=0)
    cv.setFillColor(RED); cv.rect(0, 1.25 * inch, W, 0.06 * inch, fill=1, stroke=0)
    cv.setFillColor(white); cv.setFont("Helvetica-Bold", 15); cv.drawString(0.6 * inch, 0.82 * inch, "Call (209) 554-4800")
    cv.setFont("Helvetica", 11); cv.drawString(0.6 * inch, 0.56 * inch, "Email ando23152@gmail.com")
    cv.drawString(0.6 * inch, 0.34 * inch, B.BASE.replace("https://", ""))
    cv.setFont("Helvetica", 9.5); cv.drawRightString(W - 0.6 * inch, 0.82 * inch, "Modesto · Ceres · Turlock · Manteca · Tracy · Stockton")
    cv.drawRightString(W - 0.6 * inch, 0.6 * inch, "Ships anywhere in the US")
    cv.drawRightString(W - 0.6 * inch, 0.38 * inch, "Opening January 1, 2027")
    cv.showPage(); cv.save()
