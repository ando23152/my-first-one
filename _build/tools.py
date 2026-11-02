"""Resource pages: hose size finder, material picker, measuring guide, brand pages, industry pages, resources hub."""
import json, re, html
import build as B
esc = html.escape

HOSE = json.load(open(B.SRC + "/hose_rows.json"))
CAT = B.CAT
OEMS = {x["oem"]: x for x in CAT["items"] if x["oem"]}
SIZE_ORDER = ["15/16 in", "1 in", "1-1/4 in", "1-3/8 in", "1-1/2 in", "1-2/3 in", "1-3/4 in", "1-7/8 in", "2 in", "2-1/4 in", "2-1/2 in", "4 in", "32 mm", "35 mm", "36 mm", "38 mm", "22 mm", "24 mm"]

def clean_model(m): return re.sub(r"\s*\((?:not|no |aftermarket|fits)[^)]*\)", "", m).strip()
def group(r):
    t = (r["t"] + " " + r["d"]).lower()
    if re.search(r"\bvac|vacuum|collector|extractor|shop vac", r["t"].lower()) and not re.search(r"bag|filter", r["t"].lower()): return "Vacuums & collectors"
    if r["t"].lower() == "tool" or "dust port" in r["c"].lower(): return "Power tool ports"
    if re.search(r"\bhose\b", r["t"].lower()): return "Hoses"
    return "Accessories"
for r in HOSE:
    r["g"] = group(r); r["mc"] = clean_model(r["m"])

EXTRA_CSS = r"""
/* ---- resources ---- */
.res-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.res{display:grid;gap:12px;align-content:start;padding:28px;border:1px solid var(--line);border-radius:8px;background:var(--surface);text-decoration:none;transition:border-color .2s,transform .3s var(--ease)}
.res:hover{border-color:#5578A8;transform:translateY(-2px)}
.res .k{font:500 .7rem var(--f-mono);letter-spacing:.16em;text-transform:uppercase;color:var(--accent-hi)}
.res h3{font-family:var(--f-body);font-stretch:100%;font-weight:600;font-size:1.15rem;text-transform:none;letter-spacing:0;line-height:1.3}
.res p{color:var(--muted);font-size:.95rem}
.res span.go{font-weight:600;font-size:.9rem;color:var(--ink)}
@media (max-width:960px){.res-grid{grid-template-columns:1fr 1fr}}@media (max-width:600px){.res-grid{grid-template-columns:1fr}}
.hub-sec{padding-block:48px;border-bottom:1px solid var(--line)}
.hub-sec h2{font-size:1.3rem;margin-bottom:22px}
.linklist{display:flex;flex-wrap:wrap;gap:10px}
.linklist a{color:var(--ink);text-decoration:none;border:1px solid var(--line);border-radius:999px;padding:9px 16px;font-size:.92rem;transition:all .2s}
.linklist a:hover{border-color:var(--accent)}
.ftable{overflow-x:auto;border:1px solid var(--line);border-radius:6px}
.ftable table{min-width:980px}
.ftable td{font-size:.9rem;color:var(--muted)}
.ftable td.mo{font-family:var(--f-mono);font-size:.84rem;color:var(--ink);white-space:nowrap}
.ftable td.br{font:500 .72rem var(--f-mono);letter-spacing:.1em;text-transform:uppercase;color:var(--accent-hi);white-space:nowrap}
.sz{display:inline-block;font:500 .74rem var(--f-mono);color:var(--ink);border:1px solid #5578A8;border-radius:999px;padding:3px 9px;margin:0 4px 4px 0;white-space:nowrap}
.cf{font:.68rem var(--f-mono);letter-spacing:.06em;text-transform:uppercase;border-radius:999px;padding:3px 8px;white-space:nowrap}
.cf.Confirmed{color:#7fe0a0;border:1px solid rgba(127,224,160,.4)}
.cf.Likely{color:#f0c46a;border:1px solid rgba(240,196,106,.4)}
.explain b.ok{color:#7fe0a0}.explain b.lk{color:#f0c46a}
.result p a.btn{color:#fff}
.cf.Verify,.cf.na{color:var(--faint);border:1px solid var(--line)}
.ftable a.ask{color:var(--ink);font-weight:600;font-size:.84rem;white-space:nowrap}
.filters{display:grid;gap:14px;margin-bottom:22px}
.filters .row1{display:flex;gap:14px;flex-wrap:wrap;align-items:center}
.filters select{height:46px;border-radius:999px;border:1px solid var(--line);background:var(--surface);color:var(--ink);font:inherit;font-size:.92rem;padding:0 16px;width:auto}
.chips .chip.sm{height:32px;font-size:.78rem}
.explain{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:56px}
.explain div{border-top:1px solid var(--accent);padding-top:16px}
.explain h3{font-size:1rem}
.explain p{color:var(--muted);font-size:.93rem;margin-top:8px}
@media (max-width:860px){.explain{grid-template-columns:1fr}}
.picker{display:grid;grid-template-columns:1.1fr .9fr;gap:40px;align-items:start}
.mq{position:relative;border:1px solid var(--line);border-radius:8px;background:var(--surface);padding:24px;margin:0 0 16px}
.mq legend{font:600 1rem var(--f-body);padding:0 6px;color:var(--ink)}
.mq .opts{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}
.mq input{position:absolute;opacity:0;pointer-events:none}
.mq label.o{cursor:pointer;border:1px solid #5578A8;border-radius:999px;padding:9px 15px;font-size:.9rem;color:var(--ink);transition:all .2s;text-transform:none;letter-spacing:0;font-family:var(--f-body)}
.mq input:checked+label.o{background:var(--accent);border-color:var(--accent);color:#fff}
.mq input:focus-visible+label.o{outline:2px solid var(--accent-hi);outline-offset:2px}
.result{position:sticky;top:120px;border:1px solid rgba(227,38,47,.45);border-radius:8px;padding:28px;background:linear-gradient(135deg,rgba(227,38,47,.14),rgba(227,38,47,.02))}
.result .k{font:500 .7rem var(--f-mono);letter-spacing:.16em;text-transform:uppercase;color:var(--accent-hi)}
.result h2{font-size:2rem;margin-top:10px}
.result ul{margin:14px 0 0;padding-left:18px;color:var(--ink);display:grid;gap:6px}
.result .alt{margin-top:18px;padding-top:16px;border-top:1px solid var(--line);color:var(--muted);font-size:.93rem}
.result .alt a,.result p a{color:var(--ink)}
@media (max-width:960px){.picker{grid-template-columns:1fr}.result{position:static}}
.cmp td{font-size:.92rem}
.dots{letter-spacing:2px;color:var(--accent-hi);font-size:.9rem;white-space:nowrap}
.dots i{color:#5578A8;font-style:normal}
.howto{counter-reset:s;display:grid;gap:22px;max-width:900px}
.howto li{list-style:none;display:grid;grid-template-columns:56px 1fr;gap:20px;padding:26px 0;border-top:1px solid var(--line)}
.howto li::before{counter-increment:s;content:counter(s,decimal-leading-zero);display:grid;place-items:center;width:44px;height:44px;border:1px solid var(--accent);border-radius:50%;font:500 .8rem var(--f-mono);color:var(--accent-hi)}
.howto h2{font-size:1.15rem}
.howto p,.howto li li{color:var(--muted)}
.howto ul{margin:10px 0 0;padding-left:18px;display:grid;gap:6px}
.howto li ul li{display:list-item;padding:0;border:0;grid-template-columns:none}
.howto li ul li::before{content:none}
.howto figure{margin:16px 0 0;border:1px solid var(--line);border-radius:6px;background:var(--surface);padding:16px;max-width:520px}
.howto figure svg{width:100%;height:auto;display:block}
.howto figcaption{font:.75rem var(--f-mono);color:var(--faint);margin-top:8px}
.ind-list{display:grid;grid-template-columns:1fr 1fr;gap:12px 32px;margin:8px 0 0;padding:0;list-style:none}
.ind-list li{padding-left:18px;position:relative;color:var(--ink)}
.ind-list li::before{content:"";position:absolute;left:0;top:.65em;width:6px;height:6px;border-radius:50%;background:var(--accent)}
@media (max-width:600px){.ind-list{grid-template-columns:1fr}}
"""

def page_hero(c, crumbs, h1, lead, extra=""):
    return f"""<div class="page-hero"><div class="wrap">
  {B.crumbs(c, crumbs)}
  <h1>{esc(h1)}</h1>
  <p class="lead">{lead}</p>{extra}
</div></div>"""

def cta(c, h="Need a part made?", p="Describe your part and we'll reply with questions or a written quote. Free reprint if it doesn't fit."):
    return f'<div class="cta-band"><div class="wrap"><h2>{h}</h2><p>{p}</p><a class="btn" href="{c.link("", "quote")}">Request a quote <span class="ar">→</span></a></div></div>'

def G(c, slug, text): return f'<a href="{c.link("glossary/" + slug + "/")}" style="color:var(--ink)">{text}</a>'

# ---------------- HOSE SIZE FINDER ----------------
def hose_finder(c):
    brands = []
    for r in HOSE:
        if r["b"] not in brands: brands.append(r["b"])
    sizes = [s for s in SIZE_ORDER if any(s in r["s"] for r in HOSE)]
    groups = ["Vacuums & collectors", "Hoses", "Accessories", "Power tool ports"]
    rows = []
    for r in sorted(HOSE, key=lambda r: (r["b"], groups.index(r["g"]), r["mc"])):
        conf = r["conf"] or "na"
        part = OEMS.get(r["mc"].split(" / ")[0])
        if part:
            ask = f'<a class="ask" href="{c.link("", "quote")}" data-part="{esc(B.part_text(part))}">Request ours →</a>'
        else:
            from urllib.parse import quote as _q
            ask = f'<a class="ask" href="{c.link("tools/adapter-builder/")}?a={_q(r["s"][0])}&amp;am={_q(r["b"] + " " + r["mc"])}">Get an adapter →</a>'
        k = " ".join([r["b"], r["mc"], r["d"], r["c"], r["w"], r["sys"]]).lower()
        rows.append(f"""<tr data-b="{esc(r['b'])}" data-s="{esc('|'.join(r['s']))}" data-g="{esc(r['g'])}" data-k="{esc(k)}"><td class="br">{esc(r['b'])}</td><td class="mo">{(lambda _r: f'<a href="{c.link(__import__("bm").model_url(_r))}">{esc(r["mc"])}</a>' if _r else esc(r["mc"]))(__import__("bm").by_mc().get((r["b"], r["mc"])))}</td><td>{esc(r['d'])}<br><span style="color:var(--faint);font-size:.8rem">{esc(r['g'])}</span></td><td>{''.join(f'<span class="sz">{esc(s)}</span>' for s in r['s'])}<div style="font-size:.8rem;margin-top:4px">{esc(r['c'])}</div></td><td>{esc(r['w'] or '—')}</td><td><span class="cf {conf}">{esc(r['conf'] or 'Unrated')}</span></td><td>{ask}</td></tr>""")
    bchips = '<button class="chip sm" type="button" data-f="b" data-v="All" aria-pressed="true">All brands</button>' + "".join(f'<button class="chip sm" type="button" data-f="b" data-v="{esc(b)}" aria-pressed="false">{esc(b)}</button>' for b in brands)
    schips = '<button class="chip sm" type="button" data-f="s" data-v="All" aria-pressed="true">All sizes</button>' + "".join(f'<button class="chip sm" type="button" data-f="s" data-v="{esc(s)}" aria-pressed="false">{esc(s)}</button>' for s in sizes)
    gopts = '<option value="All">All types</option>' + "".join(f'<option>{g}</option>' for g in groups)
    body = f"""<main id="main">
{page_hero(c, [('Home',''),('Resources','resources/'),('Hose size finder','tools/hose-size-finder/')], 'Shop-vac hose and dust port size finder',
  f'Look up the hose, wand, and dust port sizes for {len(HOSE)} wet/dry vacuums, dust collectors, accessories, and power tools from {", ".join(brands[:-1])}, and {brands[-1]}. Find what connects to what, then get an adapter made for anything that doesn\'t.')}
<section style="padding-block:44px 80px"><div class="wrap">
  <div class="filters">
    <div class="row1">
      <div class="search"><svg viewBox="0 0 16 16" fill="none" stroke="var(--muted)" stroke-width="1.6" aria-hidden="true"><circle cx="7" cy="7" r="5"/><path d="M11 11l3.5 3.5"/></svg><label for="hf-q" style="position:absolute;left:-9999px">Search models</label><input id="hf-q" type="search" placeholder="Search a model number, e.g. DXV10S or 0880-20"></div>
      <label for="hf-g" style="position:absolute;left:-9999px">Type</label><select id="hf-g">{gopts}</select>
      <span id="hf-count" style="color:var(--faint);font-size:.88rem;margin-left:auto"></span><button type="button" class="tbtn" data-copylink="hf-cl">Copy link to this view</button><span id="hf-cl" role="status" style="color:var(--muted);font-size:.85rem"></span>
    </div>
    <div class="chips" role="group" aria-label="Filter by brand">{bchips}</div>
    <div class="chips" role="group" aria-label="Filter by size">{schips}</div>
  </div>
  <div class="ftable"><table id="hf">
    <thead><tr><th>Brand</th><th>Model</th><th>Item</th><th>Size</th><th>Works with</th><th>Confidence</th><th><span class="sr-only">Get it</span></th></tr></thead>
    <tbody>
{chr(10).join(rows)}
    </tbody></table></div>
  <p class="empty" id="hf-empty" hidden>Nothing matches. Try a shorter model number, build a custom piece in the <a href="{c.link('tools/adapter-builder/')}" style="color:var(--ink)">adapter builder</a>, or <a href="{c.link('', 'quote')}" style="color:var(--ink)">ask us</a> and we'll measure it.</p>
  <h2 class="sr-only">About these sizes</h2><div class="explain">
    <div><h3>Sizes are nominal</h3><p>"2-1/2 inch" names a family, not an exact measurement. Cuff and port diameters vary by brand, which is why universal adapters often fit loosely. See {G(c,'dust-port-hose-sizes','shop-vac hose sizes')}.</p></div>
    <div><h3>Confidence ratings</h3><p><b class="ok">Confirmed</b> means a published manufacturer spec. <b class="lk">Likely</b> means matched by size or rating. <b>Verify</b> means check your product before buying.</p></div>
    <div><h3>Measure to be sure</h3><p>Before ordering an adapter, measure the outside of the hose cuff and the inside or outside of the port. Our <a href="{c.link('guides/how-to-measure-a-part/')}" style="color:var(--ink)">measuring guide</a> shows how.</p></div>
  </div>
  <p class="legal">Researched October 2026 from manufacturer and retailer listings. Brand names and model numbers belong to their owners and are used only to describe fit. True Part Fabrication is not affiliated with any brand listed. Always confirm sizes on your own equipment.</p>
</div></section>
<div class="wrap" style="padding-bottom:40px"><div class="callout" style="max-width:760px"><div class="k">Adapter builder</div><p>Found both sizes? <a href="{c.link('tools/adapter-builder/')}" style="color:var(--ink);font-weight:600">Build your adapter</a>: pick the two ends and request it in one step.</p></div></div>
{cta(c, 'Need an adapter that fits both ends?', 'Tell us the vacuum and the tool, or send measurements. We\'ll make an adapter sized to your exact hose and port.')}
</main>
<script>
(function(){{var t=document.getElementById('hf'),rows=[].slice.call(t.tBodies[0].rows),q=document.getElementById('hf-q'),g=document.getElementById('hf-g'),cnt=document.getElementById('hf-count'),em=document.getElementById('hf-empty'),f={{b:'All',s:'All'}};
document.querySelectorAll('.filters .chip').forEach(function(c){{c.addEventListener('click',function(){{var k=c.getAttribute('data-f');f[k]=c.getAttribute('data-v');document.querySelectorAll('.filters .chip[data-f="'+k+'"]').forEach(function(x){{x.setAttribute('aria-pressed',x===c)}});go()}})}});
function go(){{var v=q.value.trim().toLowerCase().replace(/\\s+/g,' '),n=0;rows.forEach(function(r){{var ok=(f.b==='All'||r.dataset.b===f.b)&&(f.s==='All'||r.dataset.s.split('|').indexOf(f.s)>-1)&&(g.value==='All'||r.dataset.g===g.value)&&(!v||r.dataset.k.indexOf(v)>-1);r.hidden=!ok;if(ok)n++}});cnt.textContent=n+(n===1?' item':' items');em.hidden=n>0}}
function sync(){{try{{var p=new URLSearchParams();if(f.b!=='All')p.set('brand',f.b);if(f.s!=='All')p.set('size',f.s);if(g.value!=='All')p.set('type',g.value);if(q.value.trim())p.set('q',q.value.trim());var s=p.toString();history.replaceState(null,'',location.pathname+(s?'?'+s:''))}}catch(e){{}}}}
var go0=go;go=function(){{go0();sync()}};
try{{var P=new URLSearchParams(location.search);if(P.get('q'))q.value=P.get('q');if(P.get('type'))g.value=P.get('type');['b:brand','s:size'].forEach(function(kv){{var k=kv.split(':')[0],val=P.get(kv.split(':')[1]);if(!val)return;var ch=[].find.call(document.querySelectorAll('.filters .chip[data-f="'+k+'"]'),function(x){{return x.getAttribute('data-v').toLowerCase()===val.toLowerCase()}});if(ch){{f[k]=ch.getAttribute('data-v');document.querySelectorAll('.filters .chip[data-f="'+k+'"]').forEach(function(x){{x.setAttribute('aria-pressed',x===ch)}})}}}})}}catch(e){{}}
q.addEventListener('input',go);g.addEventListener('change',go);var h=(location.hash||'').slice(1);if(h){{var b=document.querySelector('.filters .chip[data-f="b"][data-v="'+decodeURIComponent(h).replace(/-/g,' ')+'"]')||[].find.call(document.querySelectorAll('.filters .chip[data-f="b"]'),function(x){{return x.getAttribute('data-v').toLowerCase().replace(/\\s+/g,'-')===h}});if(b)b.click()}}go()}})();
</script>"""
    title = "Shop-Vac Hose & Dust Port Size Finder | DeWalt, Milwaukee, Ryobi, RIDGID, WEN"
    desc = f"Free lookup of hose, wand, and dust port sizes for {len(HOSE)} wet/dry vacs, dust collectors, accessories, and power tools. 1-1/4, 1-7/8, 2-1/2, and 4 in. sizes, with compatible models."
    lds = [B.crumbs_ld([("Home", ""), ("Resources", "resources/"), ("Hose size finder", "tools/hose-size-finder/")]),
           {"@context": "https://schema.org", "@type": "WebApplication", "name": "Shop-vac hose and dust port size finder", "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}, "url": B.BASE + "/tools/hose-size-finder/", "provider": {"@id": B.BASE + "/#business"}}]
    return B.doc(c, B.head(c, title, desc, lds), body)

# ---------------- MATERIAL PICKER ----------------
MATS = [  # name, slug, heat C, heat F, uv, tough, flex, stiff, wear, cost, best
 ("PLA", "pla", "≈ 55 °C", "131 °F", 1, 1, 0, 3, 1, 1, "Prototypes, fit checks, indoor organizers"),
 ("PETG", "petg", "≈ 70 °C", "158 °F", 2, 2, 1, 2, 1, 1, "Clips, brackets, adapters, everyday parts"),
 ("ASA", "asa", "≈ 95 °C", "203 °F", 3, 2, 1, 2, 1, 2, "Outdoor, vehicle, and enclosure parts"),
 ("ABS", "abs", "≈ 95 °C", "203 °F", 0, 2, 1, 2, 1, 2, "Indoor parts near warmth; housings"),
 ("PA-CF", "pa-cf", "100 °C +", "212 °F +", 2, 3, 0, 3, 3, 3, "High-load, wear, and hot-environment parts"),
 ("TPU", "tpu", "Moderate", "", 2, 3, 3, 0, 2, 2, "Seals, bumpers, flexible cuffs, grips"),
]
def dots(n, m=3): return '<span class="dots" aria-label="' + str(n) + ' of ' + str(m) + '">' + "●" * n + "<i>" + "●" * (m - n) + "</i></span>"
def material_picker(c):
    Q = [("env", "Where will the part live?", [("in", "Indoors"), ("out", "Outdoors in the sun"), ("veh", "In a vehicle or near a motor"), ("cold", "Freezer or cold storage")]),
         ("heat", "How hot does it get?", [("room", "Room temperature"), ("warm", "Warm, up to 60 °C / 140 °F"), ("hot", "Hot, up to 90 °C / 195 °F"), ("vhot", "Very hot, above 90 °C")]),
         ("flex", "Should it be rigid or flexible?", [("rigid", "Rigid"), ("some", "A little flex (clips, snap fits)"), ("rubber", "Rubbery (seals, bumpers)")]),
         ("load", "How hard is it used?", [("light", "Light duty"), ("mod", "Everyday use"), ("heavy", "Heavy load or wear")]),
         ("proto", "Is this a prototype or fit check?", [("no", "No, it's the final part"), ("yes", "Yes, just checking fit")])]
    qs = ""
    for key, label, opts in Q:
        o = "".join(f'<input type="radio" name="{key}" id="{key}-{v}" value="{v}"{" checked" if i == 0 else ""}><label class="o" for="{key}-{v}">{esc(t)}</label>' for i, (v, t) in enumerate(opts))
        qs += f'<fieldset class="mq"><legend>{esc(label)}</legend><div class="opts">{o}</div></fieldset>'
    rows = "".join(f'<tr><td class="m"><a href="{c.link("glossary/" + s + "/")}">{n}</a></td><td class="t">{h}{(" / " + f) if f else ""}</td><td>{dots(uv)}</td><td>{dots(t)}</td><td>{dots(fl)}</td><td>{dots(st)}</td><td>{dots(w)}</td><td>{"$" * co}</td><td>{esc(best)}</td></tr>'
                   for n, s, h, f, uv, t, fl, st, w, co, best in MATS)
    links = {n: c.link("glossary/" + s + "/") for n, s, *_ in MATS}
    body = f"""<main id="main">
{page_hero(c, [('Home',''),('Resources','resources/'),('Material picker','tools/material-picker/')], 'Which material should I use for my part?',
  'Answer five quick questions about where your part lives and how it\'s used. You\'ll get a recommended material, the reasons, and a backup option. Compare all six materials in the chart below.')}
<section style="padding-block:44px 40px"><div class="wrap picker">
  <form id="mp" onsubmit="return false">{qs}</form>
  <div class="result" aria-live="polite"><div class="k">Recommended material</div><h2 id="mp-name">PETG</h2><ul id="mp-why"></ul><p class="alt" id="mp-alt"></p><p style="margin-top:18px"><a class="btn" href="{c.link('', 'quote')}" id="mp-quote">Quote a part in this material <span class="ar">→</span></a></p></div>
</div></section>
<section style="padding-block:40px 100px;border-top:1px solid var(--line)"><div class="wrap">
  <div class="head" style="margin-bottom:28px"><div class="label">Compare</div><h2>PLA vs PETG vs ASA vs ABS vs <em class="s">nylon vs TPU</em></h2><p>Relative ratings for the materials we print. Heat values are typical published ranges and vary by brand and print settings.</p></div>
  <div class="tbl"><table class="cmp"><thead><tr><th>Material</th><th>Heat limit</th><th>Sun / UV</th><th>Toughness</th><th>Flexibility</th><th>Stiffness</th><th>Wear</th><th>Cost</th><th>Best for</th></tr></thead><tbody>{rows}</tbody></table></div>
  <div class="explain">
    <div><h3>Heat decides first</h3><p>If a part sees heat, that narrows the choice fast. Learn about {G(c,'heat-deflection-temperature','heat deflection temperature')}.</p></div>
    <div><h3>Sun is the silent killer</h3><p>UV light makes many plastics brittle. Outdoors, ASA is the safe default. See {G(c,'uv-resistance','UV resistance')}.</p></div>
    <div><h3>Design matters too</h3><p>{G(c,'wall-count','Wall count')}, {G(c,'infill','infill')}, and {G(c,'print-orientation','print orientation')} change strength as much as material does.</p></div>
  </div>
</div></section>
{cta(c)}
</main>
<script>
(function(){{var L={json.dumps(links)};
function val(n){{var e=document.querySelector('input[name="'+n+'"]:checked');return e?e.value:''}}
function pick(){{var env=val('env'),heat=val('heat'),flex=val('flex'),load=val('load'),proto=val('proto'),why=[],m,alt;
if(flex==='rubber'){{m='TPU';why.push('It needs to flex like rubber, which only TPU does.');alt=heat==='hot'||heat==='vhot'?'For heat, consider a rigid ASA or PA-CF part with a TPU seal.':'For a firmer feel, a PETG part with a TPU insert also works.'}}
else if(heat==='vhot'){{m='PA-CF';why.push('Above 90 °C, carbon-fiber nylon is the only option we print that holds its shape.');why.push('Tell us the exact temperature so we can confirm the grade.');alt='If the part is outdoors and under about 90 °C, ASA is a lower-cost option.'}}
else if(heat==='hot'||env==='veh'){{m=load==='heavy'?'PA-CF':'ASA';why.push(heat==='hot'?'It sees up to about 90 °C, which rules out PLA and PETG.':'Vehicles and motors get hot, which rules out PLA and PETG.');if(m==='ASA')why.push('ASA handles heat and also resists sun.');else why.push('Heavy load plus heat calls for the strongest option.');alt=m==='ASA'?'For heavy loads or wear, step up to PA-CF.':'For lighter loads, ASA costs less.'}}
else if(env==='out'){{m=load==='heavy'?'PA-CF':'ASA';why.push('Sunlight makes PLA and ABS brittle; ASA is made to resist UV.');if(m==='PA-CF')why.push('Heavy load outdoors calls for the strongest option.');alt=m==='ASA'?'PETG works outdoors for a season or two if cost matters most.':'ASA costs less if the load is moderate.'}}
else if(env==='cold'){{m=load==='heavy'?'PA-CF':'PETG';why.push('PLA turns brittle in the cold; PETG stays tough.');why.push('PETG also handles moisture and condensation.');alt=m==='PETG'?'For heavy or impact loads, PA-CF holds up better.':'PETG costs less for everyday parts.'}}
else if(proto==='yes'&&heat==='room'){{m='PLA';why.push('PLA prints accurately and costs least, ideal for checking fit.');why.push('Order the final part in PETG or another material once the fit is right.');alt='If the prototype will be tested under load, use PETG instead.'}}
else if(load==='heavy'){{m='PA-CF';why.push('Heavy load or wear calls for carbon-fiber nylon\\'s stiffness and wear resistance.');alt='For moderate loads, PETG with extra walls costs less.'}}
else{{m=heat==='warm'?'PETG':'PETG';why.push('PETG is tough, slightly flexible, and handles moisture.');if(heat==='warm')why.push('It handles warmth up to about 70 °C better than PLA.');if(flex==='some')why.push('Its slight flex suits clips and snap fits.');alt=heat==='room'&&flex==='rigid'&&load==='light'?'For an indoor organizer or display part, PLA is fine and costs less.':'If the part also sees sun or more heat, step up to ASA.'}}
document.getElementById('mp-name').innerHTML='<a href="'+L[m]+'" style="color:inherit;text-decoration:none">'+m+'</a>';
var ul=document.getElementById('mp-why');ul.textContent='';why.forEach(function(w){{var li=document.createElement('li');li.textContent=w;ul.appendChild(li)}});
document.getElementById('mp-alt').textContent='Backup option: '+alt;
document.getElementById('mp-quote').setAttribute('data-part','Material picker suggestion: '+m+' ('+[env,heat,flex,load].join(', ')+')');}}
document.getElementById('mp').addEventListener('change',pick);pick();}})();
</script>"""
    lds = [B.crumbs_ld([("Home", ""), ("Resources", "resources/"), ("Material picker", "tools/material-picker/")]),
           {"@context": "https://schema.org", "@type": "WebApplication", "name": "Part material picker", "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}, "url": B.BASE + "/tools/material-picker/"}]
    return B.doc(c, B.head(c, "Which Material for Your Part? PLA vs PETG vs ASA vs ABS vs Nylon | Material Picker",
                           "Free material picker and comparison chart for custom manufactured parts. Compare PLA, PETG, ASA, ABS, carbon-fiber nylon, and TPU for heat, sun, toughness, flexibility, and cost.", lds), body)

# ---------------- MEASURING GUIDE ----------------
SVG_OD = """<svg viewBox="0 0 480 200" role="img" aria-label="Calipers measuring the outside diameter of a hose cuff"><rect x="40" y="70" width="210" height="80" rx="6" fill="#1d1d22" stroke="#e9e8e4" stroke-width="1.5"/><rect x="250" y="82" width="160" height="56" rx="4" fill="#2a2a30" stroke="#e9e8e4" stroke-width="1.5"/><path d="M40 40h240v14H40zM40 54v16M266 54v16" stroke="#e3262f" stroke-width="3" fill="none"/><rect x="40" y="34" width="250" height="20" fill="none" stroke="#e3262f" stroke-width="2"/><path d="M40 160v20M250 160v20" stroke="#ff3b43" stroke-width="1.5"/><path d="M44 174h202" stroke="#ff3b43" stroke-width="1.5" marker-start="url(#a)" marker-end="url(#a)"/><text x="145" y="196" text-anchor="middle" fill="#e9e8e4" font-family="JetBrains Mono, monospace" font-size="13">OD (outside diameter)</text><text x="330" y="115" text-anchor="middle" fill="#b9b9bf" font-family="JetBrains Mono, monospace" font-size="12">hose</text><defs><marker id="a" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 1L10 5L0 9z" fill="#ff3b43"/></marker></defs></svg>"""
SVG_CC = """<svg viewBox="0 0 480 200" role="img" aria-label="Measuring hole spacing center to center"><rect x="40" y="50" width="400" height="100" rx="8" fill="#1d1d22" stroke="#e9e8e4" stroke-width="1.5"/><circle cx="120" cy="100" r="18" fill="#0A3161" stroke="#e9e8e4" stroke-width="1.5"/><circle cx="360" cy="100" r="18" fill="#0A3161" stroke="#e9e8e4" stroke-width="1.5"/><path d="M120 100h240" stroke="#ff3b43" stroke-width="1.5" stroke-dasharray="4 4"/><path d="M120 34v32M360 34v32" stroke="#ff3b43" stroke-width="1.5"/><path d="M124 40h232" stroke="#ff3b43" stroke-width="1.5" marker-start="url(#b)" marker-end="url(#b)"/><text x="240" y="30" text-anchor="middle" fill="#e9e8e4" font-family="JetBrains Mono, monospace" font-size="13">center to center</text><text x="240" y="182" text-anchor="middle" fill="#b9b9bf" font-family="JetBrains Mono, monospace" font-size="12">= edge to edge + one hole diameter</text><defs><marker id="b" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 1L10 5L0 9z" fill="#ff3b43"/></marker></defs></svg>"""
SVG_PH = """<svg viewBox="0 0 480 200" role="img" aria-label="Photo setup: part beside a ruler on a plain background"><rect x="20" y="20" width="440" height="160" rx="10" fill="#e9e8e4"/><rect x="150" y="60" width="150" height="80" rx="10" fill="#e3262f"/><circle cx="225" cy="100" r="20" fill="#e9e8e4"/><rect x="60" y="150" width="360" height="18" fill="#c9a24a"/><g stroke="#3a2a10" stroke-width="1.5">""" + "".join(f'<path d="M{60+i*18} 150v{8 if i%5 else 14}"/>' for i in range(21)) + """</g><text x="240" y="44" text-anchor="middle" fill="#0A3161" font-family="JetBrains Mono, monospace" font-size="13">plain background · ruler in frame · straight on</text></svg>"""
STEPS = [
 ("Gather what you have", "<p>The original part is the best reference, even broken. You'll also want:</p><ul><li>Digital calipers if you have them, or a ruler with millimeter marks</li><li>Your phone camera</li><li>The make and model of the equipment the part came from</li></ul>", ""),
 ("Photograph it with a scale", "<p>Lay the part on a plain, light background with a ruler beside it. Shoot straight on from the front, side, and top, plus a close-up of anything that clips, threads, or slides into something else.</p>", SVG_PH),
 ("Measure the critical fits", "<p>Critical fits are the surfaces that touch another part: hose cuffs, shafts, holes, slots, and snap clips. Measure each one three times and write down the average.</p><ul><li>Use the outside jaws for outside diameters (OD)</li><li>Use the inside jaws for holes and inside diameters (ID)</li><li>Don't squeeze soft or rubbery parts; touch the jaws lightly</li></ul>", SVG_OD),
 ("Measure hole spacing", "<p>For mounting holes, measure center to center. The easy way is to measure edge to edge across two holes, then add one hole diameter.</p>", SVG_CC),
 ("Get the overall size and thickness", "<p>Measure the overall length, width, and height, and the thickness of walls and tabs. These don't need to be exact, but they help us check the model.</p>", ""),
 ("Measure what it connects to", "<p>If the part plugs into something, measure that too: the port, the hose end, or the rail. For dust adapters, measure the outside of the hose cuff and the inside or outside of the tool port. Check the <a href=\"{finder}\">hose size finder</a> for published sizes.</p>", ""),
 ("Note how it's used", "<p>Tell us where the part lives and what it does: indoors or outdoors, heat, load, how many you need, and where the original failed. Not sure which material fits? Try the <a href=\"{picker}\">material picker</a>.</p>", ""),
 ("Send it to us", "<p>Attach your photos and measurements to a <a href=\"{quote}\">quote request</a>. If something's missing, we'll ask. If the finished part doesn't fit, we reprint it free.</p>", ""),
]
def measure_guide(c):
    fmt = dict(finder=c.link("tools/hose-size-finder/"), picker=c.link("tools/material-picker/"), quote=c.link("", "quote"))
    items = "".join(f'<li><div><h2>{esc(t)}</h2>{h.format(**fmt).replace("<a href=", "<a style=\"color:var(--ink)\" href=")}{("<figure>" + s + "</figure>") if s else ""}</div></li>' for t, h, s in STEPS)
    body = f"""<main id="main">
{page_hero(c, [('Home',''),('Resources','resources/'),('How to measure a part','guides/how-to-measure-a-part/')], 'How to measure a part for a replacement',
  'Eight steps to photograph and measure a broken or discontinued part so it can be modeled and manufactured. No special tools needed, though digital calipers help.')}
<section style="padding-block:40px 80px"><div class="wrap"><ol class="howto" style="padding:0;margin:0">{items}</ol>
<div class="explain" style="max-width:900px">
  <div><h3>Why accuracy matters</h3><p>Printed parts are made to your numbers. See how {G(c,'tolerance','tolerance')} and {G(c,'fit-types','fit types')} affect the result.</p></div>
  <div><h3>Can't measure it?</h3><p>Send the part. We'll {G(c,'reverse-engineering','reverse engineer')} it in the shop or measure on site nearby.</p></div>
  <div><h3>Have a file already?</h3><p>Attach an {G(c,'stl-file','STL')}, STEP, or CAD file and we'll check it before printing.</p></div>
</div></div></section>
{cta(c, 'Ready to send it?', 'Attach your photos and measurements to a quote request. We reply with questions or a written quote.')}
</main>"""
    howto = {"@context": "https://schema.org", "@type": "HowTo", "name": "How to measure a part for a custom replacement",
             "description": "Photograph and measure a broken or discontinued part so it can be modeled and manufactured.",
             "tool": [{"@type": "HowToTool", "name": "Digital calipers"}, {"@type": "HowToTool", "name": "Ruler"}, {"@type": "HowToTool", "name": "Phone camera"}],
             "step": [{"@type": "HowToStep", "position": i + 1, "name": t, "text": re.sub("<[^>]+>", " ", h.format(**fmt)).strip()} for i, (t, h, s) in enumerate(STEPS)]}
    return B.doc(c, B.head(c, "How to Measure a Part for a Custom Replacement | True Part Fabrication",
                           "Step-by-step guide to photographing and measuring a broken or discontinued part with calipers or a ruler, including hose cuffs, holes, and hole spacing.",
                           [howto, B.crumbs_ld([("Home", ""), ("Resources", "resources/"), ("How to measure a part", "guides/how-to-measure-a-part/")])], og_type="article"), body)

# ---------------- BRAND PAGES ----------------
BRANDS = {
 "DeWalt": ("dewalt", "wet/dry vacs and dust extraction", "DeWalt wet/dry vacs come in three hose families, 1-1/4, 1-7/8, and 2-1/2 inch, and the brand's dust extractors use their own 1-1/4 inch / 35 mm connector. We make adapters, nozzles, and fittings that bridge those sizes and fit DeWalt tools to other brands' hoses."),
 "Milwaukee": ("milwaukee", "wet/dry vacs and vacuum accessories", "Milwaukee's wet/dry vacs use 1-1/4, 1-7/8, and 2-1/2 inch hoses, and its stepped attachment line spans all three. We make compatible separators, nozzles, collectors, and adapters, plus parts for its modular vac systems."),
 "RYOBI": ("ryobi", "wet/dry vacs and accessories", "RYOBI's cordless and corded wet/dry vacs mostly use 1-1/4 and 1-7/8 inch hoses, with larger models at 2-1/2 inches. We make compatible nozzles, crevice tools, adapters, and fittings."),
 "RIDGID": ("ridgid", "wet/dry vacs and accessories", "RIDGID's wet/dry vacs are built around 1-7/8 and 2-1/2 inch locking hoses. We make compatible nozzles, adapters, drain fittings, and accessories, including step-downs to smaller tool ports."),
 "Makita": ("makita", "dust extractors and wet/dry vacs", "Makita's cordless and corded dust extractors use 1 inch and 1-1/4 inch hoses, with tool cuffs in 22, 24, and 38 mm. We make adapters that join Makita hoses to other brands' tools and ports, and step-downs between Makita's own cuff sizes."),
 "Craftsman": ("craftsman", "wet/dry vacs and accessories", "Craftsman wet/dry vacs use 1-1/4, 1-7/8, and 2-1/2 inch hoses, with Pos-I-Lock fittings on the larger models. We make step adapters between those sizes, plus compatible nozzles, grips, and fittings."),
 "Shop-Vac": ("shop-vac", "wet/dry vacs and accessories", "Shop-Vac wet/dry vacs use 1-1/4, 1-1/2, 1-7/8, and 2-1/2 inch hoses, many with Lock-On ends. We make conversion adapters between those sizes and fittings that connect Shop-Vac hoses to power tools."),
 "Vacmaster": ("vacmaster", "wet/dry vacs and accessories", "Vacmaster wet/dry vacs use 1-1/4, 1-7/8, and 2-1/2 inch hoses. We make adapters between those sizes, power tool adapters, and compatible nozzles."),
 "WEN": ("wen", "dust collection and woodworking tools", "WEN's dust collectors use 4 inch hoses, and its benchtop tools have 1-1/2, 2, 2-1/2, and 4 inch dust ports. We make reducers, blast gates, elbows, separators, and adapters that tie them together."),
 "Shark": ("shark", "vacuums", "Shark uprights, cordless sticks, and robot vacuums use brand-specific wands, latches, and attachments. We make compatible crevice tools, brushes, wall mounts, and accessories."),
 "Prolux": ("prolux", "backpack and canister vacuums", "Prolux backpack and canister vacuums mostly use 1-1/2 inch (38 mm) wands and tools, the common commercial size. We make compatible floor tools, caddies, latches, and fittings."),
 "Samsung": ("samsung", "refrigerators, dishwashers, and stick vacuums", "Small plastic trim, caps, rollers, and clips on Samsung refrigerators, dishwashers, and stick vacuums break often and can be hard to buy alone. We make compatible non-food-contact replacements."),
 "Hampton Bay": ("hampton-bay", "ceiling fan remotes and accessories", "Hampton Bay ceiling fan remotes lose battery doors and wall holders. We make compatible covers and holders. We don't make fan blades, blade arms, mounts, or electrical parts."),
}
def brand_page(c, b):
    slug, cat, intro = BRANDS[b]
    items = [x for x in CAT["items"] if x["b"] == b]
    hose = [r for r in HOSE if r["b"] == b and r["g"] in ("Vacuums & collectors", "Hoses", "Power tool ports")]
    rows = "\n".join(f"""<div class="row"><div class="b">{esc(it['b'])}</div><h3 class="n" style="font:600 1rem var(--f-body);text-transform:none;letter-spacing:0"><a href="{c.link('parts/' + it['slug'] + '/')}">{esc(it['n'])}</a>{'' if it['f'] else '<span class="fitbadge">Fit to confirm</span>'}</h3><div class="o">{esc(B.rp(it))}</div><div class="f">{esc(it['f'] or 'Ask us to confirm your model')}</div><a class="btn ghost" style="height:34px;padding:0 14px;font-size:.8rem" href="{c.link('', 'quote')}" data-part="{esc(B.part_text(it))}">Request</a></div>""" for it in items)
    htab = ""
    if hose:
        trs = "".join(f'<tr><td class="mo">{esc(r["mc"])}</td><td>{esc(r["d"])}</td><td>{"".join(f"<span class=sz>{esc(s)}</span>" for s in r["s"])}</td><td><span class="cf {r["conf"] or "na"}">{esc(r["conf"] or "Unrated")}</span></td></tr>' for r in hose[:24])
        more_link = (f'<p style="margin-top:12px"><a href="{c.link("tools/hose-size-finder/")}?brand={esc(b).replace(" ","%20")}" style="color:var(--ink)">See all {len([r for r in HOSE if r["b"] == b])} {esc(b)} sizes and accessories in the finder →</a></p>')
        htab = f"""<div class="head" style="margin:72px 0 24px"><div class="label">Hose and port sizes</div><h2>{esc(b)} <em class="s">connection sizes</em></h2><p>Published hose and port sizes for {esc(b)} {esc(cat)}. See the full <a href="{c.link('tools/hose-size-finder/')}" style="color:var(--ink)">hose size finder</a> for accessories and other brands.</p></div>
<div class="ftable"><table style="min-width:640px"><thead><tr><th>Model</th><th>Item</th><th>Size</th><th>Confidence</th></tr></thead><tbody>{trs}</tbody></table></div>{more_link}"""
    body = f"""<main id="main">
{page_hero(c, [('Home',''),('Compatible parts','parts/'),(b + ' parts','brands/' + slug + '/')], f'Compatible parts for {b} {cat}', esc(intro))}
<section style="padding-block:44px 100px"><div class="wrap">
  <div class="parts-top"><h2 class="pt-h">{f"{len(items)} compatible {esc(b)} parts" if items else f"Custom {esc(b)} adapters and fittings, made to order"}</h2><span style="display:flex;gap:10px;flex-wrap:wrap"><a class="btn ghost" href="{c.link('parts/')}?brand={esc(b).replace(' ','%20')}">Filter in catalog <span class="ar">→</span></a><a class="btn ghost" href="{c.link('tools/hose-size-finder/')}?brand={esc(b).replace(' ','%20')}">{esc(b)} hose sizes <span class="ar">→</span></a></span></div>
  {f'<div class="list">{rows}</div>' if items else f'<p style="color:var(--muted);max-width:62ch">We don\'t keep a stock list for {esc(b)} yet. Every part is modeled to your hose, port, or tool. Check the sizes below, then <a href="{c.link("", "quote")}" style="color:var(--ink)">request a quote</a> with your model number.</p>'}
  {htab}
  {__import__("seo2").brand_extra(c, b)}
  {__import__("bm2").brand_models(c, b)}
  <div style="margin-top:44px"><div class="head" style="margin-bottom:14px"><div class="label">Other brands</div></div><div class="terms-strip">{''.join(f'<a href="{c.link("brands/" + v[0] + "/")}">{esc(k)}</a>' for k, v in BRANDS.items() if k != b)}</div></div>
  <p class="legal">These are compatible aftermarket parts made by True Part Fabrication, not genuine {esc(b)} parts. {esc(b)} and its model numbers are trademarks of their owner and are used only to describe fit. True Part Fabrication is not affiliated with or endorsed by {esc(b)}.</p>
</div></section>
{cta(c, f"Don't see your {esc(b)} part?", 'Send a photo and the model number. If it\'s plastic and not safety-critical, we can usually make it.')}
</main>"""
    title = f"Compatible {b} Replacement Parts & Accessories | True Part Fabrication"
    desc = f"Made-to-order aftermarket parts that fit {b} {cat}: {len(items)} compatible parts" + (", plus hose and port sizes" if hose else "") + ". Made to order in Modesto, CA, with a free reprint if it doesn't fit."
    return B.doc(c, B.head(c, title, desc, [B.crumbs_ld([("Home", ""), ("Compatible parts", "parts/"), (b + " parts", "brands/" + slug + "/")])]), body)

# ---------------- INDUSTRY PAGES ----------------
INDS = [
 ("food-processing", "Food processing", "Custom parts for food processing plants",
  "When a plastic bracket, guide, or sensor mount breaks on a processing line, waiting weeks for an OEM part means downtime. We make non-food-contact replacement and custom parts for food processing plants across the Central Valley.",
  ["Sensor and photo-eye mounts", "Line-side holders and organizers", "Guides, spacers, and bumpers", "Label and sign holders", "Cable and hose management clips", "Jigs for changeovers and setup"],
  "Everything we make for food plants stays outside the food zone. Parts that touch food or drink need certified materials and finishes, so we don't make them, and we'll tell you if a part crosses that line.",
  ["food-contact", "petg", "fixture", "small-batch-manufacturing"]),
 ("agriculture", "Agriculture", "Custom parts for farms and agricultural equipment",
  "Growers, packers, and equipment dealers in Stanislaus and San Joaquin counties lose time to small plastic parts: covers, clips, spacers, and mounts that are discontinued or sold only in big assemblies. We model and print them in materials that handle sun, dust, and heat.",
  ["Equipment covers and caps", "Clips, spacers, and bushings", "Sensor and monitor mounts", "Hose and line organizers", "Cab organizers and phone mounts", "Labels, tags, and holders"],
  "Outdoor and in-cab parts get ASA by default, so they hold up to UV and summer heat. We don't make pressurized, load-bearing, or safety-critical parts.",
  ["asa", "uv-resistance", "heat-deflection-temperature", "reverse-engineering"]),
 ("warehouse-cold-storage", "Warehouse & cold storage", "Custom parts for warehouses and cold storage",
  "Distribution centers and cold storage facilities run on small fixtures: scanner holsters, label holders, cable guides, and organizers. We make them to fit your racks, carts, and equipment, in materials that stay tough in the cold.",
  ["Scanner and handheld holsters", "Rack and bin label holders", "Cable guides and cord wraps", "Charging-station organizers", "Cart and tote accessories", "Door and dock bumpers"],
  "PLA turns brittle in freezers, so cold-room parts get PETG or carbon-fiber nylon. Tell us the temperature range and we'll pick the material.",
  ["petg", "pa-cf", "tpu", "small-batch-manufacturing"]),
 ("industrial-shops", "Industrial shops", "Jigs, fixtures, and parts for industrial and fabrication shops",
  "Machine shops, fabricators, and maintenance teams use printed jigs, fixtures, and dust collection fittings to work faster and more consistently. We build them to your drawings or from the part you need to hold.",
  ["Drilling and alignment jigs", "Assembly and inspection fixtures", "Dust collection adapters and fittings", "Tool holders and shadow boards", "Sensor covers and machine accessories", "Prototype and fit-check parts"],
  "Printed tooling is light, fast to make, and easy to revise. For high-wear or high-load tooling we use carbon-fiber nylon.",
  ["jig", "fixture", "dust-port-hose-sizes", "pa-cf"]),
]
def industry_page(c, ind):
    slug, name, h1, intro, parts, note, gl = ind
    lis = "".join(f"<li>{esc(p)}</li>" for p in parts)
    gls = "".join(f'<a href="{c.link("glossary/" + g + "/")}">{esc(B.GLOSS[g]["term"].split(" (")[0])}</a>' for g in gl)
    others = "".join(f'<a href="{c.link("industries/" + s + "/")}">{esc(n)}</a>' for s, n, *_ in INDS if s != slug)
    body = f"""<main id="main">
{page_hero(c, [('Home',''),('Resources','resources/'),(name,'industries/' + slug + '/')], h1, esc(intro))}
<section style="padding-block:56px 40px"><div class="wrap">
  <div class="biz">
    <div><div class="label" style="margin-bottom:18px">What we make</div><ul class="ind-list">{lis}</ul>
      <div class="callout" style="margin-top:32px"><div class="k">Materials &amp; limits</div><p>{esc(note)}</p></div></div>
    <div><div class="perks">
      <div><span></span><p><b>On-site measuring</b><span>For parts that can't come off the machine, anywhere from Stockton to Turlock.</span></p></div>
      <div><span></span><p><b>Written quote first</b><span>Material, price, and turnaround before we print.</span></p></div>
      <div><span></span><p><b>Reorders that match</b><span>Your model stays on file for the next run.</span></p></div>
      <div><span></span><p><b>Fit guarantee</b><span>If a part doesn't fit, we reprint it free.</span></p></div>
    </div>
    <div class="price"><div class="k">Typical business job</div><p class="n">$75 – $800+</p><small>Depends on size, material, and quantity.</small></div></div>
  </div>
  <div style="margin-top:56px"><div class="label" style="margin-bottom:14px">Related terms</div><div class="terms-strip">{gls}</div></div>
  {__import__("seo2").links_strip(c, "Related services and guides", __import__("seo2").IND_LINKS.get(slug, []))}
  <div style="margin-top:28px"><div class="label" style="margin-bottom:14px">Other industries</div><div class="terms-strip">{others}</div></div>
</div></section>
{cta(c, 'Have a part that keeps breaking?', 'Send a photo or the part itself. We\'ll reply with questions or a written quote.')}
</main>"""
    svc = {"@context": "https://schema.org", "@type": "Service", "name": h1, "serviceType": "Custom part manufacturing and replacement parts", "areaServed": B.ORG["areaServed"], "provider": {"@id": B.BASE + "/#business"}, "url": B.BASE + "/industries/" + slug + "/"}
    return B.doc(c, B.head(c, f"{h1} | Modesto & Central Valley | True Part Fabrication",
                           f"{intro[:150].rsplit(' ',1)[0]}…", [svc, B.crumbs_ld([("Home", ""), ("Resources", "resources/"), (name, "industries/" + slug + "/")])]), body)

# ---------------- RESOURCES HUB ----------------
def resources(c):
    cards = [("Tool", "Will it fit?", "Compare any two vacs, hoses, ports or accessories and see whether you need an adapter.", "tools/will-it-fit/"),
             ("Tool", "Hose & dust port size finder", f"Look up hose and port sizes for {len(HOSE)} vacs, collectors, accessories, and tools.", "tools/hose-size-finder/"),
             ("Tool", "Adapter builder", "Pick any two hose or port sizes and request an adapter made to fit both.", "tools/adapter-builder/"),
             ("Tool", "Material picker", "Answer five questions and get the right material for your part, with a full comparison chart.", "tools/material-picker/"),
             ("Guide", "How to measure a part", "Photograph and measure a broken part so it can be modeled and printed.", "guides/how-to-measure-a-part/"),
             ("Tool", "Size chart (printable)", "Every vac, collector, hose and tool port in the finder, by brand, with a page for each model.", "sizes/"),
             ("Tool", "Inch–mm converter", "Convert caliper readings and print a 1/64-inch fraction chart.", "tools/inch-mm-converter/"),
             ("Tool", "My shop", "Save your equipment and see the sizes and parts that fit it, every visit.", "my-shop/"),
             ("Guide", "Shop vac hose sizes by brand", "The common hose sizes, how to measure, and which sizes each brand uses.", "guides/shop-vac-hose-sizes/"),
             ("Guide", "Adapter fit problems and fixes", "Loose, tight, won't lock or leaking: causes and fixes.", "guides/vacuum-adapter-fit-problems/"),
             ("Updates", "What's new", "New tools, guides and size data, with a feed for feed readers.", "whats-new/"),
             ("Guide", "Replacing a discontinued plastic part", "Five ways to find or replace a part the manufacturer no longer sells.", "guides/replacing-a-discontinued-plastic-part/"),
             ("Reference", "Glossary", f"{len(B.TERMS)} plain-English definitions of printing, material, and fit terms.", "glossary/"),
             ("Reference", "FAQ", "Quotes, pricing, turnaround, the fit guarantee, and what we won't make.", "faq/"),
             ("Catalog", "Compatible parts", f"{len(CAT['items'])} made-to-order aftermarket parts, searchable by part number.", "parts/"),
             ("Catalog", "Part sets", "Tools that work together, grouped by tool family and hose size. One order, one shipping charge.", "bundles/")]
    cg = "".join(f'<a class="res" href="{c.link(p)}"><div class="k">{k}</div><h3>{esc(t)}</h3><p>{esc(d)}</p><span class="go">Open →</span></a>' for k, t, d, p in cards)
    bl = "".join(f'<a href="{c.link("brands/" + s + "/")}">{esc(b)}</a>' for b, (s, *_) in BRANDS.items())
    il = "".join(f'<a href="{c.link("industries/" + s + "/")}">{esc(n)}</a>' for s, n, *_ in INDS)
    body = f"""<main id="main">
{page_hero(c, [('Home',''),('Resources','resources/')], 'Resources for replacement and custom parts', 'Free tools, guides, and references to help you find the right size, pick the right material, and get an accurate quote the first time.')}
<div class="wrap">
  <div class="hub-sec"><h2>Tools &amp; guides</h2><div class="res-grid">{cg}</div></div>
  <div class="hub-sec"><h2>Parts by brand</h2><div class="linklist">{bl}</div></div>
  <div class="hub-sec" style="border-bottom:0"><h2>By industry</h2><div class="linklist">{il}</div></div>
</div>
{cta(c)}
</main>"""
    return B.doc(c, B.head(c, "Free Manufacturing & Replacement Part Resources | True Part Fabrication",
                           "Free hose size finder, material picker, measuring guide, glossary, and FAQ for replacement and custom manufactured parts.",
                           [B.crumbs_ld([("Home", ""), ("Resources", "resources/")])]), body)

def pages():
    p = {"resources/": resources, "tools/hose-size-finder/": hose_finder, "tools/material-picker/": material_picker, "guides/how-to-measure-a-part/": measure_guide}
    for b, (s, *_) in BRANDS.items(): p["brands/" + s + "/"] = (lambda bb: (lambda c: brand_page(c, bb)))(b)
    for ind in INDS: p["industries/" + ind[0] + "/"] = (lambda ii: (lambda c: industry_page(c, ii)))(ind)
    return p
