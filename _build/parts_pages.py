"""One page per catalog part: /parts/<slug>/"""
import re, html, json
import build as B
esc = html.escape

EBAY_SEARCH = "https://www.ebay.com/sch/i.html?_ssn=truepartfabrication&_nkw="
MAT = {"PETG": "petg", "TPU": "tpu", "ASA": "asa", "PA-CF": "pa-cf", "PLA": "pla", "ABS": "abs"}
KIND = {"adapter": "Adapter / fitting", "nozzle": "Nozzle / tool", "brush": "Brush", "separator": "Dust separator", "clip": "Clip / cover / holder", "roller": "Roller / wheel"}
BRAND_SLUG = None

def slugify(s):
    s = s.lower().replace("&", " and ").replace("/", " ").replace('"', " in ")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s

def assign_slugs(items):
    seen = set()
    for it in items:
        ref = it["oem"] or it.get("for", "")
        words = slugify(it["n"]).split("-")
        w = words[:8]
        while w and (w[-1] in ("for", "to", "in", "with", "and", "of", "the", "a", "on") or (w[-1].isdigit() and len(w) > 1 and w[-2] in ("for", "to", "with"))):
            w = w[:-1]
        base = slugify(it["b"] + " " + ref) + "-" + "-".join(w)
        base = re.sub(r"-+", "-", base)[:90].strip("-")
        s, k = base, 2
        while s in seen:
            s = f"{base}-{k}"; k += 1
        seen.add(s); it["slug"] = s
    return items

def url(it): return "parts/" + it["slug"] + "/"

def mat_html(c, m):
    out = []
    for part in [x.strip() for x in m.split("/")]:
        sl = MAT.get(part)
        out.append(f'<a href="{c.link("glossary/" + sl + "/")}" style="color:var(--ink)">{esc(part)}</a>' if sl else esc(part))
    return " or ".join(out)

PART_CSS = r"""
.acts2{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-top:14px}
.tbtn{font:600 .85rem var(--f-body);background:none;border:1px solid var(--line);color:var(--ink);border-radius:999px;height:38px;padding:0 16px;cursor:pointer}
.tbtn:hover{border-color:var(--accent)}
.tstat{color:var(--muted);font-size:.88rem}
.sz small{font-weight:400;opacity:.75}
.sortbox{display:inline-flex;align-items:center;gap:8px;color:var(--muted);font-size:.88rem}
.sortbox select{font:400 .9rem var(--f-body);color:var(--ink);background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:8px 12px}
@media print{
  .opening,header,footer,.mnav,.to-top,.acts,.acts2,.add-list,.cta-band,.recent,.rel,.head:has(+ .rel),.list-pill,#list-live,.crumbs{display:none!important}
  body{zoom:1!important;background:#fff!important;color:#000!important}
  :root{--bg:#fff;--surface:#fff;--ink:#000;--muted:#222;--faint:#444;--line:#bbb}
  .page-hero{padding-block:0 12px!important;border-bottom:1px solid #bbb}
  .pp{grid-template-columns:1fr 260px!important;gap:24px!important;padding-block:16px!important}
  .pp .spec,.pp .fig{break-inside:avoid}
  main::after{content:"True Part Fabrication · Modesto, CA · " attr(data-url);display:block;margin-top:24px;font-size:11px;color:#444}
}
/* ---- part pages ---- */
.pp{display:grid;grid-template-columns:minmax(0,1fr) 380px;gap:56px;padding-block:48px 90px;align-items:start}
.pp .spec{border:1px solid var(--line);border-radius:8px;overflow:hidden}
.pp .spec div{display:grid;grid-template-columns:150px 1fr;gap:16px;padding:16px 20px;border-bottom:1px solid var(--line)}
.pp .spec div:last-child{border-bottom:0}
.pp .spec dt{font:500 .7rem var(--f-mono);letter-spacing:.14em;text-transform:uppercase;color:var(--faint);padding-top:3px}
.pp .spec dd{margin:0;color:var(--ink)}
.pp .acts{display:flex;gap:12px;flex-wrap:wrap;margin-top:26px}
.pp .fig{border:1px solid var(--line);border-radius:8px;overflow:hidden;background:var(--surface)}
.pp .fig img{display:block;width:100%;height:auto}
.pp .fig figcaption{font-size:.8rem;color:var(--faint);padding:10px 14px;border-top:1px solid var(--line)}
.pp .note{color:var(--muted);font-size:.95rem;margin-top:22px;max-width:62ch}
.pp .note a{color:var(--ink)}
.price-tag{display:inline-block;font:600 1.4rem var(--f-body);color:var(--ink);margin-top:18px}
.price-tag small{display:block;font:400 .8rem var(--f-body);color:var(--faint)}
.rel{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.rel a{display:grid;gap:6px;padding:18px;border:1px solid var(--line);border-radius:6px;background:var(--surface);text-decoration:none;color:var(--ink);transition:border-color .2s}
.rel a:hover{border-color:var(--accent)}
.rel a span{font:.72rem var(--f-mono);color:var(--faint)}
.list .row h3.n a{color:inherit;text-decoration:none}
.list .row h3.n a:hover{text-decoration:underline;text-decoration-color:var(--accent);text-underline-offset:3px}
.pc h4 a,.row .n a{color:inherit;text-decoration:none}
.pc h4 a:hover,.row .n a:hover{text-decoration:underline;text-decoration-color:var(--accent);text-underline-offset:3px}
@media (max-width:900px){.pp{grid-template-columns:1fr;gap:32px}.rel{grid-template-columns:1fr 1fr}}
@media (max-width:560px){.pp .spec div{grid-template-columns:1fr;gap:4px}.rel{grid-template-columns:1fr}}
"""

def part_page(c, it, items, hose):
    import tools as T
    b = it["b"]; slug = T.BRANDS.get(b, (None,))[0]
    ref = it["oem"] or it.get("for", "")
    fit = it["f"]
    sizes = []
    if it["oem"]:
        for r in hose:
            if r["mc"].split(" / ")[0] == it["oem"] or r["m"] == it["oem"]:
                sizes = r["s"]; break
    crumbs_list = [("Home", ""), ("Compatible parts", "parts/")]
    if slug: crumbs_list.append((b + " parts", "brands/" + slug + "/"))
    crumbs_list.append((it["n"], url(it)))
    rows = [("Replaces" if it["oem"] else "For", f'{esc(b)} <b style="font-family:var(--f-mono);font-weight:500">{esc(ref)}</b>'),
            ("Fits", esc(fit) if fit else 'Ask us to confirm your model <span class="fitbadge">Fit to confirm</span>'),
            ("Material", mat_html(c, it["mat"])),
            ("Type", esc(KIND.get(it["i"], it["i"].title())))]
    if sizes:
        rows.append(("Size", "".join(f'<span class="sz">{esc(s)}</span> ' for s in sizes) + f' <a href="{c.link("tools/hose-size-finder/")}" style="color:var(--ink);font-size:.88rem">Hose size finder</a>'))
    rows.append(("Made in", "Modesto, California, to order"))
    spec = "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in rows)
    price = ""
    if it.get("price"):
        price = f'<div class="price-tag">From ${it["price"]:.2f}<small>Final price is in your written quote.</small></div>'
    same = [x for x in items if x is not it and x["b"] == b and x["i"] == it["i"]]
    same += [x for x in items if x is not it and x["b"] == b and x not in same]
    rel = "".join(f'<a href="{c.link(url(x))}">{esc(x["n"])}<span>{esc(B.rp(x))}</span></a>' for x in same[:6])
    status = "confirmed" if fit else "not yet confirmed"
    body = f"""<main id="main" data-url="{B.BASE}/{url(it)}">
<div class="page-hero"><div class="wrap">
  {B.crumbs(c, crumbs_list)}
  <h1>{esc(it['n'])}</h1>
  <p class="lead">A compatible aftermarket replacement for {esc(b)} {esc(ref)}, manufactured to order in Modesto, CA. Fit is {status} for the models listed. Free reprint if it doesn't fit.</p>
  {price}
</div></div>
<div class="wrap">
  <div class="pp">
    <div>
      <dl class="spec" style="margin:0">{spec}</dl>
      <div class="acts">
        <a class="btn" href="{c.link('', 'quote')}" data-part="{esc(B.part_text(it))}">Request this part <span class="ar">→</span></a>
        <a class="btn ghost" href="{EBAY_SEARCH + esc(re.sub(r'[^A-Za-z0-9-]+', '+', ref).strip('+'))}" target="_blank" rel="noopener">Check our eBay store <span class="ar">↗</span></a>
      </div>
      <div class="acts2"><button type="button" class="tbtn" data-print>Print spec sheet</button><button type="button" class="tbtn" data-share data-title="{esc(it['n'])}">Share this part</button><span class="tstat" role="status"></span></div>
      <p class="note">Send your equipment's model number with the request so we can confirm the fit before we print. Not sure of a size? Use the <a href="{c.link('guides/how-to-measure-a-part/')}">measuring guide</a>. Prices and turnaround are in your written quote; see the <a href="{c.link('faq/')}">FAQ</a> and our <a href="{c.link('terms/')}">Terms of Service</a>.</p>
    </div>
    <figure class="fig" style="margin:0"><img src="{c.asset('img/sample-' + it['i'] + '.jpg')}" alt="Illustration of a custom manufactured {esc(KIND.get(it['i'], it['i']).lower())}" width="640" height="480" loading="lazy"><figcaption>Illustration only, not a photo of this exact part.</figcaption></figure>
  </div>
  {f'<div class="head" style="margin:10px 0 22px"><div class="label">More {esc(b)} parts</div></div><div class="rel">{rel}</div>' if rel else ''}
  <div class="recent" id="recent" data-me="{esc(it['n'])}|{esc(B.rp(it))}" hidden><div class="head" style="margin:44px 0 18px"><div class="label">Recently viewed</div></div><div class="rel" id="recent-list"></div></div>
  <p class="legal" style="margin:44px 0 90px">This is a compatible aftermarket part made by True Part Fabrication, not a genuine {esc(b)} part. {esc(b)} and its part and model numbers are trademarks of their owner and are used only to describe fit. True Part Fabrication is not affiliated with or endorsed by {esc(b)}.</p>
</div>
</main>"""
    t_ref = f" for {b} {ref}" if ref else f" for {b}"
    title = f"{it['n']}{t_ref} | True Part Fabrication"
    if len(title) > 95: title = f"{it['n']}{t_ref}"
    desc = f"Aftermarket {it['n'][0].lower() + it['n'][1:]} that {'replaces' if it['oem'] else 'fits'} {b} {ref}." + (f" Fits {fit}." if fit else "") + f" Made in {it['mat']} in Modesto, CA. Free reprint if it doesn't fit."
    lds = [B.crumbs_ld(crumbs_list)]
    if it.get("price"):
        lds.append({"@context": "https://schema.org", "@type": "Product", "name": it["n"], "description": desc,
                    "brand": {"@type": "Brand", "name": "True Part Fabrication"}, "image": B.BASE + "/assets/img/sample-" + it["i"] + ".jpg",
                    "offers": {"@type": "Offer", "price": f'{it["price"]:.2f}', "priceCurrency": "USD", "availability": "https://schema.org/PreOrder", "url": B.BASE + "/" + url(it)}})
    return B.doc(c, B.head(c, title, desc[:300], lds, og_type="product"), body)

def pages():
    import tools as T
    items = assign_slugs(B.CAT["items"])
    return {url(it): (lambda c, it=it: part_page(c, it, items, T.HOSE)) for it in items}
