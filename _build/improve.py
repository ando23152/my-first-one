"""25-round improvement pass: shared CSS, JS, HTML post-processing, and the HTML site map."""
import re, html, posixpath
import build as B
esc = html.escape

IMP_CSS = r"""
/* r1: visible keyboard focus everywhere */
:focus-visible{outline:2px solid var(--accent-hi);outline-offset:3px;border-radius:4px}
.btn:focus-visible,.chip:focus-visible,.tbtn:focus-visible,.add-list:focus-visible{outline-offset:2px}
/* r2: current page in the menu */
nav.main a.l[aria-current="page"]{color:var(--ink);text-decoration:underline;text-decoration-color:var(--accent);text-underline-offset:6px;text-decoration-thickness:2px}
/* r7: opening countdown */
.opening .cd{font-weight:600}
/* r10/11: filter boxes on glossary and FAQ */
.filterbar{display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin-top:22px}
.filterbar input{flex:1;min-width:220px;max-width:460px;font:400 1rem var(--f-body);color:var(--ink);background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:0 20px;height:46px}
.filterbar .tbtn{height:46px}
.az{display:flex;flex-wrap:wrap;gap:6px;margin-top:16px}
.az a{font:500 .8rem var(--f-mono);color:var(--muted);text-decoration:none;border:1px solid var(--line);border-radius:6px;padding:4px 9px}
.az a:hover{border-color:var(--accent);color:var(--ink)}
/* r9: search */
.sres mark{background:rgba(255,138,142,.28);color:inherit;border-radius:3px;padding:0 2px}
.pop{display:flex;flex-wrap:wrap;gap:8px;margin-top:18px}
.pop span{width:100%;font:500 .7rem var(--f-mono);letter-spacing:.14em;text-transform:uppercase;color:var(--faint)}
.pop button{font:500 .85rem var(--f-body);color:var(--ink);background:none;border:1px solid var(--line);border-radius:999px;padding:7px 14px;cursor:pointer}
.pop button:hover{border-color:var(--accent)}
/* r21: sticky request bar on phones */
.stickybar{display:none}
@media (max-width:760px){.stickybar{display:flex;position:fixed;left:0;right:0;bottom:0;z-index:25;gap:10px;align-items:center;justify-content:space-between;padding:10px 16px calc(10px + env(safe-area-inset-bottom,0px));background:var(--surface);border-top:1px solid var(--line)}
  .stickybar .n{font:600 .88rem var(--f-body);color:var(--ink);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;min-width:0}
  .stickybar .btn{height:40px;padding:0 16px;font-size:.85rem;flex:none}
  body.has-sticky{padding-bottom:70px}body.has-sticky .to-top{bottom:84px}}
/* r19: what happens next */
.next{margin-top:18px;border-top:1px solid var(--line);padding-top:16px}
.next h3{font:600 .95rem var(--f-body);text-transform:none;letter-spacing:0;margin-bottom:8px}
.next ol{margin:0;padding-left:20px;color:var(--muted);display:grid;gap:4px;font-size:.92rem}
/* r18: site map page */
.smap{display:grid;grid-template-columns:repeat(3,1fr);gap:28px}
.smap h2{font-size:1rem;margin-bottom:10px}
.smap ul{list-style:none;margin:0;padding:0;display:grid;gap:6px}
.smap a{color:var(--ink);text-decoration:none;border-bottom:1px solid var(--line)}
.smap a:hover{border-color:var(--accent)}
.smap details summary{cursor:pointer;color:var(--muted);margin-top:6px}
@media (max-width:900px){.smap{grid-template-columns:1fr 1fr}}@media (max-width:560px){.smap{grid-template-columns:1fr}}
/* r16: empty-result helpers */
.empty a{color:var(--ink)}
@media print{.stickybar,.filterbar,.az,.pop,#rl-send,.rl-items button{display:none!important}.rl-items input{border:0}}
"""

IMP_JS = r"""
  // r7: opening countdown in the banner
  (function(){var o=document.querySelector('.opening .wrap');if(!o)return;var d=Math.ceil((new Date(2027,0,1)-new Date())/864e5);if(d<1)return;var es=document.documentElement.lang==='es';
    var s=document.createElement('span');s.className='cd';s.textContent=es?('· faltan '+d+(d===1?' día ':' días ')):('· '+d+(d===1?' day':' days')+' to go ');var first=o.firstChild;if(first&&first.nodeType===3){first.after(s)}})();
  // r6: keep keyboard focus inside the open phone menu
  (function(){var mn=document.getElementById('mnav'),mb=document.getElementById('menu-btn');if(!mn||!mb)return;
    document.addEventListener('keydown',function(e){if(e.key!=='Tab'||mn.hidden)return;var f=[mb].concat([].slice.call(mn.querySelectorAll('a,button')));var i=f.indexOf(document.activeElement);
      if(e.shiftKey&&(i<=0)){e.preventDefault();f[f.length-1].focus()}else if(!e.shiftKey&&i===f.length-1){e.preventDefault();f[0].focus()}});
    mb.addEventListener('click',function(){if(!mn.hidden){var a=mn.querySelector('a');if(a)setTimeout(function(){a.focus()},30)}})})();
  // r18: check the contact field looks like a phone number or email before any form sends
  document.addEventListener('submit',function(e){var f=e.target,c=f.querySelector('[id$="-contact"]');if(!c)return;var v=c.value.trim();if(!v)return;
    var ok=/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v)||(v.replace(/\D/g,'').length>=7);if(ok)return;e.preventDefault();e.stopImmediatePropagation();
    var es=document.documentElement.lang==='es',msg=es?'Escriba un teléfono o correo válido para poder responderle.':'Enter a phone number or email address we can reach you at.';
    var er=f.querySelector('[role=alert]');if(er){er.textContent=msg;er.hidden=false}c.setAttribute('aria-invalid','true');c.focus()},true);
  document.addEventListener('input',function(e){if(e.target.id&&/-contact$/.test(e.target.id))e.target.removeAttribute('aria-invalid')});
  // r21: sticky request bar on part pages (phones)
  (function(){var sb=document.querySelector('.stickybar');if(!sb)return;document.body.classList.add('has-sticky')})();
  // r12: copy a link to the current filtered view
  document.addEventListener('click',function(e){var b=e.target.closest('[data-copylink]');if(!b)return;var st=document.getElementById(b.getAttribute('data-copylink'));
    try{navigator.clipboard.writeText(location.href).then(function(){if(st)st.textContent='Link copied.'},function(){if(st)st.textContent=location.href})}catch(err){if(st)st.textContent=location.href}});
"""

NAV_PATHS = {"services/": "services/", "resources/": "resources/", "faq/": "faq/", "parts/": "parts/"}

def post(h):
    """Applied to every page after it is built."""
    m = re.search(r'<link rel="canonical" href="([^"]+)"', h)
    path = m.group(1)[len(B.BASE) + 1:] if m else ""
    # r2: mark the current section in the main menu
    sect = next((k for k in ("services/", "resources/", "faq/", "parts/", "tools/", "glossary/", "guides/", "brands/", "industries/") if path.startswith(k)), None)
    target = {"tools/": "resources/", "glossary/": "resources/", "guides/": "resources/", "brands/": "parts/", "industries/": None}.get(sect, sect)
    if target:
        def cur(mm):
            href = mm.group(1)
            res = posixpath.normpath(posixpath.join(posixpath.dirname("/" + path), href.replace("index.html", ""))).lstrip("/") + "/"
            if res == target:
                return mm.group(0).replace('<a class="l"', '<a class="l" aria-current="page"', 1)
            return mm.group(0)
        h = re.sub(r'<a class="l" href="([^"#]*)"', cur, h)
    # r24: images decode off the main thread
    h = h.replace('<img loading="lazy"', '<img loading="lazy" decoding="async"')
    h = re.sub(r'(<img(?![^>]*decoding)[^>]*loading="lazy")', r'\1 decoding="async"', h)
    # r13: result counts are announced to screen readers
    for i in ("cat-count", "hf-count"):
        h = h.replace(f'<span id="{i}" style=', f'<span id="{i}" role="status" style=')
    return h

def minify_css(css):
    # r25: smaller stylesheet
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};,>])\s*", r"\1", css)
    return css.replace(";}", "}").strip()

def sitemap_page(c, pages):
    from glossary import TERMS
    import tools as T
    L = c.link
    def ul(items): return "<ul>" + "".join(f'<li><a href="{L(p)}">{esc(t)}</a></li>' for t, p in items) + "</ul>"
    main = [("Home", ""), ("Services", "services/"), ("Pricing", "pricing/"), ("Projects", "projects/"), ("FAQ", "faq/"), ("Request a quote", "#quote"),
            ("Reorder a part", "reorder/"), ("Request list", "request-list/"), ("Search", "search/"), ("Terms of Service", "terms/"), ("Privacy", "privacy/"), ("Español", "es/")]
    main = [(t, p) if not p.startswith("#") else (t, "") for t, p in main]
    import extras as X
    svc = [(n, "services/" + s + "/") for s, n, *_ in X.SERVICES]
    tools = [("Resources hub", "resources/"), ("Hose size finder", "tools/hose-size-finder/"), ("Adapter builder", "tools/adapter-builder/"), ("Material picker", "tools/material-picker/"), ("How to measure a part", "guides/how-to-measure-a-part/"), ("Glossary", "glossary/")]
    inds = [(n, "industries/" + s + "/") for s, n, *_ in T.INDS]
    brands = [(b + " parts", "brands/" + v[0] + "/") for b, v in T.BRANDS.items()]
    terms = [(t["term"], "glossary/" + t["slug"] + "/") for t in sorted(TERMS, key=lambda t: t["term"].lower())]
    parts = sorted(B.CAT["items"], key=lambda x: (x["b"], x["n"]))
    pbrands = []
    for x in parts:
        if x["b"] not in pbrands: pbrands.append(x["b"])
    pl = "".join(f'<details><summary>{esc(b)} ({sum(1 for x in parts if x["b"] == b)})</summary>' + ul([(x["n"], "parts/" + x["slug"] + "/") for x in parts if x["b"] == b]) + "</details>" for b in pbrands)
    body = f"""<main id="main">
<div class="page-hero"><div class="wrap">{B.crumbs(c, [('Home', ''), ('Site map', 'sitemap/')])}<h1>Site map</h1><p class="lead">Every page on the site in one place.</p></div></div>
<div class="wrap" style="padding-block:48px 90px"><div class="smap">
  <div><h2>Main pages</h2>{ul(main)}</div>
  <div><h2>Services</h2>{ul(svc)}<h2 style="margin-top:24px">Industries</h2>{ul(inds)}</div>
  <div><h2>Tools and guides</h2>{ul(tools)}<h2 style="margin-top:24px">Brands</h2>{ul(brands)}</div>
  <div><h2>Parts ({len(parts)})</h2>{pl}</div>
  <div style="grid-column:span 2"><h2>Glossary ({len(terms)})</h2>{ul(terms)}</div>
</div></div>
</main>"""
    return B.doc(c, B.head(c, "Site Map | True Part Fabrication", "Every page on the True Part Fabrication website: services, tools, brands, parts, and glossary.", [B.crumbs_ld([("Home", ""), ("Site map", "sitemap/")])]), body)
