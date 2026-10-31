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
    sect = next((k for k in ("services/", "resources/", "faq/", "parts/", "tools/", "glossary/", "guides/", "brands/", "industries/", "business/", "process/", "about/", "materials/") if path.startswith(k)), None)
    target = {"tools/": "resources/", "glossary/": "resources/", "guides/": "resources/", "brands/": "parts/", "industries/": "business/", "materials/": "process/"}.get(sect, sect)
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
    main = [("Home", ""), ("Services", "services/"), ("Pricing", "pricing/"), ("Projects", "projects/"), ("FAQ", "faq/"), ("Request a quote", "quote/"), ("For business", "business/"), ("Process", "process/"), ("Materials", "materials/"), ("About", "about/"),
            ("Reorder a part", "reorder/"), ("Cart", "request-list/"), ("Search", "search/"), ("Terms of Service", "terms/"), ("Privacy", "privacy/"), ("Español", "es/")]
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

# ================= second 25-round pass =================
IMP_CSS += r"""
/* r2: hose finder table keeps its header in view */
.ftable:has(#hf){max-height:78vh;overflow:auto}
#hf thead th{position:sticky;top:0;z-index:2;background:var(--surface)}
/* r11: skip link */
.skip{position:absolute;left:-9999px;top:0;z-index:60;background:var(--accent);color:#fff;padding:10px 16px;border-radius:0 0 6px 0;font-weight:600}
.skip:focus{left:0}
/* r13: screen-reader-only text */
.sr-only{position:absolute!important;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
/* r7: description counter */
.cnt{font:400 .8rem var(--f-body);color:var(--faint);text-align:right;margin-top:4px}
/* r14/15: previous / next */
.pn{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:40px 0 0}
.pn a{display:grid;gap:4px;padding:16px 18px;border:1px solid var(--line);border-radius:8px;text-decoration:none;color:var(--ink)}
.pn a:hover{border-color:var(--accent)}
.pn a span{font:500 .7rem var(--f-mono);letter-spacing:.14em;text-transform:uppercase;color:var(--faint)}
.pn a.nx{text-align:right;grid-column:2}
@media (max-width:560px){.pn{grid-template-columns:1fr}.pn a.nx{grid-column:1}}
/* r16: search keyboard focus */
.sres a:focus-visible{outline-offset:0}
/* r25: quote checklist */
.checklist{max-width:760px}
.checklist ul{margin:10px 0 0;padding-left:20px;display:grid;gap:6px;color:var(--ink)}
/* r21: popular parts on service page */
.mini{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.mini a{display:grid;gap:4px;padding:16px;border:1px solid var(--line);border-radius:8px;text-decoration:none;color:var(--ink);background:var(--surface)}
.mini a:hover{border-color:var(--accent)}
.mini a span{font:.72rem var(--f-mono);color:var(--faint)}
@media (max-width:860px){.mini{grid-template-columns:1fr 1fr}}@media (max-width:520px){.mini{grid-template-columns:1fr}}
@media print{.pn,.cnt,.tools2{display:none!important}}
"""

IMP_JS += r"""
  // r1: clear catalog filters
  (function(){var b=document.getElementById('cat-clear');if(!b)return;b.addEventListener('click',function(){var q=document.getElementById('cat-q'),f=document.getElementById('fit-only'),s=document.getElementById('cat-sort');
    if(s&&s.value){s.value='';s.dispatchEvent(new Event('change'))}if(f&&!f.checked){f.checked=true;f.dispatchEvent(new Event('change'))}q.value='';q.dispatchEvent(new Event('input'));var all=document.querySelector('#cat-chips .chip[data-b="All"]');if(all)all.click();q.focus()})})();
  // r3/r4: adapter builder swap ends + copy spec
  (function(){var f=document.getElementById('ab');if(!f)return;var out=document.querySelector('.ab-out > div[style]');if(!out)return;
    var sw=document.createElement('button');sw.type='button';sw.className='tbtn';sw.textContent='Swap ends';
    var cp=document.createElement('button');cp.type='button';cp.className='tbtn';cp.textContent='Copy spec';
    var st=document.createElement('span');st.className='tstat';st.setAttribute('role','status');out.appendChild(sw);out.appendChild(cp);out.appendChild(st);
    sw.addEventListener('click',function(){['kind','size','fit','model'].forEach(function(k){var a=document.getElementById('a-'+k),b=document.getElementById('b-'+k),t=a.value;a.value=b.value;b.value=t});f.dispatchEvent(new Event('change'));st.textContent='Ends swapped.'});
    cp.addEventListener('click',function(){var t=document.getElementById('ab-sum').textContent;try{navigator.clipboard.writeText(t).then(function(){st.textContent='Spec copied.'},function(){st.textContent='Copy did not work in this browser.'})}catch(e){st.textContent='Copy did not work in this browser.'}})})();
  // r5: material picker answers saved in the link
  (function(){var f=document.getElementById('mp');if(!f)return;try{var P=new URLSearchParams(location.search),any=false;P.forEach(function(v,k){var r=f.querySelector('input[name="'+k+'"][value="'+v+'"]');if(r){r.checked=true;any=true}});if(any)f.dispatchEvent(new Event('change',{bubbles:true}))}catch(e){}
    f.addEventListener('change',function(){try{var p=new URLSearchParams();[].forEach.call(f.querySelectorAll('input[type=radio]:checked'),function(r){p.set(r.name,r.value)});var s=p.toString();history.replaceState(null,'',location.pathname+(s?'?'+s:''))}catch(e){}})})();
  // r6: printable measuring checklist
  (function(){var h=document.querySelector('ol.howto');if(!h)return;var d=document.createElement('div');d.className='acts2 tools2';d.style.marginBottom='18px';d.innerHTML='<button type="button" class="tbtn" data-print>Print this checklist</button>';h.parentNode.insertBefore(d,h)})();
  // r7: description length counter
  ['q-desc','e-desc'].forEach(function(id){var t=document.getElementById(id);if(!t)return;var c=document.createElement('div');c.className='cnt';c.id=id+'-cnt';t.insertAdjacentElement('afterend',c);t.setAttribute('aria-describedby',c.id);
    function u(){var n=t.value.trim().length;c.textContent=n<40?(document.documentElement.lang==='es'?'Un poco más de detalle ayuda: marca, modelo y qué se rompió.':'A little more detail helps: make, model, and what broke.'):(n+(document.documentElement.lang==='es'?' caracteres':' characters'))}t.addEventListener('input',u);u()});
  // r9: reorder link can carry a part ID
  (function(){var r=document.getElementById('r-id');if(!r)return;try{var v=new URLSearchParams(location.search).get('id');if(v&&!r.value)r.value=v}catch(e){}})();
  // r10: copyright year stays current
  (function(){var y=new Date().getFullYear();document.querySelectorAll('.copy-line span').forEach(function(s){if(/©\s*2026/.test(s.textContent)&&y>2026)s.textContent=s.textContent.replace('2026','2026–'+y)})})();
  // r16: arrow keys move through search results
  (function(){var q=document.getElementById('sq'),ul=document.getElementById('sres');if(!q||!ul)return;
    function links(){return [].slice.call(ul.querySelectorAll('a'))}
    q.addEventListener('keydown',function(e){if(e.key==='ArrowDown'){var l=links();if(l.length){e.preventDefault();l[0].focus()}}});
    ul.addEventListener('keydown',function(e){var l=links(),i=l.indexOf(document.activeElement);if(i<0)return;if(e.key==='ArrowDown'&&i<l.length-1){e.preventDefault();l[i+1].focus()}if(e.key==='ArrowUp'){e.preventDefault();if(i>0)l[i-1].focus();else q.focus()}})})();
  // r18: page-not-found suggests a search from the address
  (function(){var i=document.getElementById('nf-q');if(!i||i.value)return;var seg=location.pathname.split('/').filter(Boolean).pop()||'';seg=decodeURIComponent(seg).replace(/\.html?$/,'').replace(/[-_]+/g,' ').trim();if(seg&&seg!=='404')i.value=seg})();
  // r20: copy part number
  document.addEventListener('click',function(e){var b=e.target.closest('[data-copytext]');if(!b)return;var st=b.parentNode.querySelector('.tstat'),t=b.getAttribute('data-copytext');try{navigator.clipboard.writeText(t).then(function(){if(st)st.textContent='Copied '+t+'.'},function(){if(st)st.textContent=t})}catch(err){if(st)st.textContent=t}});
"""

_post1 = post
def post(h):
    h = _post1(h)
    # r11: skip link uses a class instead of inline script
    h = re.sub(r'<a href="#main" class="skip"[^>]*>([^<]*)</a>', r'<a href="#main" class="skip">\1</a>', h)
    # r12: referrer policy
    if 'name="referrer"' not in h:
        h = h.replace('<meta name="robots"', '<meta name="referrer" content="strict-origin-when-cross-origin">\n<meta name="robots"', 1)
    # r13: links that open a new tab say so to screen readers
    def nt(m):
        a, inner = m.group(1), m.group(2)
        if 'sr-only' in inner: return m.group(0)
        es_ = 'lang="es"' in h[:400]
        return a + inner + ('<span class="sr-only"> (se abre en una pestaña nueva)</span>' if es_ else '<span class="sr-only"> (opens in a new tab)</span>') + '</a>'
    h = re.sub(r'(<a [^>]*target="_blank"[^>]*>)(.*?)</a>', nt, h, flags=re.S)
    # r24: header logo loads first
    h = h.replace('<a class="brand" href="', '<a class="brand" data-x href="', 1)
    h = re.sub(r'(<a class="brand" data-x href="[^"]*"[^>]*>)<img ', r'\1<img fetchpriority="high" ', h, 1).replace('<a class="brand" data-x ', '<a class="brand" ', 1)
    return h

# ================= third 25-round pass =================
IMP_CSS += r"""
.swipe{display:none;font-size:.85rem;color:var(--faint);margin:0 0 8px}
@media (max-width:760px){.swipe{display:block}}
.stypes{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px}
.stypes button{font:500 .85rem var(--f-body);color:var(--ink);background:none;border:1px solid var(--line);border-radius:999px;padding:7px 14px;cursor:pointer}
.stypes button[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);color:#fff}
.faq .a .alink{font:500 .78rem var(--f-mono);color:var(--muted);text-decoration:underline;text-underline-offset:3px}
.faq details{scroll-margin-top:110px}
.noscript{border:1px solid var(--accent);border-radius:8px;padding:14px 18px;margin:18px 0;color:var(--ink)}
@media (max-width:760px){.chip,.chips button,.stypes button,.tbtn{min-height:44px}.terms-strip a,.az a{padding-block:10px}}
.rl-total{color:var(--muted);margin-top:14px}
.ab-note{color:var(--muted);font-size:.92rem;margin-top:10px}
"""

IMP_JS += r"""
  // r1/r2: catalog show-all and Esc to clear
  (function(){var more=document.getElementById('cat-more'),list=document.getElementById('plist');if(!more||!list)return;var all=document.createElement('button');all.type='button';all.className='btn ghost';all.style.marginLeft='10px';
    all.textContent=document.documentElement.lang==='es'?'Ver todas':'Show all';more.insertAdjacentElement('afterend',all);
    function sync(){all.hidden=more.hidden}new MutationObserver(sync).observe(more,{attributes:true});sync();
    all.addEventListener('click',function(){var n=0;for(var i=0;i<30&&!more.hidden;i++){more.click();n++}all.hidden=true});
    var q=document.getElementById('cat-q');if(q)q.addEventListener('keydown',function(e){if(e.key==='Escape'&&q.value){q.value='';q.dispatchEvent(new Event('input'))}})})();
  // r3/r4: hose finder clear + download view
  (function(){var t=document.getElementById('hf');if(!t)return;var row=document.querySelector('.filters .row1');if(!row)return;
    var cl=document.createElement('button');cl.type='button';cl.className='tbtn';cl.textContent='Clear filters';
    var dl=document.createElement('button');dl.type='button';dl.className='tbtn';dl.textContent='Download this view (CSV)';
    var st=document.getElementById('hf-cl');row.insertBefore(cl,st);row.insertBefore(dl,st);
    cl.addEventListener('click',function(){var q=document.getElementById('hf-q'),g=document.getElementById('hf-g');q.value='';g.value='All';['b','s'].forEach(function(k){var a=document.querySelector('.filters .chip[data-f="'+k+'"][data-v="All"]');if(a)a.click()});q.dispatchEvent(new Event('input'));g.dispatchEvent(new Event('change'))});
    dl.addEventListener('click',function(){var rows=[['Brand','Model','Item','Type','Sizes','Works with','Confidence']];[].forEach.call(t.tBodies[0].rows,function(r){if(r.hidden)return;var c=r.cells;
      rows.push([c[0].textContent,c[1].textContent,c[2].childNodes[0].textContent,r.dataset.g,[].map.call(c[3].querySelectorAll('.sz'),function(s){return s.childNodes[0].textContent}).join('; '),c[4].textContent,c[5].textContent])});
      var csv=rows.map(function(r){return r.map(function(v){v=String(v).trim();return /[",\n]/.test(v)?'"'+v.replace(/"/g,'""')+'"':v}).join(',')}).join('\r\n');
      var a=document.createElement('a');a.href=URL.createObjectURL(new Blob([csv],{type:'text/csv'}));a.download='TPF-hose-sizes.csv';document.body.appendChild(a);a.click();setTimeout(function(){URL.revokeObjectURL(a.href);a.remove()},500);if(st)st.textContent=(rows.length-1)+' rows downloaded.'})})();
  // r8/r9: dates can't be in the past; quantities are whole numbers
  (function(){var d=new Date(),iso=d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');document.querySelectorAll('input[type=date]').forEach(function(i){i.min=iso});
    document.querySelectorAll('#q-qty,#r-qty,#e-qty,#ab-qty').forEach(function(i){i.setAttribute('inputmode','numeric');i.addEventListener('change',function(){var v=i.value.replace(/[^\d]/g,'');if(i.value&&!v){i.value='1'}else if(v)i.value=String(Math.max(1,parseInt(v,10)))})})})();
  // r12: home catalog search opens the full catalog
  (function(){var f=document.getElementById('cat-full'),q=document.getElementById('cat-q');if(!f||!q||document.getElementById('plist'))return;var base=f.getAttribute('href');function u(){f.href=base+(q.value.trim()?'?q='+encodeURIComponent(q.value.trim()):'')}q.addEventListener('input',u);u()})();
  // r15: FAQ answers can be linked to directly
  (function(){var d=document.querySelectorAll('.faq details[id]');if(!d.length)return;function openHash(){var h=location.hash.slice(1);if(!h)return;var t=document.getElementById(h);if(t&&t.tagName==='DETAILS'){t.open=true;t.scrollIntoView({block:'start'})}}openHash();addEventListener('hashchange',openHash)})();
  // r21: after opening day the banner says so
  (function(){if(new Date()<new Date(2027,0,1))return;var o=document.querySelector('.opening .wrap');if(!o)return;var es=document.documentElement.lang==='es',a=o.querySelector('a');var href=a?a.getAttribute('href'):'#';
    o.innerHTML=(es?'Ya abrimos en Modesto · ':'Now open in Modesto · ')+'<a href="'+href+'">'+(es?'Pida una cotización':'Request a quote')+'</a>'})();
  // r22/r23: adapter builder notes same-size ends and shows metric
  (function(){var f=document.getElementById('ab'),sum=document.getElementById('ab-sum');if(!f||!sum)return;var MM={"15/16 in":"23.8 mm","1 in":"25.4 mm","1-1/4 in":"31.8 mm","1-3/8 in":"34.9 mm","1-1/2 in":"38.1 mm","1-3/4 in":"44.5 mm","1-7/8 in":"47.6 mm","2 in":"50.8 mm","2-1/4 in":"57.2 mm","2-1/2 in":"63.5 mm","4 in":"101.6 mm","22 mm":"0.87 in","24 mm":"0.94 in","32 mm":"1.26 in","35 mm":"1.38 in","36 mm":"1.42 in","38 mm":"1.50 in"};
    var note=document.createElement('p');note.className='ab-note';note.setAttribute('aria-live','polite');sum.insertAdjacentElement('afterend',note);
    function upd(){var a=document.getElementById('a-size').value,b=document.getElementById('b-size').value,t=[];if(a===b&&a!=='other')t.push('Both ends are the same size, so this is a straight coupler. If the ends fit differently (one over, one into), set "Fit on that end" for each.');
      [a,b].forEach(function(s,i){if(MM[s])t.push((i?'End B: ':'End A: ')+s+' = '+MM[s]+'.')});note.textContent=t.join(' ')}
    f.addEventListener('change',upd);f.addEventListener('input',upd);upd()})();
  // r25: request list shows a running total
  (function(){var ul=document.getElementById('rl-items');if(!ul)return;var tot=document.createElement('p');tot.className='rl-total';tot.setAttribute('role','status');ul.insertAdjacentElement('afterend',tot);
    function u(){var L=[];try{L=JSON.parse(localStorage.getItem('tpf-list')||'[]')}catch(e){}var n=L.reduce(function(s,x){return s+(x.q||1)},0);tot.textContent=L.length?(L.length+(L.length===1?' part, ':' parts, ')+n+(n===1?' piece in total.':' pieces in total.')):''}
    new MutationObserver(u).observe(ul,{childList:true});ul.addEventListener('change',function(){setTimeout(u,0)});u()})();
"""

GLOSS_AUTO = [("PETG", "petg"), ("ASA", "asa"), ("TPU", "tpu"), ("CAD", "cad"), ("STEP", None), ("STL", "stl-file"), ("prototypes", "prototyping"), ("Jigs", "jig"), ("jigs", "jig"), ("fixtures", "fixture"), ("brackets", "bracket"), ("Enclosures", "enclosure"), ("enclosures", "enclosure")]

_post2 = post
def post(h):
    h = _post2(h)
    m = re.search(r'<link rel="canonical" href="([^"]+)"', h)
    path = m.group(1)[len(B.BASE) + 1:] if m else ""
    # r5: hose finder table caption
    h = h.replace('<table id="hf">', '<table id="hf"><caption class="sr-only">Hose, wand, and dust port sizes by brand and model</caption>', 1)
    # r6: swipe hint on phones
    h = re.sub(r'(<div class="ftable"[^>]*><table id="hf">)', r'<p class="swipe" aria-hidden="true">Swipe the table sideways to see every column →</p>\1', h, 1)
    # r16: link glossary terms in service page cards (first mention each)
    if path.startswith("services/") and path != "services/":
        root = re.search(r'<link rel="stylesheet" href="([^"]*)assets/site\.css', h).group(1)
        done = set()
        def lk(mm):
            seg = mm.group(0)
            for word, slug in GLOSS_AUTO:
                if not slug or slug in done: continue
                new = re.sub(r'(?<![\w/>-])' + re.escape(word) + r'(?![\w<-])', f'<a href="{root}glossary/{slug}/" style="color:inherit">{word}</a>', seg, 1)
                if new != seg: done.add(slug); seg = new
            return seg
        h = re.sub(r'<div class="card"><h3>.*?</ul></div>', lk, h, flags=re.S)
    # r17: meta descriptions kept to 160 characters
    def trim(mm):
        d = html.unescape(mm.group(2))
        if len(d) <= 160: return mm.group(0)
        cut = d[:157].rsplit(" ", 1)[0].rstrip(",;:") + "…"
        return mm.group(1) + esc(cut, quote=True) + '">'
    h = re.sub(r'(<meta name="description" content=")([^"]*)">', trim, h, 1)
    h = re.sub(r'(<meta property="og:description" content=")([^"]*)">', trim, h, 1)
    # r19: tools that need scripts say so when scripts are off
    if any(path.startswith(p) for p in ("tools/", "search/", "request-list/")):
        h = h.replace('<main id="main">', '<main id="main"><noscript><div class="wrap"><p class="noscript">This tool needs JavaScript. You can still <a href="' + ('../' * path.count('/')) + 'quote/" style="color:var(--ink)">request a quote</a> and describe what you need.</p></div></noscript>', 1)
    return h
