"""25 rounds: be the shop's reference. Size hubs, will-it-fit, cross-links, downloads, what's new, feed."""
import re, html, json, collections, datetime
from urllib.parse import quote
import build as B
esc = html.escape

def _bm():
    import bm
    return bm

def _T():
    import tools as T
    return T

def size_slug(s): return re.sub(r"[^a-z0-9]+", "-", s.lower().replace("/", "-")).strip("-")
def size_url(s): return "sizes/by-size/" + size_slug(s) + "/"

def all_items():
    """Every row in the size data, linked to its model page or, for accessories we make, its part page."""
    bm = _bm(); T = _T()
    oem = {x["oem"]: x for x in B.CAT["items"] if x["oem"]}
    pages = {(r["b"], r["mc"]): bm.model_url(r) for r in bm.rows()}
    out = []
    for r in T.HOSE:
        u = pages.get((r["b"], r["mc"]))
        if not u:
            p = oem.get(r["mc"].split(" / ")[0])
            if p: u = "parts/" + p["slug"] + "/"
        if u:
            out.append({"b": r["b"], "m": r["mc"], "d": r["d"], "s": r["s"], "g": r["g"], "c": r["conf"] or "", "u": u})
    return out

def sizes_used():
    cnt = collections.Counter(s for r in _T().HOSE for s in r["s"])
    order = {s: i for i, s in enumerate(_T().SIZE_ORDER)}
    return sorted([s for s, n in cnt.items() if n >= 2], key=lambda s: order.get(s, 99))

# ---------- R2: one hub page per size ----------
def size_hub(c, s):
    import seo2
    T = _T(); bm = _bm(); path = size_url(s)
    items = [x for x in all_items() if s in x["s"]]
    groups = collections.OrderedDict((g, []) for g in ["Vacuums & collectors", "Hoses", "Power tool ports", "Accessories"])
    for x in items: groups.setdefault(x["g"], []).append(x)
    S = seo2.part_sizes()
    parts = [p for p in B.CAT["items"] if s in S.get(p["slug"], [])]
    mm = B.MM.get(s, "")
    secs = ""
    for g, xs in groups.items():
        if not xs: continue
        li = "".join(f'<li><a href="{c.link(x["u"])}">{esc(x["b"])} {esc(x["m"])}</a> <span>{esc(x["d"])}</span></li>' for x in sorted(xs, key=lambda x: (x["b"], x["m"])))
        secs += f'<h2>{esc(g)} <small>({len(xs)})</small></h2><ul class="hub-list">{li}</ul>'
    pl = "".join(f'<a href="{c.link("parts/" + p["slug"] + "/")}">{esc(p["n"])}<span>{esc(B.rp(p))}</span></a>' for p in sorted(parts, key=lambda p: (not p["f"], p["b"]))[:12])
    others = "".join(f'<a href="{c.link(size_url(x))}">{esc(x)}</a>' for x in sizes_used() if x != s)
    brands = sorted({x["b"] for x in items})
    lead = (f'Everything in our size data that uses {s}' + (f' ({mm})' if mm else '') + f': {len(items)} vacs, hoses, ports and accessories from {", ".join(brands[:-1]) + (" and " if len(brands) > 1 else "") + brands[-1]}. '
            'Nominal sizes are names, not exact measurements, and brand locking ends may not lock together, so check fit before you buy.')
    body = f"""<main id="main">
<div class="page-hero"><div class="wrap">
  {B.crumbs(c, [('Home', ''), ('Size chart', 'sizes/'), (s, path)])}
  <h1>Everything that uses {esc(s)}<span class="h1sub">{esc(mm)}</span></h1>
  <p class="lead">{esc(lead)}</p>
</div></div>
<div class="wrap hub" style="padding-block:30px 80px">
  <div class="acts2"><button type="button" class="tbtn" data-print>Print this list</button><a class="tbtn" href="{c.link('tools/will-it-fit/')}">Will it fit?</a><a class="tbtn" href="{c.link('tools/adapter-builder/')}?a={quote(s)}">Adapter from {esc(s)}</a></div>
  {bm.HINT}
  {secs}
  {f'<h2>Our parts in {esc(s)}</h2><div class="rel">{pl}</div>' if pl else ''}
  <h2>Other sizes</h2><div class="terms-strip">{others}</div>
</div>
</main>"""
    il = {"@context": "https://schema.org", "@type": "ItemList", "name": f"Equipment that uses {s}", "numberOfItems": len(items),
          "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": B.BASE + "/" + x["u"], "name": f'{x["b"]} {x["m"]}'} for i, x in enumerate(items[:100])]}
    return B.doc(c, B.head(c, f"{s} Shop Vac Hoses, Ports & Accessories | True Part Fabrication",
                           f"Every vac, hose, dust port and accessory in our size data that uses {s}" + (f" ({mm})" if mm else "") + f": {len(items)} items by type and brand, plus parts and adapters.",
                           [il, B.crumbs_ld([("Home", ""), ("Size chart", "sizes/"), (s, path)])]), body)

# ---------- R3: same size, other brands (for model pages) ----------
def same_size_models(c, r):
    s = set(r["s"]); xs = [x for x in all_items() if x["b"] != r["b"] and s & set(x["s"]) and x["g"] == r["g"]]
    seen, out = set(), []
    for x in xs:
        if x["b"] in seen: continue
        seen.add(x["b"]); out.append(x)
        if len(out) == 6: break
    if not out: return ""
    links = "".join(f'<a href="{c.link(x["u"])}">{esc(x["b"])} {esc(x["m"])}<span>{esc(", ".join(x["s"]))}</span></a>' for x in out)
    hubs = " ".join(f'<a href="{c.link(size_url(z))}">all {esc(z)}</a>' for z in r["s"] if z in sizes_used())
    return f'<div class="head" style="margin:40px 0 22px"><div class="label">Same size, other brands</div></div><div class="rel">{links}</div>' + (f'<p style="margin-top:10px;color:var(--muted)">See {hubs}.</p>' if hubs else "")

# ---------- R4: part page -> models with that size ----------
def part_fits(c, it):
    import seo2
    S = seo2.part_sizes().get(it["slug"])
    if not S: return ""
    xs = [x for x in all_items() if x["b"] == it["b"] and set(S) & set(x["s"]) and x["g"] in ("Vacuums & collectors", "Hoses", "Power tool ports")][:8]
    links = "".join(f'<a href="{c.link(x["u"])}">{esc(x["b"])} {esc(x["m"])}</a>' for x in xs)
    hubs = "".join(f'<a href="{c.link(size_url(z))}">Everything in {esc(z)}</a>' for z in S if z in sizes_used())
    w = (f'<div class="fitcheck" data-fitcheck data-root="{c.link("")}" data-sizes="{esc("|".join(S))}" data-models="{c.asset("models.json")}">'
         f'<label for="fc-{it["slug"][:20]}">Check your model</label><div class="fc-row"><input id="fc-{it["slug"][:20]}" list="fc-dl" placeholder="e.g. WD4070" autocomplete="off"><button type="button" class="tbtn">Check</button></div>'
         f'<datalist id="fc-dl"></datalist><p class="fc-out" role="status" aria-live="polite"></p></div>')
    out = '<section class="about-part prose" style="margin-top:0"><h2>Which machines use this size?</h2>' + w
    if links: out += f'<p style="margin-top:14px">{esc(it["b"])} models in our size data with this size:</p><div class="terms-strip">{links}</div>'
    if hubs: out += f'<div class="terms-strip" style="margin-top:10px">{hubs}</div>'
    return out + "</section>"

# ---------- R5: will it fit? ----------
def will_it_fit(c):
    bm = _bm()
    body = f"""<main id="main">
<div class="page-hero"><div class="wrap">
  {B.crumbs(c, [('Home', ''), ('Resources', 'resources/'), ('Will it fit?', 'tools/will-it-fit/')])}
  <h1>Will it fit?</h1>
  <p class="lead">Pick two things you want to connect: a vac, hose, tool port or accessory. We compare their sizes from our size data and tell you whether they should connect directly or need an adapter.</p>
</div></div>
<div class="wrap" style="padding-block:34px 80px">
  {bm.HINT}
  <form class="xform wif" id="wif" data-nodraft onsubmit="return false" data-root="{c.link('')}" data-models="{c.asset('models.json')}">
    <label for="wif-a">First item (model number)<input id="wif-a" list="wif-dl" placeholder="e.g. WD4070" autocomplete="off"></label>
    <label for="wif-b">Second item (model number)<input id="wif-b" list="wif-dl" placeholder="e.g. DCA016" autocomplete="off"></label>
    <datalist id="wif-dl"></datalist>
    <div class="full"><button class="btn" type="button" id="wif-go">Compare <span class="ar">→</span></button></div>
    <div class="full wif-out" id="wif-out" role="status" aria-live="polite"></div>
  </form>
  <section class="about-part prose" style="margin-top:30px;padding:0"><h2>How to read the answer</h2>
  <p><b>Same nominal size</b> means both are listed at the same size, so they usually connect. Brand locking ends (Lock-On, Pos-I-Lock and similar) may not lock to another brand's fitting, and friction fits can be loose. <b>Different sizes</b> means you need an adapter; the button opens the <a href="{c.link('tools/adapter-builder/')}">adapter builder</a> with both sizes filled in.</p>
  <p>Not in the list? Measure both ends with the <a href="{c.link('tools/inch-mm-converter/')}">inch–mm converter</a> handy, or look it up in the <a href="{c.link('tools/hose-size-finder/')}">hose size finder</a>.</p></section>
</div>
</main>
<script>
(function(){{
  var f=document.getElementById('wif'),out=document.getElementById('wif-out'),R=f.getAttribute('data-root'),M=null;
  function load(cb){{if(M)return cb();fetch(f.getAttribute('data-models')).then(function(r){{return r.json()}}).then(function(j){{M=j;var dl=document.getElementById('wif-dl');M.forEach(function(x){{var o=document.createElement('option');o.value=x.b+' '+x.m;o.label=x.d;dl.appendChild(o)}});cb()}}).catch(function(){{out.textContent='Could not load the size list. Try again.'}})}}
  function find(q){{q=q.trim().toLowerCase().replace(/\\s+/g,' ');if(!q)return null;var e=M.filter(function(x){{var n=(x.b+' '+x.m).toLowerCase();return n===q||x.m.toLowerCase()===q}});if(e.length)return e[0];var p=M.filter(function(x){{return (x.b+' '+x.m+' '+x.d).toLowerCase().indexOf(q)>-1}});return p[0]||null}}
  function a(h,t){{var e=document.createElement('a');e.href=h;e.textContent=t;return e}}
  function go(){{load(function(){{var A=find(document.getElementById('wif-a').value),Bb=find(document.getElementById('wif-b').value);out.textContent='';
    if(!A||!Bb){{out.textContent=!A?'First item not found. Try just the model number.':'Second item not found. Try just the model number.';return}}
    var same=A.s.filter(function(s){{return Bb.s.indexOf(s)>-1}}),p=document.createElement('p'),b=document.createElement('b');
    if(same.length){{b.textContent='Same nominal size: '+same.join(', ')+'.';p.appendChild(b);p.appendChild(document.createTextNode(' They usually connect directly. If one end locks and the other is a different brand, or the fit is loose, a custom adapter fixes it.'))}}
    else{{b.textContent='Different sizes: '+A.s.join(' / ')+' and '+Bb.s.join(' / ')+'.';p.appendChild(b);p.appendChild(document.createTextNode(' You need an adapter. '));var l=a(R+'tools/adapter-builder/?a='+encodeURIComponent(A.s[0])+'&b='+encodeURIComponent(Bb.s[0])+'&am='+encodeURIComponent(A.b+' '+A.m),'Build this adapter →');l.className='btn';l.style.marginTop='10px';p.appendChild(document.createElement('br'));p.appendChild(l)}}
    out.appendChild(p);var d=document.createElement('p');d.style.color='var(--muted)';d.appendChild(document.createTextNode('Details: '));d.appendChild(a(R+A.u,A.b+' '+A.m));d.appendChild(document.createTextNode(' ('+A.c+') · '));d.appendChild(a(R+Bb.u,Bb.b+' '+Bb.m));d.appendChild(document.createTextNode(' ('+Bb.c+')'));out.appendChild(d);
    try{{history.replaceState(null,'','?a='+encodeURIComponent(A.b+' '+A.m)+'&b='+encodeURIComponent(Bb.b+' '+Bb.m))}}catch(e){{}}}})}}
  document.getElementById('wif-go').addEventListener('click',go);
  ['wif-a','wif-b'].forEach(function(id){{var i=document.getElementById(id);i.addEventListener('focus',function(){{load(function(){{}})}});i.addEventListener('keydown',function(e){{if(e.key==='Enter'){{e.preventDefault();go()}}}})}});
  var P=new URLSearchParams(location.search);if(P.get('a')&&P.get('b')){{document.getElementById('wif-a').value=P.get('a');document.getElementById('wif-b').value=P.get('b');go()}}
}})();
</script>"""
    app = {"@context": "https://schema.org", "@type": "WebApplication", "name": "Will it fit? Shop vac hose and port compatibility checker", "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}, "url": B.BASE + "/tools/will-it-fit/"}
    return B.doc(c, B.head(c, "Will It Fit? Shop Vac Hose & Port Compatibility Checker | True Part Fabrication",
                           "Pick a vac, hose, tool port or accessory and a second item. See whether they share a hose size or need an adapter, using our size data for hundreds of models.",
                           [app, B.crumbs_ld([("Home", ""), ("Resources", "resources/"), ("Will it fit?", "tools/will-it-fit/")])]), body)

# ---------- R8: brand page -> model pages ----------
def brand_models(c, b):
    bm = _bm(); xs = [r for r in bm.rows() if r["b"] == b]
    if not xs: return ""
    links = "".join(f'<a href="{c.link(bm.model_url(r))}">{esc(r["mc"])}</a>' for r in xs)
    return f'<div style="margin-top:44px"><div class="head" style="margin-bottom:14px"><div class="label">{esc(b)} size pages</div></div><div class="terms-strip">{links}</div></div>'

# ---------- R11: glossary additions ----------
NEW_TERMS = [
 {"slug": "od-and-id", "term": "OD and ID (outside and inside diameter)", "cat": "Fit", "short": "Outside diameter is measured across the outside of a tube or cuff; inside diameter across the opening.",
  "body": ["OD (outside diameter) is the distance across the outside of a hose cuff, port or tube. ID (inside diameter) is the distance across the hole.", "Which one matters depends on how two parts join. If a cuff slides into a port, the cuff's OD has to match the port's ID. If a cuff slides over a port, the cuff's ID has to match the port's OD.", "Calipers measure both: the outside jaws for OD and the small inside jaws for ID."],
  "quote": "Tell us whether each end slides into or over the other part, with the OD or ID you measured.", "related": ["fit-types", "tolerance", "dust-port-hose-sizes"]},
 {"slug": "friction-fit", "term": "Friction fit", "cat": "Fit", "short": "A connection held only by a snug fit between two parts, with no latch or thread.",
  "body": ["Many vacuum hoses, wands and accessories simply push together and stay put by friction.", "Friction fits loosen as the plastic wears, and a fitting that is slightly too small falls off while one slightly too large won't go on.", "Tapered ends make friction fits more forgiving because the parts wedge together."],
  "quote": "If an accessory keeps falling off, measure both ends; a slightly larger custom cuff usually fixes it.", "related": ["fit-types", "taper", "od-and-id"]},
 {"slug": "taper", "term": "Taper", "cat": "Fit", "short": "A gradual change in diameter along a cuff or port, so it wedges into its mating part.",
  "body": ["Most vacuum cuffs and tool ports are slightly tapered rather than perfectly straight.", "That's why a single measurement isn't enough: measure the diameter at both the end and the base of a tapered part.", "A taper helps parts of slightly different sizes fit snugly, within limits."],
  "quote": "Measure tapered ends at the tip and at the base, and tell us which is which.", "related": ["od-and-id", "friction-fit", "tolerance"]},
 {"slug": "step-adapter", "term": "Step adapter", "cat": "Parts", "short": "An adapter with several diameters in steps, so it can fit more than one hose or port size.",
  "body": ["A step adapter has a series of rings of different sizes. You use the step that matches your port, and some can be cut down to remove steps you don't need.", "They're handy for a quick connection, but each step only fits well over a narrow range, and the joint can leak or slip.", "A custom adapter sized to both of your exact ends usually fits more securely."],
  "quote": "If a step adapter keeps slipping, we can make one sized to your exact port and hose.", "related": ["dust-port-hose-sizes", "fit-types", "od-and-id"]},
 {"slug": "blast-gate", "term": "Blast gate", "cat": "Parts", "short": "A sliding gate in a dust collection line that opens or closes the airflow to one machine.",
  "body": ["In a shop with several tools on one dust collector, blast gates let you close off the tools you're not using so the suction goes where it's needed.", "Gates come in common duct sizes such as 2-1/2 and 4 inch, in plastic or metal.", "A gate that doesn't seal fully wastes suction, so a snug fit at both ends matters."],
  "quote": "Need a gate or reducer for an odd duct size? We can make one to fit.", "related": ["dust-port-hose-sizes", "cyclone-separator", "step-adapter"]},
 {"slug": "cyclone-separator", "term": "Cyclone separator", "cat": "Parts", "short": "A device that spins incoming air so most dust and chips drop into a bin before reaching the vacuum or filter.",
  "body": ["A cyclone separator sits between the tool and the vacuum or dust collector, often on top of a bucket or can.", "Air enters at an angle and spins; heavier debris falls out into the container, and the air continues to the vacuum.", "It keeps the vacuum's filter cleaner and its suction steadier, especially for fine dust."],
  "quote": "Lids, inlet adapters and fittings for separators are common replacement parts; send us the model or measurements.", "related": ["blast-gate", "dust-port-hose-sizes"]},
 {"slug": "locking-hose-ends", "term": "Locking hose ends", "cat": "Parts", "short": "Hose and accessory ends with a twist or click lock, so they don't pull apart in use.",
  "body": ["Several wet/dry vac brands use locking ends on their hoses and accessories, under names such as Lock-On and Pos-I-Lock.", "Locking ends hold well within one brand, but they often won't lock onto another brand's fitting, even at the same nominal size.", "When mixing brands, plan on a friction connection or an adapter."],
  "quote": "Mixing brands? Tell us both models and we'll make an adapter that fits both ends.", "related": ["friction-fit", "dust-port-hose-sizes", "step-adapter"]},
 {"slug": "nominal-size", "term": "Nominal size", "cat": "Fit", "short": "The name of a size, like 2-1/2 inch, rather than an exact measurement.",
  "body": ["Hose and pipe sizes are usually nominal: they name a size family. A 2-1/2 inch vacuum hose doesn't measure exactly 2.5 inches anywhere.", "Two parts with the same nominal size usually connect, but real diameters vary by brand, so fit isn't guaranteed.", "When fit matters, measure the actual outside and inside diameters."],
  "quote": "Give us the measured diameters, not just the nominal size, and the part will fit the first time.", "related": ["dust-port-hose-sizes", "od-and-id", "tolerance"]},
]

# ---------- R12: guide ----------
def guide_fit_problems(c):
    import seo2
    L = c.link
    sections = [
        ("loose", "It's loose or falls off", f'<p>The male end is a little too small for the female end. Measure both: the outside of the part that slides in and the inside of the part that slides over (<a href="{L("glossary/od-and-id/")}">OD and ID</a>). Tape is a short-term fix; it peels and leaks. A cuff sized to your exact port, or a flexible <a href="{L("glossary/tpu/")}">TPU</a> sleeve, holds properly.</p>'),
        ("tight", "It won't go on", f'<p>The parts may be the same <a href="{L("glossary/nominal-size/")}">nominal size</a> but different real diameters, or one end is <a href="{L("glossary/taper/")}">tapered</a> the wrong way. Don\'t force it; plastic cracks. Measure both ends at the tip and the base, and compare them with the <a href="{L("tools/inch-mm-converter/")}">inch–mm converter</a>.</p>'),
        ("lock", "It fits but won't lock", f'<p>Brands use different <a href="{L("glossary/locking-hose-ends/")}">locking ends</a>. A same-size accessory from another brand will often slide on but not lock. That\'s fine for light use; for a secure joint, use an adapter with the right lock on one side and a friction fit on the other.</p>'),
        ("leak", "It leaks suction", f'<p>Gaps at a joint waste suction and spread fine dust. Check for a cracked cuff, a worn friction fit, or a step adapter used between steps. A <a href="{L("glossary/step-adapter/")}">step adapter</a> only seals well at the step that matches your port.</p>'),
        ("two", "Two different sizes", f'<p>Use <a href="{L("tools/will-it-fit/")}">Will it fit?</a> to compare two models, then the <a href="{L("tools/adapter-builder/")}">adapter builder</a> to request an adapter sized to both. Common sizes are listed in the <a href="{L("sizes/")}">size chart</a>.</p>'),
        ("safe", "When not to adapt", f'<p>Adapters are for vacuum and dust collection connections. We don\'t make pressurized, electrical or safety-critical fittings; see <a href="{L("terms/")}#t4">what we won\'t make</a>.</p>'),
    ]
    return seo2._guide(c, "guides/vacuum-adapter-fit-problems/", "Shop Vac Adapter Won't Fit? Loose, Tight & Leak Fixes",
                       "Shop vac adapter fit problems and fixes", "Loose, tight, won't lock, or leaking: what causes each fit problem between hoses, ports and accessories, and how to fix it.",
                       sections, "Shop vac hose or adapter loose, too tight, not locking or leaking? Causes and fixes for each, plus how to measure and when a custom adapter helps.", "Adapter fit problems")

# ---------- R13: downloadable PDFs ----------
def make_pdfs(root):
    import os
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas
    from fractions import Fraction
    os.makedirs(root + "/assets/downloads", exist_ok=True)
    bm = _bm(); T = _T()
    # size chart
    cv = canvas.Canvas(root + "/assets/downloads/TPF-shop-vac-size-chart.pdf", pagesize=letter)
    cv.setTitle("Shop vac hose and port size chart"); cv.setAuthor("True Part Fabrication")
    W, H = letter; y = H - 0.7 * inch
    def header():
        nonlocal y
        cv.setFont("Helvetica-Bold", 14); cv.drawString(0.6 * inch, H - 0.6 * inch, "Shop vac hose and port size chart")
        cv.setFont("Helvetica", 8); cv.drawRightString(W - 0.6 * inch, H - 0.6 * inch, "True Part Fabrication · Modesto, CA · (209) 554-4800 · " + B.BASE.replace("https://", ""))
        y = H - 0.95 * inch
    header()
    for b in list(T.BRANDS) + sorted({r["b"] for r in bm.rows()} - set(T.BRANDS)):
        rs = [r for r in bm.rows() if r["b"] == b]
        if not rs: continue
        if y < 1.2 * inch: cv.showPage(); header()
        cv.setFont("Helvetica-Bold", 10); cv.drawString(0.6 * inch, y, b); y -= 0.18 * inch
        for r in rs:
            if y < 0.7 * inch: cv.showPage(); header(); cv.setFont("Helvetica-Bold", 10); cv.drawString(0.6 * inch, y, b + " (cont.)"); y -= 0.18 * inch
            cv.setFont("Helvetica", 7.6)
            cv.drawString(0.7 * inch, y, r["mc"][:22]); cv.drawString(2.1 * inch, y, r["d"][:70])
            cv.drawString(6.0 * inch, y, ", ".join(r["s"])); cv.drawString(7.15 * inch, y, (r["conf"] or "")[:9]); y -= 0.15 * inch
        y -= 0.08 * inch
    cv.setFont("Helvetica", 7); cv.drawString(0.6 * inch, 0.45 * inch, "Confirmed: published spec. Likely: matched by size or rating. Verify: check before buying. Brand names are trademarks of their owners, used only to describe fit.")
    cv.save()
    # fraction chart
    cv = canvas.Canvas(root + "/assets/downloads/TPF-fraction-to-mm-chart.pdf", pagesize=letter)
    cv.setTitle("Fraction, decimal and mm chart"); cv.setAuthor("True Part Fabrication")
    cv.setFont("Helvetica-Bold", 14); cv.drawString(0.6 * inch, H - 0.6 * inch, "Inch fraction to decimal and millimeter chart")
    cv.setFont("Helvetica", 8); cv.drawRightString(W - 0.6 * inch, H - 0.6 * inch, "True Part Fabrication · " + B.BASE.replace("https://", ""))
    for col in range(2):
        x = 0.8 * inch + col * 3.6 * inch; yy = H - 1.0 * inch
        cv.setFont("Helvetica-Bold", 9); cv.drawString(x, yy, "Fraction"); cv.drawString(x + 1.1 * inch, yy, "Inches"); cv.drawString(x + 2.1 * inch, yy, "mm"); yy -= 0.2 * inch
        for n in range(1 + col * 32, 33 + col * 32):
            f = Fraction(n, 64)
            cv.setFont("Helvetica-Bold" if f.denominator <= 8 else "Helvetica", 9)
            cv.drawString(x, yy, f"{f.numerator}/{f.denominator}"); cv.drawString(x + 1.1 * inch, yy, f"{float(f):.4f}"); cv.drawString(x + 2.1 * inch, yy, f"{float(f) * 25.4:.2f}")
            yy -= 0.27 * inch
    cv.save()

# ---------- R14: what's new + feed ----------
NEWS = [
    ("2026-11-02", "Part sets", "bundles/", "Tools that work together, grouped by tool family and hose size. Add a whole set to your cart in one click."),
    ("2026-11-02", "One-page business flyer", "business/", "A printable summary of what we make for food processing, agriculture, warehouses and industrial shops."),
    ("2026-11-01", "Will it fit? compatibility checker", "tools/will-it-fit/", "Compare any two vacs, hoses, ports or accessories and see whether they connect directly or need an adapter."),
    ("2026-11-01", "Size pages for every model, and a page for every size", "sizes/", "A page for each vac, hose and tool port in our size data, a printable chart, and hub pages listing everything in each size."),
    ("2026-11-01", "Guide: shop vac adapter fit problems", "guides/vacuum-adapter-fit-problems/", "Loose, tight, won't lock or leaking: causes and fixes."),
    ("2026-11-01", "My shop and the inch–mm converter", "my-shop/", "Save your equipment to see the parts that fit, and convert caliper readings with a printable fraction chart."),
    ("2026-11-01", "Eight new glossary terms", "glossary/", "OD and ID, friction fit, taper, step adapter, blast gate, cyclone separator, locking hose ends and nominal size."),
    ("2026-10-31", "Guides: hose sizes by brand and replacing a discontinued part", "guides/shop-vac-hose-sizes/", "Which hose sizes each brand uses, and five ways to replace a plastic part that's no longer sold."),
    ("2026-10-31", "Online cart", "request-list/", "Collect parts in a cart and send one quote request; online checkout opens January 1, 2027."),
]
def whats_new(c):
    items = "".join(f'<li><time datetime="{d}">{datetime.date.fromisoformat(d).strftime("%b %-d, %Y")}</time><a href="{c.link(u)}">{esc(t)}</a><p>{esc(s)}</p></li>' for d, t, u, s in NEWS)
    body = f"""<main id="main">
<div class="page-hero"><div class="wrap">
  {B.crumbs(c, [('Home', ''), ("What's new", 'whats-new/')])}
  <h1>What's new</h1>
  <p class="lead">New tools, guides, size data and parts, newest first. Follow along with the <a href="{c.link('feed.xml')}" style="color:var(--ink)">feed</a> in any feed reader.</p>
</div></div>
<div class="wrap" style="padding-block:30px 80px"><ol class="news">{items}</ol></div>
</main>"""
    return B.doc(c, B.head(c, "What's New: Tools, Guides & Size Data | True Part Fabrication", "The latest tools, guides, size data and parts from True Part Fabrication, newest first, with a feed for feed readers.", []), body)

def feed_xml():
    e = lambda s: html.escape(s, quote=True)
    entries = "".join(f'<entry><title>{e(t)}</title><link href="{B.BASE}/{u}"/><id>{B.BASE}/{u}#{d}</id><updated>{d}T12:00:00Z</updated><summary>{e(s)}</summary></entry>' for d, t, u, s in NEWS)
    return (f'<?xml version="1.0" encoding="utf-8"?>\n<feed xmlns="http://www.w3.org/2005/Atom"><title>True Part Fabrication: what\'s new</title>'
            f'<link href="{B.BASE}/whats-new/"/><link rel="self" href="{B.BASE}/feed.xml"/><id>{B.BASE}/feed.xml</id><updated>{NEWS[0][0]}T12:00:00Z</updated>'
            f'<author><name>True Part Fabrication</name></author>{entries}</feed>\n')

def models_json(c):
    return json.dumps([dict(x, id=i) for i, x in enumerate(all_items())], ensure_ascii=False, separators=(",", ":"))

def pages():
    p = {"tools/will-it-fit/": will_it_fit, "whats-new/": whats_new, "guides/vacuum-adapter-fit-problems/": guide_fit_problems}
    for s in sizes_used():
        p[size_url(s)] = (lambda ss: (lambda c: size_hub(c, ss)))(s)
    return p

JS = r"""
  // ---- part page: check your model ----
  (function(){var w=document.querySelector('[data-fitcheck]');if(!w)return;var M=null,R=w.getAttribute('data-root'),S=w.getAttribute('data-sizes').split('|'),inp=w.querySelector('input'),out=w.querySelector('.fc-out'),dl=w.querySelector('datalist');
    function load(cb){if(M)return cb();fetch(w.getAttribute('data-models')).then(function(r){return r.json()}).then(function(j){M=j.filter(function(x){return x.g!=='Accessories'});M.forEach(function(x){var o=document.createElement('option');o.value=x.b+' '+x.m;dl.appendChild(o)});cb()}).catch(function(){})}
    function go(){load(function(){var q=inp.value.trim().toLowerCase();if(!q)return;var x=M.filter(function(x){return (x.b+' '+x.m).toLowerCase()===q||x.m.toLowerCase()===q})[0]||M.filter(function(x){return (x.b+' '+x.m).toLowerCase().indexOf(q)>-1})[0];out.textContent='';
      if(!x){out.textContent='That model isn\'t in our size data yet. Send the model number with your request and we\'ll check.';return}
      var same=x.s.filter(function(s){return S.indexOf(s)>-1}),a=document.createElement('a');a.href=R+x.u;a.textContent=x.b+' '+x.m;
      out.appendChild(document.createTextNode(same.length?'Same size ('+same.join(', ')+'): ':'Different size ('+x.s.join(', ')+'): '));out.appendChild(a);
      out.appendChild(document.createTextNode(same.length?' should take this part. Brand locking ends may differ.':' needs an adapter for this part. '));
      if(!same.length){var b=document.createElement('a');b.href=R+'tools/adapter-builder/?a='+encodeURIComponent(x.s[0])+'&b='+encodeURIComponent(S[0]);b.textContent='Build an adapter';out.appendChild(b)}})}
    inp.addEventListener('focus',function(){load(function(){})});w.querySelector('button').addEventListener('click',go);inp.addEventListener('keydown',function(e){if(e.key==='Enter'){e.preventDefault();go()}})})();
  // ---- size chart filter ----
  (function(){var q=document.getElementById('chart-q');if(!q)return;var st=document.getElementById('chart-n');
    q.addEventListener('input',function(){var v=q.value.trim().toLowerCase(),n=0;document.querySelectorAll('.chart tbody tr').forEach(function(tr){var on=!v||tr.textContent.toLowerCase().indexOf(v)>-1;tr.hidden=!on;if(on)n++});
      document.querySelectorAll('.chart h2[id]').forEach(function(h){var t=h.nextElementSibling;var any=t&&[].some.call(t.querySelectorAll('tbody tr'),function(r){return !r.hidden});h.hidden=!any;if(t)t.hidden=!any});st.textContent=v?n+' match'+(n===1?'':'es'):''})})();
  // ---- recently viewed models (for My shop) ----
  (function(){var m=document.querySelector('main[data-model]');if(!m)return;try{var K='tpf-recent-models',L=JSON.parse(localStorage.getItem(K)||'[]'),d=JSON.parse(m.getAttribute('data-model'));L=L.filter(function(x){return x.u!==d.u});L.unshift(d);localStorage.setItem(K,JSON.stringify(L.slice(0,8)))}catch(e){}})();
  // ---- open this page on your phone (QR) ----
  (function(){var b=document.querySelector('[data-phone-qr]');if(!b||typeof qrcode!=='function')return;b.hidden=false;b.addEventListener('click',function(){var box=document.getElementById('phone-qr');if(box){box.remove();b.setAttribute('aria-expanded','false');return}
    var q=qrcode(0,'M');q.addData(location.href.split('#')[0]);q.make();box=document.createElement('div');box.id='phone-qr';box.className='phone-qr';box.innerHTML=q.createSvgTag({cellSize:4,margin:2,scalable:true});var p=document.createElement('p');p.textContent='Scan with your phone camera to open this page in the shop.';box.appendChild(p);b.insertAdjacentElement('afterend',box);b.setAttribute('aria-expanded','true');
    var s=box.querySelector('svg');if(s){s.setAttribute('role','img');s.setAttribute('aria-label','QR code for this page')}})})();
"""

CSS = """
.hub h2{font-size:1.2rem;margin:34px 0 12px}.hub h2 small{color:var(--faint);font-weight:400}
.hub-list{list-style:none;margin:0;padding:0;columns:2;column-gap:40px}
.hub-list li{break-inside:avoid;padding:6px 0;border-bottom:1px solid var(--line)}
.hub-list a{color:var(--ink);font-weight:600}.hub-list span{color:var(--muted);font-size:.88rem}
@media (max-width:760px){.hub-list{columns:1}}
.fitcheck{margin-top:12px;padding:14px 16px;border:1px solid var(--line);border-radius:10px;max-width:560px}
.fitcheck label{display:block;font:500 .7rem var(--f-mono);letter-spacing:.12em;text-transform:uppercase;color:var(--faint);margin-bottom:8px}
.fc-row{display:flex;gap:10px;flex-wrap:wrap}.fc-row input,.wif input,.chart-q input{font:400 1rem var(--f-body);color:var(--ink);background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:9px 12px;min-width:min(260px,100%)}
.fc-out{margin:10px 0 0;color:var(--ink)}.fc-out a{color:var(--ink)}
.wif-out{font-size:1.02rem;color:var(--ink)}.wif-out a{color:var(--ink)}.wif-out .btn{color:#fff}
.news{list-style:none;margin:0;padding:0;max-width:760px}.news li{padding:18px 0;border-bottom:1px solid var(--line)}
.news time{display:block;font:500 .7rem var(--f-mono);letter-spacing:.12em;text-transform:uppercase;color:var(--faint)}
.news a{color:var(--ink);font-weight:600;font-size:1.05rem}.news p{margin:6px 0 0;color:var(--muted)}
.chart-q{display:flex;gap:12px;align-items:center;flex-wrap:wrap;margin:16px 0}
.phone-qr{margin-top:12px;padding:14px;background:#fff;border-radius:10px;width:220px}.phone-qr svg{width:100%;height:auto;display:block}.phone-qr p{color:#111;font-size:.82rem;margin:8px 0 0}
.bm-phone{font:600 .82rem var(--f-body);color:var(--ink);background:transparent;border:1px solid var(--line);border-radius:999px;padding:6px 14px;cursor:pointer}
.bm-phone:hover{border-color:var(--accent)}
.acts2 a.tbtn,.dl-links a.tbtn{display:inline-flex;align-items:center;text-decoration:none}
.dl-links{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px}
@media print{.fitcheck,.chart-q,.phone-qr,[data-phone-qr]{display:none!important}.hub-list{columns:2}}
"""

# ---- clearer links (user request: make internal links obviously clickable) ----
CSS += """
main :is(p,li,dd,td,dt,figcaption,.lead,.def,.note,.legal,.fc-out,.wif-out) a:not([class]),.side a,.faq .a a,.about-part a,.prose a{color:var(--ink);text-decoration:underline;text-decoration-color:var(--accent-hi);text-decoration-thickness:1.5px;text-underline-offset:3px;border-bottom:0;transition:color .15s,text-decoration-thickness .15s}
main :is(p,li,dd,td,dt,figcaption,.lead,.def,.note,.legal,.fc-out,.wif-out) a:not([class]):hover,.side a:hover,.faq .a a:hover,.about-part a:hover,.prose a:hover{color:var(--accent-hi);text-decoration-thickness:2.5px}
main a:not([class]):focus-visible{outline:2px solid var(--accent-hi);outline-offset:2px;border-radius:2px}
td.mo a,.hub-list a{font-weight:600}
.rel a,.mini a{position:relative;padding-right:38px}
.rel a::after,.mini a::after{content:"\\2192";position:absolute;right:14px;top:50%;transform:translateY(-50%);color:var(--accent-hi);font-size:1.05rem;transition:transform .15s}
.rel a:hover::after,.mini a:hover::after{transform:translate(4px,-50%)}
.rel a:hover,.mini a:hover{border-color:var(--accent)}
.terms-strip a{color:var(--ink)}
.terms-strip a::after{content:" \\2192";color:var(--accent-hi)}
.crumbs a{text-decoration:underline;text-decoration-color:var(--line);text-underline-offset:3px}
.crumbs a:hover{text-decoration-color:var(--accent-hi)}
.ms-item>a:first-child{text-decoration:underline;text-decoration-color:var(--accent-hi);text-underline-offset:3px}
@media print{.rel a::after,.mini a::after,.terms-strip a::after{content:none}}
"""
