"""Reasons to come back: model size pages, size chart, My shop, inch/mm converter,
reorder links, install-to-phone and bookmark hints, QR scan landing."""
import re, html, json
from urllib.parse import quote
import build as B
esc = html.escape

CONF_TXT = {"Confirmed": "Confirmed means a published manufacturer spec.",
            "Likely": "Likely means matched by size or rating. Measure before you order an exact-fit part.",
            "Verify": "Verify means check your product before buying; the size could not be confirmed from a published spec."}

def _T():
    import tools as T
    return T

def _slug(s):
    s = s.lower().replace("&", " and ").replace("/", " ").replace('"', " in ")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")

_ROWS = None
def rows():
    """Vacs, collectors, hoses and tool ports (not accessories), each with a page slug."""
    global _ROWS
    if _ROWS is None:
        T = _T(); seen = set(); _ROWS = []
        oems = {x["oem"] for x in B.CAT["items"] if x["oem"]}
        # every vac, collector, hose and tool port, plus accessories that aren't already a catalog part
        for r in sorted([r for r in T.HOSE if r["g"] != "Accessories" or r["mc"].split(" / ")[0] not in oems], key=lambda r: (r["b"], r["mc"])):
            s = _slug(r["b"] + " " + r["mc"])[:80]; k, base = 2, s
            while s in seen:
                s = f"{base}-{k}"; k += 1
            seen.add(s); _ROWS.append(dict(r, pslug=s))
    return _ROWS

def model_url(r): return "sizes/" + r["pslug"] + "/"
def by_mc():
    return {(r["b"], r["mc"]): r for r in rows()}

def matching_parts(brand, sizes, limit=8):
    import seo2
    S = seo2.part_sizes(); ss = set(sizes)
    same = [x for x in B.CAT["items"] if x["b"] == brand and ss & set(S.get(x["slug"], []))]
    other = [x for x in B.CAT["items"] if x["b"] != brand and x["i"] == "adapter" and ss & set(S.get(x["slug"], []))]
    same.sort(key=lambda x: (not x["f"], x["n"])); other.sort(key=lambda x: (not x["f"], x["b"]))
    out = same[:limit]
    for x in other:
        if len(out) >= limit: break
        out.append(x)
    return out

def save_btn(r, c):
    data = {"id": r["pslug"], "b": r["b"], "m": r["mc"], "d": r["d"], "s": r["s"], "u": c.link(model_url(r))}
    return f'<button type="button" class="tbtn shop-save" data-shop-save="{esc(json.dumps(data))}" aria-pressed="false">Save to My shop</button>'

HINT = '<p class="bm-hint" data-bm-hint>Use this often? <span class="bm-keys">Bookmark it</span> so it\'s one click away next time.<button type="button" class="bm-install" hidden>Add to home screen</button><button type="button" class="bm-phone" data-phone-qr aria-expanded="false" hidden>Open on your phone</button></p>'

def model_page(c, r):
    T = _T(); path = model_url(r); b, mc = r["b"], r["mc"]
    bslug = T.BRANDS.get(b, (None,))[0]
    sizes = "".join(f'<span class="sz">{esc(s)}</span> ' for s in r["s"])
    conf = r["conf"] or "Verify"
    spec = [("Brand", f'<a href="{c.link("brands/" + bslug + "/")}">{esc(b)}</a>' if bslug else esc(b)), ("Model", f'<b style="font-family:var(--f-mono);font-weight:500">{esc(mc)}</b>'),
            ("Item", esc(r["d"])), ("Type", esc(r["g"])), ("Size", sizes)]
    if r.get("c"): spec.append(("Hose / connector", esc(r["c"])))
    if r.get("w"): spec.append(("Works with", esc(r["w"])))
    spec.append(("Size confidence", f'<span class="cf {esc(conf)}">{esc(conf)}</span> <span style="color:var(--muted);font-size:.9rem">{esc(CONF_TXT.get(conf, ""))}</span>'))
    dl = "".join(f"<div><dt>{k}</dt><dd>{v}</dd></div>" for k, v in spec)
    parts = matching_parts(b, r["s"])
    pl = "".join(f'<a href="{c.link("parts/" + x["slug"] + "/")}">{esc(x["n"])}<span>{esc(B.rp(x))}</span></a>' for x in parts)
    a0 = quote(r["s"][0]); am = quote(b + " " + mc)
    same_b = [x for x in rows() if x["b"] == b and x is not r][:10]
    ob = "".join(f'<a href="{c.link(model_url(x))}">{esc(x["mc"])}</a>' for x in same_b)
    sz_txt = " and ".join(r["s"])
    lead = f'{esc(b)} {esc(mc)} ({esc(r["d"])}) uses {esc(sz_txt)}. {esc(CONF_TXT.get(conf, ""))}'
    body = f"""<main id="main" data-model="{esc(json.dumps({'u': model_url(r), 'n': b + ' ' + mc, 's': r['s']}))}">
<div class="page-hero"><div class="wrap">
  {B.crumbs(c, [('Home', ''), ('Hose size finder', 'tools/hose-size-finder/'), ('Size chart', 'sizes/'), (b + ' ' + mc, path)])}
  <h1>{esc(b)} {esc(mc)} hose and port size<span class="h1sub">{esc(sz_txt)}</span></h1>
  <p class="lead">{lead}</p>
</div></div>
<div class="wrap" style="padding-block:36px 80px">
  <div class="pp" style="display:block"><dl class="spec" style="margin:0;max-width:860px">{dl}</dl></div>
  <div class="acts2" style="margin-top:18px">{save_btn(r, c)}<button type="button" class="tbtn" data-print>Print</button><button type="button" class="tbtn" data-share data-title="{esc(b + ' ' + mc + ' hose size')}">Share</button><a class="tbtn" href="{c.link('sizes/')}">Full size chart</a></div>
  {HINT}
  <section class="about-part prose" style="margin-top:34px;padding:0"><h2>Need to connect it to something else?</h2><p>The <a href="{c.link('tools/adapter-builder/')}?a={a0}&amp;am={am}">adapter builder</a> starts with this size filled in. Pick the other end and we make an adapter that fits both. Not sure of the other size? Look it up in the <a href="{c.link('tools/hose-size-finder/')}?brand={quote(b)}">hose size finder</a> or measure it with the <a href="{c.link('tools/inch-mm-converter/')}">inch–mm converter</a>.</p></section>
  {f'<div class="head" style="margin:40px 0 22px"><div class="label">Parts in this size</div></div><div class="rel">{pl}</div>' if pl else ''}
  {__import__("bm2").same_size_models(c, r)}
  {f'<div class="head" style="margin:40px 0 18px"><div class="label">Other {esc(b)} models</div></div><div class="terms-strip">{ob}</div>' if ob else ''}
  <p class="legal" style="margin-top:44px">Sizes are from published specs where marked Confirmed. {esc(b)} and its model numbers are trademarks of their owner, used only to describe fit. True Part Fabrication is not affiliated with {esc(b)}.</p>
</div>
</main>"""
    nm = mc if mc.lower().startswith(b.lower()) else f"{b} {mc}"
    dup = sum(1 for x in rows() if x["b"] == b and x["mc"] == mc) > 1
    title = (f"{nm}: {re.sub(r"\s*\([^)]*$", "", (r['d'][:34].rsplit(' ', 1)[0] if len(r['d']) > 34 else r['d'])).rstrip(' ,(/')} Size" if dup else f"{nm} Hose Size: {', '.join(r['s'])}")
    desc = f"{b} {mc} {r['d'][:60].rstrip()}: {sz_txt} hose and port size, connector details, matching adapters and parts. Free size lookup from True Part Fabrication."
    return B.doc(c, B.head(c, title + " | True Part Fabrication", desc,
                           [B.crumbs_ld([("Home", ""), ("Hose size finder", "tools/hose-size-finder/"), ("Size chart", "sizes/"), (b + " " + mc, path)])]), body)

def size_chart(c):
    T = _T(); out = []
    for b, (slug, *_r) in T.BRANDS.items():
        rs = [r for r in rows() if r["b"] == b]
        if not rs: continue
        trs = "".join(f'<tr><td class="mo"><a href="{c.link(model_url(r))}">{esc(r["mc"])}</a></td><td>{esc(r["d"])}</td><td>{"".join(f"<span class=sz>{esc(s)}</span> " for s in r["s"])}</td><td><span class="cf {esc(r["conf"] or "na")}">{esc(r["conf"] or "")}</span></td></tr>' for r in rs)
        out.append(f'<h2 id="{slug}">{esc(b)}</h2><div class="ftable"><table><thead><tr><th>Model</th><th>Item</th><th>Size</th><th>Confidence</th></tr></thead><tbody>{trs}</tbody></table></div>')
    jump = "".join(f'<a href="#{s}">{esc(b)}</a>' for b, (s, *_r) in T.BRANDS.items() if any(r["b"] == b for r in rows()))
    body = f"""<main id="main">
<div class="page-hero"><div class="wrap">
  {B.crumbs(c, [('Home', ''), ('Hose size finder', 'tools/hose-size-finder/'), ('Size chart', 'sizes/')])}
  <h1>Shop vac hose and port size chart</h1>
  <p class="lead">Every vacuum, dust collector, hose and power tool port in our size finder, {len(rows())} models by brand. Print it for the shop, or tap a model for its own page.</p>
</div></div>
<div class="wrap chart" style="padding-block:30px 80px">
  <div class="acts2"><button type="button" class="tbtn" data-print>Print the chart</button><a class="tbtn" href="{c.link('tools/hose-size-finder/')}">Search the size finder</a><a class="tbtn" href="{c.link('tools/inch-mm-converter/')}">Inch–mm converter</a></div>
  {HINT}
  <div class="dl-links"><a class="tbtn" href="{c.asset('downloads/TPF-shop-vac-size-chart.pdf')}" download>Download the chart (PDF)</a><a class="tbtn" href="{c.asset('downloads/TPF-fraction-to-mm-chart.pdf')}" download>Fraction to mm chart (PDF)</a></div>
  <div class="chart-q"><label for="chart-q" style="font:500 .7rem var(--f-mono);letter-spacing:.12em;text-transform:uppercase;color:var(--faint)">Filter the chart</label><input id="chart-q" type="search" placeholder="Model, brand or size" autocomplete="off"><span id="chart-n" role="status" style="color:var(--muted);font-size:.9rem"></span></div>
  <nav class="terms-strip" aria-label="Brands" style="margin:18px 0 10px">{jump}</nav>
  <p style="color:var(--muted);margin:10px 0 0">By size: {" ".join(f'<a href="{c.link(__import__("bm2").size_url(z))}" style="color:var(--ink)">{esc(z)}</a>' for z in __import__("bm2").sizes_used())}</p>
  {''.join(out)}
  <p style="margin-top:30px;color:var(--muted)">Missing a model? <a href="mailto:{__import__('extras').QUOTE_TO}?subject=Size%20chart%3A%20missing%20model&amp;body=Brand%3A%20%0AModel%3A%20%0AWhat%20it%20is%20(vac%2C%20hose%2C%20tool)%3A%20%0AMeasured%20size%20(if%20known)%3A%20" style="color:var(--ink)">Tell us the brand and model</a> and we'll add it.</p>
  <p class="legal" style="margin-top:36px">Confirmed: published manufacturer spec. Likely: matched by size or rating. Verify: check your product before buying. Brand names are trademarks of their owners, used only to describe fit.</p>
</div>
</main>"""
    return B.doc(c, B.head(c, "Shop Vac Hose & Port Size Chart (Printable) | True Part Fabrication",
                           f"Printable hose and dust port size chart for {len(rows())} wet/dry vacs, dust collectors, hoses and power tools from DeWalt, Milwaukee, RYOBI, RIDGID, WEN and more.",
                           [{"@context": "https://schema.org", "@type": "Dataset", "name": "Shop vac hose and dust port sizes", "description": f"Hose, wand and dust port sizes for {len(rows())} wet/dry vacuums, dust collectors, hoses and power tools, with a confidence rating for each.", "url": B.BASE + "/sizes/", "creator": {"@id": B.BASE + "/#business"}, "isAccessibleForFree": True, "keywords": ["shop vac hose size", "dust port size", "wet/dry vacuum", "dust collector"], "distribution": [{"@type": "DataDownload", "encodingFormat": "application/pdf", "contentUrl": B.BASE + "/assets/downloads/TPF-shop-vac-size-chart.pdf"}]},
                            B.crumbs_ld([("Home", ""), ("Hose size finder", "tools/hose-size-finder/"), ("Size chart", "sizes/")])]), body)

# ---------- My shop ----------
def my_shop(c):
    import seo2
    S = seo2.part_sizes()
    cat = [{"s": x["slug"], "n": x["n"], "b": x["b"], "r": B.rp(x), "z": S.get(x["slug"], []), "a": x["i"] == "adapter", "f": bool(x["f"]), "u": c.link("parts/" + x["slug"] + "/")} for x in B.CAT["items"]]
    eq = {r["pslug"]: {"id": r["pslug"], "b": r["b"], "m": r["mc"], "d": r["d"], "s": r["s"], "u": c.link(model_url(r))} for r in rows()}
    body = f"""<main id="main">
<div class="page-hero"><div class="wrap">
  {B.crumbs(c, [('Home', ''), ('My shop', 'my-shop/')])}
  <h1>My shop</h1>
  <p class="lead">Save the vacs, dust collectors and tools you own. We show the sizes and the parts and adapters that fit them, every time you come back. Saved on this device only; no account needed.</p>
</div></div>
<div class="wrap ms-wrap" style="padding-block:36px 80px">
  {HINT}
  <section aria-labelledby="ms-eq"><h2 id="ms-eq" style="font-size:1.3rem;margin:10px 0 14px">Your equipment</h2>
  <div id="ms-list" class="ms-list"></div>
  <p id="ms-empty" style="color:var(--muted)" hidden>Nothing saved yet. Find your model in the <a href="{c.link('sizes/')}" style="color:var(--ink)">size chart</a> or the <a href="{c.link('tools/hose-size-finder/')}" style="color:var(--ink)">hose size finder</a> and tap <b>Save to My shop</b>.</p>
  <form class="ms-add" id="ms-add" role="search" style="margin-top:18px"><label for="ms-q">Add equipment by model number</label><div style="display:flex;gap:10px;flex-wrap:wrap"><input id="ms-q" list="ms-dl" placeholder="e.g. WD4070, DCA016" autocomplete="off"><button class="btn ghost" type="submit">Add</button></div><datalist id="ms-dl"></datalist><p class="xerr" id="ms-err" role="alert" hidden></p></form>
  </section>
  <section aria-labelledby="ms-fit" id="ms-fit-sec" hidden><h2 id="ms-fit" style="font-size:1.3rem;margin:44px 0 14px">Parts and adapters that fit</h2><div class="rel" id="ms-parts"></div></section>
  <section aria-labelledby="ms-rv" id="ms-rv-sec" hidden><h2 id="ms-rv" style="font-size:1.3rem;margin:44px 0 14px">Recently viewed</h2><div class="terms-strip" id="ms-rv-list"></div></section>
  <section aria-labelledby="ms-ro"><h2 id="ms-ro" style="font-size:1.3rem;margin:44px 0 10px">Reorder</h2>
  <p style="color:var(--muted);max-width:62ch">Ordered from us before? Use your part ID on the <a href="{c.link('reorder/')}" style="color:var(--ink)">reorder page</a>. Your <a href="{c.link('request-list/')}" style="color:var(--ink)">cart</a> can also make a reorder link to bookmark or send to whoever does the buying.</p></section>
  <div class="acts2" style="margin-top:26px"><button type="button" class="tbtn" id="ms-share">Copy a link to my equipment list</button><button type="button" class="tbtn" id="ms-clear">Clear My shop</button><span id="ms-st" role="status" style="color:var(--muted);font-size:.9rem"></span></div>
</div>
</main>
<script>
(function(){{
  var CAT={json.dumps(cat, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')},EQ={json.dumps(eq, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')};
  var K='tpf-shop',st=document.getElementById('ms-st');
  function get(){{try{{return JSON.parse(localStorage.getItem(K)||'[]')}}catch(e){{return []}}}}
  function set(a){{try{{localStorage.setItem(K,JSON.stringify(a))}}catch(e){{}}}}
  var P=new URLSearchParams(location.search).get('e');
  if(P){{var L=get(),n=0;P.split(',').forEach(function(id){{if(EQ[id]&&!L.some(function(x){{return x.id===id}})){{L.push(EQ[id]);n++}}}});set(L);st.textContent=n?n+' item'+(n===1?'':'s')+' added from the link.':'';history.replaceState(null,'',location.pathname)}}
  var dl=document.getElementById('ms-dl');Object.keys(EQ).forEach(function(k){{var o=document.createElement('option');o.value=EQ[k].b+' '+EQ[k].m;dl.appendChild(o)}});
  function draw(){{var L=get(),box=document.getElementById('ms-list');box.textContent='';document.getElementById('ms-empty').hidden=L.length>0;
    L.forEach(function(x,i){{var d=document.createElement('div');d.className='ms-item';var a=document.createElement('a');a.href=x.u;a.textContent=x.b+' '+x.m;var p=document.createElement('p');p.textContent=x.d;var z=document.createElement('div');x.s.forEach(function(s){{var sp=document.createElement('span');sp.className='sz';sp.textContent=s;z.appendChild(sp);z.appendChild(document.createTextNode(' '))}});
      var ab=document.createElement('a');ab.className='ms-ab';ab.href='{c.link('tools/adapter-builder/')}?a='+encodeURIComponent(x.s[0])+'&am='+encodeURIComponent(x.b+' '+x.m);ab.textContent='Get an adapter';
      var rm=document.createElement('button');rm.type='button';rm.textContent='Remove';rm.setAttribute('aria-label','Remove '+x.b+' '+x.m);rm.addEventListener('click',function(){{var A=get();A.splice(i,1);set(A);draw();st.textContent='Removed.'}});
      d.appendChild(a);d.appendChild(p);d.appendChild(z);d.appendChild(ab);d.appendChild(rm);box.appendChild(d)}});
    var sizes={{}},brands={{}};L.forEach(function(x){{brands[x.b]=1;x.s.forEach(function(s){{sizes[s]=1}})}});
    var fit=CAT.filter(function(p){{return p.z.some(function(s){{return sizes[s]}})&&(brands[p.b]||p.a)}}).sort(function(a,b){{return (brands[b.b]?1:0)-(brands[a.b]?1:0)||(b.f-a.f)}}).slice(0,18);
    var pb=document.getElementById('ms-parts');pb.textContent='';document.getElementById('ms-fit-sec').hidden=!fit.length;
    fit.forEach(function(p){{var a=document.createElement('a');a.href=p.u;a.textContent=p.n;var s=document.createElement('span');s.textContent=p.r+' · '+p.z.join(', ');a.appendChild(s);pb.appendChild(a)}})}}
  document.getElementById('ms-add').addEventListener('submit',function(e){{e.preventDefault();var q=document.getElementById('ms-q').value.trim().toLowerCase().replace(/\\s+/g,' '),er=document.getElementById('ms-err');if(!q)return;
    var hit=Object.keys(EQ).map(function(k){{return EQ[k]}}).filter(function(x){{var n=(x.b+' '+x.m).toLowerCase();return n===q||x.m.toLowerCase()===q||n.indexOf(q)>-1}});
    if(!hit.length){{er.textContent='No model matches that. Try the size finder, or ask us to look it up.';er.hidden=false;return}}er.hidden=true;
    var L=get(),x=hit[0];if(!L.some(function(y){{return y.id===x.id}}))L.push(x);set(L);document.getElementById('ms-q').value='';draw();st.textContent='Added '+x.b+' '+x.m+'.'}});
  document.getElementById('ms-clear').addEventListener('click',function(){{set([]);draw();st.textContent='Cleared.'}});
  document.getElementById('ms-share').addEventListener('click',function(){{var L=get();if(!L.length){{st.textContent='Save some equipment first.';return}}var u=location.origin+location.pathname+'?e='+L.map(function(x){{return x.id}}).join(',');
    try{{navigator.clipboard.writeText(u).then(function(){{st.textContent='Link copied. Bookmark it or send it to your team.'}},function(){{st.textContent=u}})}}catch(e){{st.textContent=u}}}});
  draw();
  (function(){{var R='{c.link('')}',L=[],P=[];try{{L=JSON.parse(localStorage.getItem('tpf-recent-models')||'[]');P=JSON.parse(localStorage.getItem('tpf-recent')||'[]')}}catch(e){{}}
    var box=document.getElementById('ms-rv-list');L.forEach(function(x){{var a=document.createElement('a');a.href=R+x.u;a.textContent=x.n+' ('+x.s.join(', ')+')';box.appendChild(a)}});
    P.slice(0,6).forEach(function(x){{if(!x.u||!x.n)return;var a=document.createElement('a');a.href=x.u;a.textContent=x.n;box.appendChild(a)}});document.getElementById('ms-rv-sec').hidden=!box.children.length}})();
}})();
</script>"""
    return B.doc(c, B.head(c, "My shop: your saved equipment | True Part Fabrication", "Save your vacs, dust collectors and tools to see their sizes and the parts and adapters that fit, every time you come back.", []), body)

# ---------- Inch / mm converter ----------
def converter(c):
    from fractions import Fraction
    rows_ = []
    for n in range(1, 65):
        f = Fraction(n, 64);
        rows_.append(f'<tr><td>{f.numerator}/{f.denominator}</td><td>{float(f):.4f}</td><td>{float(f)*25.4:.2f}</td></tr>')
    common = [("1 in", 1), ("1-1/4 in", 1.25), ("1-3/8 in", 1.375), ("1-1/2 in", 1.5), ("1-7/8 in", 1.875), ("2 in", 2), ("2-1/4 in", 2.25), ("2-1/2 in", 2.5), ("4 in", 4)]
    crow = "".join(f'<tr><td>{n}</td><td>{v:.3f}</td><td>{v*25.4:.1f}</td></tr>' for n, v in common)
    body = f"""<main id="main">
<div class="page-hero"><div class="wrap">
  {B.crumbs(c, [('Home', ''), ('Resources', 'resources/'), ('Inch–mm converter', 'tools/inch-mm-converter/')])}
  <h1>Inch to mm converter and fraction chart</h1>
  <p class="lead">Convert caliper readings between inches, fractions and millimeters, find the nearest fraction, and print a 1/64-inch chart for the shop.</p>
</div></div>
<div class="wrap" style="padding-block:34px 80px">
  {HINT}
  <form class="xform conv" id="cv" data-nodraft onsubmit="return false" style="max-width:760px">
    <label for="cv-in">Inches (decimal or fraction, e.g. 1-7/8)<input id="cv-in" inputmode="decimal" autocomplete="off" placeholder="1-7/8"></label>
    <label for="cv-mm">Millimeters<input id="cv-mm" inputmode="decimal" autocomplete="off" placeholder="47.6"></label>
    <div class="full cv-out" id="cv-out" role="status" aria-live="polite">Type a value in either box.</div>
  </form>
  <div class="cv-grid">
    <section><h2>Common hose sizes</h2><div class="ftable"><table><thead><tr><th>Nominal</th><th>Inches</th><th>mm</th></tr></thead><tbody>{crow}</tbody></table></div>
      <p style="color:var(--muted);font-size:.9rem;margin-top:10px">Nominal hose sizes are names, not exact measurements. See <a href="{c.link('guides/shop-vac-hose-sizes/')}" style="color:var(--ink)">shop vac hose sizes</a>.</p></section>
    <section><h2>Fractions of an inch (1/64 to 1)</h2><div class="acts2" style="margin-bottom:10px"><button type="button" class="tbtn" data-print>Print the chart</button><a class="tbtn" href="{c.asset('downloads/TPF-fraction-to-mm-chart.pdf')}" download>Download PDF</a></div><div class="ftable"><table><thead><tr><th>Fraction</th><th>Decimal in</th><th>mm</th></tr></thead><tbody>{''.join(rows_)}</tbody></table></div></section>
  </div>
</div>
</main>
<script>
(function(){{
  var i=document.getElementById('cv-in'),m=document.getElementById('cv-mm'),o=document.getElementById('cv-out');
  function parse(s){{s=s.trim().replace(/["\\u201d]|in(ch(es)?)?\\.?$/i,'').trim();if(!s)return NaN;var w=0,mt=s.match(/^(\\d+)[\\s-]+(\\d+)\\/(\\d+)$/);if(mt)return +mt[1]+mt[2]/mt[3];mt=s.match(/^(\\d+)\\/(\\d+)$/);if(mt)return mt[1]/mt[2];return parseFloat(s.replace(',','.'))}}
  function frac(x){{var w=Math.floor(x),n=Math.round((x-w)*64),d=64;if(n===64){{w++;n=0}}while(n&&n%2===0){{n/=2;d/=2}}return (w?w+(n?'-':''):'')+(n?n+'/'+d:(w?'':'0'))+' in'}}
  function show(inch){{if(!isFinite(inch)||inch<=0){{o.textContent='Type a value in either box.';return}}var nf=frac(inch),err=Math.abs(inch-parse(nf.replace(' in','')))*25.4;
    o.innerHTML='';var b=document.createElement('b');b.textContent=inch.toFixed(4)+' in = '+(inch*25.4).toFixed(2)+' mm';o.appendChild(b);o.appendChild(document.createTextNode(' · Nearest 1/64: '+nf+(err>0.005?' ('+(err).toFixed(2)+' mm off)':' (exact)')))}}
  i.addEventListener('input',function(){{var v=parse(i.value);if(isFinite(v))m.value=(v*25.4).toFixed(2);else if(!i.value)m.value='';show(v)}});
  m.addEventListener('input',function(){{var v=parseFloat(m.value.replace(',','.'))/25.4;if(isFinite(v))i.value=v.toFixed(4);else if(!m.value)i.value='';show(v)}});
}})();
</script>"""
    app = {"@context": "https://schema.org", "@type": "WebApplication", "name": "Inch to mm converter and fraction chart", "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}, "url": B.BASE + "/tools/inch-mm-converter/"}
    return B.doc(c, B.head(c, "Inch to mm Converter & Fraction Chart (1/64 in) | True Part Fabrication",
                           "Convert inches, fractions and millimeters, find the nearest 1/64-inch fraction, and print a fraction-to-mm chart and common hose size table.",
                           [app, B.crumbs_ld([("Home", ""), ("Resources", "resources/"), ("Inch–mm converter", "tools/inch-mm-converter/")])]), body)

def pages():
    p = {"sizes/": size_chart, "my-shop/": my_shop, "tools/inch-mm-converter/": converter}
    for r in rows():
        p[model_url(r)] = (lambda rr: (lambda c: model_page(c, rr)))(r)
    return p

# ---------- site-wide script: save buttons, bookmark hint, install, reorder links, QR landing, offline ----------
JS = r"""
  // ---- My shop save buttons ----
  (function(){var K='tpf-shop';function get(){try{return JSON.parse(localStorage.getItem(K)||'[]')}catch(e){return []}}function set(a){try{localStorage.setItem(K,JSON.stringify(a))}catch(e){}}
    function sync(){var L=get();document.querySelectorAll('[data-shop-save]').forEach(function(b){var d=JSON.parse(b.getAttribute('data-shop-save')),on=L.some(function(x){return x.id===d.id});b.setAttribute('aria-pressed',on);b.textContent=on?'✓ In My shop':'Save to My shop'})}
    document.addEventListener('click',function(e){var b=e.target.closest('[data-shop-save]');if(!b)return;var d=JSON.parse(b.getAttribute('data-shop-save')),L=get(),i=L.findIndex(function(x){return x.id===d.id});if(i>-1)L.splice(i,1);else L.push(d);set(L);sync();
      var lv=document.getElementById('list-live');if(lv)lv.textContent=i>-1?'Removed from My shop.':'Saved to My shop.'});sync()})();
  // ---- bookmark hint + install ----
  (function(){var hs=document.querySelectorAll('[data-bm-hint]');if(!hs.length)return;var mac=/Mac|iPhone|iPad/.test(navigator.platform||navigator.userAgent),ios=/iPhone|iPad|iPod/.test(navigator.userAgent),touch=matchMedia('(pointer:coarse)').matches;
    var standalone=matchMedia('(display-mode: standalone)').matches||navigator.standalone;if(standalone){hs.forEach(function(h){h.hidden=true});return}
    hs.forEach(function(h){var k=h.querySelector('.bm-keys');if(ios)k.textContent='Tap Share, then Add to Home Screen,';else if(!touch)k.textContent='Bookmark it (press '+(mac?'⌘D':'Ctrl+D')+')'});
    var dp=null;addEventListener('beforeinstallprompt',function(e){e.preventDefault();dp=e;document.querySelectorAll('.bm-install').forEach(function(b){b.hidden=false})});
    document.addEventListener('click',function(e){var b=e.target.closest('.bm-install');if(!b||!dp)return;dp.prompt();dp.userChoice.then(function(){dp=null;document.querySelectorAll('.bm-install').forEach(function(x){x.hidden=true})})})})();
  // ---- QR scan landing on part pages ----
  (function(){try{if(new URLSearchParams(location.search).get('ref')!=='qr')return}catch(e){return}var h=document.querySelector('.page-hero .wrap');if(!h)return;
    var n=document.createElement('div');n.className='qr-note';n.setAttribute('role','note');n.innerHTML='Thanks for scanning. To reorder this part, tap <b>Request this part</b> or <b>+ Add to cart</b> below. Save the page to your home screen for next time.';h.appendChild(n)})();
  // ---- offline support (not inside previews) ----
  if('serviceWorker' in navigator&&location.protocol==='https:'&&!/claude|anthropic|usercontent/.test(location.hostname)){addEventListener('load',function(){navigator.serviceWorker.register('/sw.js').catch(function(){})})}
"""

SW = r"""// True Part Fabrication: offline support. Pages: network first, then cache. Assets: cache first.
const V = 'tpf-@@V@@';
const PRE = ['/', '/tools/hose-size-finder/', '/sizes/', '/my-shop/', '/tools/inch-mm-converter/', '/tools/will-it-fit/', '/request-list/', '/assets/models.json'];
self.addEventListener('install', e => { e.waitUntil(caches.open(V).then(c => c.addAll(PRE)).catch(() => {})); self.skipWaiting(); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== V).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  const r = e.request; if (r.method !== 'GET') return;
  const u = new URL(r.url); if (u.origin !== location.origin) return;
  if (r.mode === 'navigate' || (r.headers.get('accept') || '').includes('text/html')) {
    e.respondWith(fetch(r).then(res => { const cp = res.clone(); if (res.ok) caches.open(V).then(c => c.put(r, cp)); return res; })
      .catch(() => caches.match(r).then(m => m || caches.match('/')).then(m => m || new Response('<h1>Offline</h1><p>You are offline. Pages you opened before are still available.</p>', {headers: {'Content-Type': 'text/html'}}))));
    return;
  }
  if (u.pathname.startsWith('/assets/')) {
    e.respondWith(caches.match(r).then(m => m || fetch(r).then(res => { const cp = res.clone(); if (res.ok) caches.open(V).then(c => c.put(r, cp)); return res; })));
  }
});
"""

CSS = """
.bm-hint{display:flex;flex-wrap:wrap;align-items:center;gap:8px 12px;margin:18px 0 0;padding:10px 14px;border:1px dashed var(--line);border-radius:10px;color:var(--muted);font-size:.9rem;max-width:760px}
.bm-hint .bm-keys{color:var(--ink);font-weight:600}
.bm-install{font:600 .82rem var(--f-body);color:#fff;background:var(--accent);border:0;border-radius:999px;padding:7px 14px;cursor:pointer}
.shop-save[aria-pressed="true"]{border-color:var(--accent)}
.ms-list{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px}
.ms-item{border:1px solid var(--line);border-radius:12px;padding:16px;background:var(--surface)}
.ms-item>a:first-child{color:var(--ink);font-weight:600;text-decoration:none}
.ms-item>a:first-child:hover{text-decoration:underline}
.ms-item p{color:var(--muted);font-size:.9rem;margin:6px 0 10px}
.ms-item .ms-ab{display:inline-block;margin:12px 12px 0 0;color:var(--ink);font-size:.88rem}
.ms-item button{margin-top:12px;background:none;border:1px solid var(--line);color:var(--ink);border-radius:999px;height:32px;padding:0 12px;cursor:pointer;font:600 .78rem var(--f-body)}
.ms-wrap section{padding:0}
.ms-add{display:block;padding:0;border:0;background:none;max-width:none}
.ms-add label{display:block;font:500 .7rem var(--f-mono);letter-spacing:.12em;text-transform:uppercase;color:var(--faint);margin-bottom:8px}
.ms-add input{font:400 1rem var(--f-body);color:var(--ink);background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:10px 12px;min-width:min(320px,100%)}
.qr-note{margin-top:18px;padding:12px 16px;border-left:3px solid var(--accent);background:var(--surface);color:var(--ink);max-width:640px}
.conv{grid-template-columns:1fr 1fr}
.cv-out{font-size:1.05rem;color:var(--muted);padding:12px 0}
.cv-out b{color:var(--ink)}
.cv-grid{display:grid;grid-template-columns:1fr 1fr;gap:40px;margin-top:30px;align-items:start}
.cv-grid h2,.chart h2{font-size:1.2rem;margin:26px 0 12px}
.cv-grid>section{min-width:0;padding:0}
.cv-grid table{min-width:0!important;width:100%}
.cv-grid .ftable,.chart .ftable{position:relative;overflow-x:auto;max-width:100%}
.chart td a{color:var(--ink)}
@media (max-width:760px){.cv-grid,.conv{grid-template-columns:1fr}}
@media print{.bm-hint,.acts2,.qr-note,nav.terms-strip{display:none!important}.chart .ftable,.cv-grid .ftable{overflow:visible}}
"""
