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

FLYER_HTML = r"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:Archivo;src:url(@@R@@/assets/fonts/archivo-latin-wdth-normal.woff2) format("woff2");font-weight:100 900;font-stretch:62% 125%}
@font-face{font-family:"Instrument Sans";src:url(@@R@@/assets/fonts/instrument-sans-latin-wght-normal.woff2) format("woff2");font-weight:400 700}
@font-face{font-family:"Instrument Serif";font-style:italic;src:url(@@R@@/assets/fonts/instrument-serif-latin-400-italic.woff2) format("woff2")}
@font-face{font-family:"JetBrains Mono";src:url(@@R@@/assets/fonts/jetbrains-mono-latin-wght-normal.woff2) format("woff2");font-weight:100 800}
@page{size:8.5in 11in;margin:0}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:8.5in;height:11in;background:#0a0a0a;color:#f4f1ec;font-family:"Instrument Sans",sans-serif;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.page{position:relative;width:8.5in;height:11in;overflow:hidden;display:flex;flex-direction:column}
.red{color:#e3262f}
.mono{font-family:"JetBrains Mono",monospace;letter-spacing:.14em;text-transform:uppercase}
/* hero */
.hero{position:relative;padding:.45in .55in .26in;background:#0a0a0a}
.hero img.bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:62% 40%;opacity:.95;-webkit-mask-image:radial-gradient(ellipse 72% 80% at 74% 38%,#000 42%,transparent 100%);mask-image:radial-gradient(ellipse 72% 80% at 74% 38%,#000 42%,transparent 100%)}
.hero::after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(10,10,10,.92) 0%,rgba(10,10,10,.75) 35%,rgba(10,10,10,.15) 62%,rgba(10,10,10,0) 100%)}
.hero>*{position:relative;z-index:1}
.top{display:flex;align-items:center;gap:12px}
.top img{height:.62in}
.top .mono{font-size:7.5pt;color:#bdb8b0;line-height:1.6}
h1{font-family:Archivo;font-stretch:78%;font-weight:800;font-size:38pt;line-height:.92;letter-spacing:-.01em;text-transform:uppercase;margin-top:.3in}
h1 em{font-family:"Instrument Serif";font-style:italic;font-weight:400;text-transform:none;font-size:43pt;letter-spacing:0;color:#e3262f}
.sub{margin-top:.14in;max-width:4.1in;font-size:10.5pt;line-height:1.45;color:#d6d1c9}
.sub b{color:#fff}
/* services */
.sec{padding:0 .55in}
.kicker{font-size:7.5pt;color:#e3262f;margin-bottom:.1in;display:flex;align-items:center;gap:8px}
.kicker::before{content:"";width:.28in;height:2px;background:#e3262f}
.tiles{display:grid;grid-template-columns:repeat(4,1fr);gap:.12in}
.tile{border:1px solid #2a2a2a;border-radius:10px;overflow:hidden;background:#121212}
.tile img{display:block;width:100%;height:.86in;object-fit:cover}
.tile div{padding:.09in .1in .11in}
.tile b{display:block;font-family:Archivo;font-stretch:85%;font-weight:700;font-size:10.5pt;text-transform:uppercase;letter-spacing:.01em}
.tile span{display:block;margin-top:3px;font-size:7.8pt;line-height:1.35;color:#a9a39b}
/* industries */
.inds{margin-top:.18in;display:flex;flex-wrap:wrap;gap:6px}
.inds span{border:1px solid #3a3a3a;border-radius:999px;padding:4px 11px;font-size:8.3pt;color:#e9e4dc}
.inds span i{font-style:normal;color:#8d877f;font-size:7.3pt}
/* steps */
.steps{margin-top:.2in;display:grid;grid-template-columns:repeat(3,1fr);gap:.2in}
.step .n{font-family:Archivo;font-stretch:75%;font-weight:800;font-size:34pt;line-height:.9;color:transparent;-webkit-text-stroke:1.2px #e3262f}
.step b{display:block;margin-top:4px;font-size:10pt}
.step span{display:block;font-size:8pt;color:#a9a39b;line-height:1.35;margin-top:2px}
/* promise band */
.band{margin-top:.24in;background:#e3262f;color:#fff;padding:.2in .55in;display:grid;grid-template-columns:1.25fr 1fr 1fr 1fr;gap:.18in;align-items:center}
.band .big{font-family:Archivo;font-stretch:80%;font-weight:800;font-size:17pt;line-height:.98;text-transform:uppercase}
.band .big em{font-family:"Instrument Serif";font-style:italic;font-weight:400;text-transform:none;font-size:19pt}
.band p{font-size:8.3pt;line-height:1.35;border-left:1px solid rgba(255,255,255,.45);padding-left:.12in}
.band p b{display:block;font-size:9.3pt}
/* footer */
.foot{margin-top:auto;padding:.22in .55in .3in;display:grid;grid-template-columns:1fr auto;gap:.3in;align-items:end;background:radial-gradient(120% 140% at 100% 100%,#2a0b0d 0%,#0a0a0a 55%)}
.foot .mono{font-size:7.3pt;color:#8d877f}
.phone{font-family:Archivo;font-stretch:80%;font-weight:800;font-size:34pt;line-height:1;margin-top:4px}
.contact{margin-top:6px;font-size:9.5pt;color:#d6d1c9;line-height:1.55}
.price{margin-top:.12in;display:inline-flex;gap:10px;align-items:baseline;border-top:1px solid #333;padding-top:.08in}
.price b{font-family:Archivo;font-stretch:85%;font-size:15pt}
.price span{font-size:8pt;color:#a9a39b}
.qr{text-align:center}
.qr .box{background:#fff;border-radius:10px;padding:8px;width:1.25in;height:1.25in}
.qr .box svg{width:100%;height:100%}
.qr .mono{display:block;margin-top:6px;font-size:6.8pt}
.open{position:absolute;top:.52in;right:.55in;z-index:2;border:1px solid rgba(255,255,255,.35);background:rgba(10,10,10,.55);border-radius:999px;padding:5px 12px;font-size:7.5pt}
</style></head><body><div class="page">
<section class="hero"><img class="bg" src="@@R@@/assets/img/hero-black.webp" alt="">
  <div class="top"><img src="@@R@@/assets/img/logo-black.png" alt="True Part Fabrication"><div class="mono">True Part Fabrication LLC<br>Modesto, California</div></div>
  <h1>Broken.<br>Backordered.<br><em>Discontinued?</em><br><span class="red">We make it.</span></h1>
  <p class="sub">Custom and replacement plastic parts for the businesses that keep the Central Valley running. <b>No molds. No minimums. No waiting on a backorder.</b></p>
</section>
<div class="open mono">Opening Jan 1, 2027</div>
<section class="sec" style="margin-top:.06in">
  <div class="kicker mono">What we make</div>
  <div class="tiles">
    <div class="tile"><img src="@@R@@/assets/img/svc-adapter-black.jpg" alt=""><div><b>Replacement parts</b><span>Discontinued or hard-to-find parts, measured and remade.</span></div></div>
    <div class="tile"><img src="@@R@@/assets/img/svc-bracket-black.jpg" alt=""><div><b>Jigs &amp; fixtures</b><span>Guides, holders and mounts built to your drawing or sample.</span></div></div>
    <div class="tile"><img src="@@R@@/assets/img/svc-batch-black.jpg" alt=""><div><b>Small batches</b><span>10 to 500 brackets, clips or covers, no mold needed.</span></div></div>
    <div class="tile"><img src="@@R@@/assets/img/svc-enclosure-black.jpg" alt=""><div><b>Enclosures</b><span>Housings and covers for controls and sensors.</span></div></div>
  </div>
  <div class="inds"><span>Food processing <i>· non-food-contact</i></span><span>Agriculture</span><span>Warehouse &amp; cold storage</span><span>Industrial shops</span><span>Dust collection</span></div>
  <div class="steps">
    <div class="step"><div class="n">01</div><b>Send a photo or the part</b><span>With a ruler in the shot and the machine's model number.</span></div>
    <div class="step"><div class="n">02</div><b>Get a written quote</b><span>Material, price and turnaround, before any work starts.</span></div>
    <div class="step"><div class="n">03</div><b>We make it and test the fit</b><span>Then we ship it, or you pick it up in Modesto.</span></div>
  </div>
</section>
<section class="band">
  <div class="big">If it doesn't fit, <em>we reprint it free.</em></div>
  <p><b>On-site measuring</b>For parts that can't come off the machine.</p>
  <p><b>Reorder in one message</b>Your part's model stays on file.</p>
  <p><b>Ships nationwide</b>Local pickup in Modesto is free.</p>
</section>
<section class="foot">
  <div>
    <div class="mono">Call us</div>
    <div class="phone">(209) 554-4800</div>
    <div class="contact">ando23152@gmail.com &nbsp;·&nbsp; @@SITE@@<br>Modesto · Ceres · Turlock · Manteca · Tracy · Stockton</div>
    <div class="price"><b>$75 – $800+</b><span>Typical business job, quoted in writing first</span></div>
  </div>
  <div class="qr"><div class="box" id="qr"></div><span class="mono">Scan for parts &amp; quotes</span></div>
</section>
</div>
<script src="@@R@@/assets/qrcode.min.js"></script>
<script>var q=qrcode(0,'M');q.addData('@@URL@@');q.make();document.getElementById('qr').innerHTML=q.createSvgTag({cellSize:4,margin:0,scalable:true});</script>
</body></html>"""

def make_flyer(root):
    """One-page letter-size flyer for businesses, rendered from HTML with the site's fonts and images."""
    import os, pathlib
    from playwright.sync_api import sync_playwright
    os.makedirs(root + "/assets/downloads", exist_ok=True)
    R = pathlib.Path(root).resolve().as_uri()
    url = B.BASE + "/business/?ref=flyer"
    html_ = FLYER_HTML.replace("@@R@@", R).replace("@@URL@@", url).replace("@@SITE@@", esc(B.BASE.replace("https://", "")))
    tmp = os.path.join(root, "_flyer.html")
    open(tmp, "w").write(html_)
    try:
        with sync_playwright() as p:
            br = p.chromium.launch(); pg = br.new_page()
            pg.goto(pathlib.Path(tmp).resolve().as_uri()); pg.wait_for_timeout(400)
            pg.pdf(path=root + "/assets/downloads/TPF-business-flyer.pdf", width="8.5in", height="11in", print_background=True, margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
            br.close()
    finally:
        os.remove(tmp)
