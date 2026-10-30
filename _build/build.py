#!/usr/bin/env python3
"""Build the True Part Fabrication multi-page site.
Outputs:
  /home/claude/site/        -> Render (full documents, clean URLs)
  /home/claude/site_art/    -> claude.ai artifact preview (index has no doctype; links use index.html)
Set BASE to the real domain and INDEX=True when the site goes live on its own domain.
"""
import json, re, html, os, shutil, sys
sys.path.insert(0, os.path.dirname(__file__))
from glossary import TERMS

BASE = "https://truepart-fabrication.onrender.com"
INDEX = False          # False while on the temporary Render address: pages carry noindex
SITE = "True Part Fabrication"
EMAIL = "nsottero@gmail.com"
EBAY = "https://www.ebay.com/usr/sottero"
SRC = "/home/claude/site_src"
TPL = open("/home/claude/v2/template.html").read()
CAT = json.load(open("/home/claude/site/catalog.json"))
esc = html.escape

EXTRA_CSS = r"""
/* ---- base reset for standalone pages ---- */
:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
body{margin:0}img{max-width:100%}[hidden]{display:none!important}
/* ---- multi-page additions ---- */
.crumbs{font:500 .72rem var(--f-mono);letter-spacing:.12em;text-transform:uppercase;color:var(--faint);display:flex;gap:10px;flex-wrap:wrap}
.crumbs a{color:var(--muted);text-decoration:none}.crumbs a:hover{color:var(--ink)}
.page-hero{padding-block:72px 40px;border-bottom:1px solid var(--line)}
.page-hero h1{font-size:clamp(1.8rem,3.4vw,2.8rem);margin-top:18px;max-width:22ch}
.page-hero p.lead{color:var(--muted);font-size:1.05rem;max-width:44em;margin-top:18px}
.article{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:64px;padding-block:56px 100px}
.article .body{display:grid;gap:20px;max-width:68ch}
.article .body p{color:#cfcfd3}
.article .def{font-family:var(--f-serif);font-size:clamp(1.3rem,2vw,1.6rem);line-height:1.35;color:var(--ink)}
.callout{border:1px solid rgba(227,38,47,.4);background:linear-gradient(135deg,rgba(227,38,47,.12),rgba(227,38,47,.02));border-radius:6px;padding:22px 24px}
.callout .k{font:500 .7rem var(--f-mono);letter-spacing:.16em;text-transform:uppercase;color:var(--accent-hi)}
.callout p{margin-top:8px;color:var(--ink)}
.side{display:grid;gap:20px;align-content:start}
.side .box{border:1px solid var(--line);border-radius:6px;padding:22px;background:var(--surface)}
.side h2{font-size:.72rem;font-family:var(--f-mono);font-weight:500;letter-spacing:.16em;text-transform:uppercase;color:var(--faint);margin-bottom:12px}
.side ul{list-style:none;margin:0;padding:0;display:grid;gap:10px}
.side a{color:var(--ink);text-decoration:none;border-bottom:1px solid var(--line)}
.side a:hover{border-color:var(--accent)}
.side p{color:var(--muted);font-size:.92rem;margin-bottom:14px}
@media (max-width:900px){.article{grid-template-columns:1fr;gap:40px}}
.gloss-group{padding-block:44px;border-bottom:1px solid var(--line)}
.gloss-group h2{font-size:1.2rem;margin-bottom:22px}
.gloss-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.gcard{display:grid;gap:8px;padding:22px;border:1px solid var(--line);border-radius:6px;background:var(--surface);text-decoration:none;transition:border-color .2s,transform .3s var(--ease)}
.gcard:hover{border-color:#3a3a40;transform:translateY(-2px)}
.gcard h3{font-family:var(--f-body);font-stretch:100%;font-weight:600;font-size:1.02rem;text-transform:none;letter-spacing:0;line-height:1.3}
.gcard p{color:var(--muted);font-size:.9rem}
.gcard span{font:.72rem var(--f-mono);color:var(--accent-hi);letter-spacing:.08em}
@media (max-width:960px){.gloss-grid{grid-template-columns:1fr 1fr}}@media (max-width:600px){.gloss-grid{grid-template-columns:1fr}}
.faq{max-width:860px;padding-block:40px 100px}
.faq details{border-bottom:1px solid var(--line)}
.faq summary{cursor:pointer;list-style:none;display:flex;justify-content:space-between;gap:20px;padding:24px 0;font:600 1.08rem var(--f-body)}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{content:"+";font:400 1.4rem var(--f-body);color:var(--accent-hi);transition:transform .2s}
.faq details[open] summary::after{transform:rotate(45deg)}
.faq .a{padding:0 0 26px;color:var(--muted);display:grid;gap:12px;max-width:62ch}
.faq .a a{color:var(--ink)}
.toggle{display:inline-flex;align-items:center;gap:10px;color:var(--muted);font-size:.9rem;cursor:pointer}
.toggle input{width:18px;height:18px;accent-color:var(--accent)}
.fitbadge{display:inline-block;margin-left:8px;font:.62rem var(--f-mono);letter-spacing:.08em;text-transform:uppercase;color:var(--faint);border:1px solid var(--line);border-radius:999px;padding:2px 7px;vertical-align:2px}
.prose{max-width:68ch;padding-block:48px 100px;display:grid;gap:16px}
.prose h2{font-size:1.25rem;margin-top:18px}
.prose p,.prose li{color:#cfcfd3}
.cta-band{border-top:1px solid var(--line);padding-block:72px;text-align:center}
.cta-band h2{font-size:clamp(1.5rem,2.6vw,2.2rem)}
.cta-band p{color:var(--muted);margin:14px auto 26px;max-width:40em}
.terms-strip{display:flex;flex-wrap:wrap;gap:10px;margin-top:22px}
.terms-strip a{font:.78rem var(--f-mono);letter-spacing:.04em;text-decoration:none;color:var(--muted);border:1px solid var(--line);border-radius:999px;padding:7px 13px;transition:all .2s}
.terms-strip a:hover{color:var(--ink);border-color:var(--accent)}
td.m a{color:var(--ink);text-decoration:none;border-bottom:1px solid var(--line)}
td.m a:hover{border-color:var(--accent)}
.steps a{color:var(--ink)}
"""

def css():
    base = re.search(r"<style>(.*?)</style>", TPL, re.S).group(1)
    return base + EXTRA_CSS

JS = r"""
(function(){
  var hdr=document.getElementById('hdr');
  function onS(){hdr.classList.toggle('scrolled',scrollY>24)}addEventListener('scroll',onS,{passive:true});onS();
  function store(k,v){try{sessionStorage.setItem(k,v)}catch(e){}}
  function take(k){try{var v=sessionStorage.getItem(k);sessionStorage.removeItem(k);return v}catch(e){return null}}
  // request buttons on any page
  document.addEventListener('click',function(e){
    var b=e.target.closest('[data-part]');if(!b)return;
    var text=b.getAttribute('data-part');
    var form=document.getElementById('qf');
    if(form){fill(text);e.preventDefault();document.getElementById('quote').scrollIntoView({behavior:'smooth'})}
    else{store('tpf-part',text)}
  });
  function fill(t){var d=document.getElementById('q-desc');if(!d)return;document.getElementById('q-type').value='Replacement part';d.value=t+'\nMy model: ';setTimeout(function(){document.getElementById('q-name').focus({preventScroll:true})},600)}
  var pending=take('tpf-part');if(pending)fill(pending);
  // parts filter
  var list=document.getElementById('plist');
  if(list){
    var rows=[].slice.call(list.querySelectorAll('.row')),q=document.getElementById('cat-q'),fit=document.getElementById('fit-only'),more=document.getElementById('cat-more'),empty=document.getElementById('cat-empty'),count=document.getElementById('cat-count');
    var brand='All',limit=40;
    document.querySelectorAll('#cat-chips .chip').forEach(function(c){c.addEventListener('click',function(){brand=c.getAttribute('data-b');limit=40;document.querySelectorAll('#cat-chips .chip').forEach(function(k){k.setAttribute('aria-pressed',k===c)});render()})});
    function render(){var v=q.value.trim().toLowerCase(),n=0,shown=0;
      rows.forEach(function(r){var ok=(brand==='All'||r.getAttribute('data-b')===brand)&&(!fit.checked||r.getAttribute('data-fit')==='1')&&(!v||r.getAttribute('data-k').indexOf(v)>-1);if(ok)n++;var show=ok&&shown<limit;if(show)shown++;r.hidden=!show});
      more.hidden=n<=limit;more.textContent='Show more ('+(n-limit)+')';empty.hidden=n>0;count.textContent=n+(n===1?' part':' parts');}
    q.addEventListener('input',function(){limit=40;render()});fit.addEventListener('change',function(){limit=40;render()});more.addEventListener('click',function(){limit+=60;render()});render();
  }
  // quote form
  var f=document.getElementById('qf');
  if(f&&!window.TPF_HOME){
    var out=document.getElementById('q-out'),txt=document.getElementById('q-text'),err=document.getElementById('q-err'),st=document.getElementById('q-status');
    function v(id){return document.getElementById(id).value.trim()}
    f.addEventListener('submit',function(e){
      e.preventDefault();
      if(!v('q-name')||!v('q-contact')||!v('q-desc')){err.hidden=false;out.hidden=true;return}
      err.hidden=true;
      var lines=['Quote request — True Part Fabrication','','Name: '+v('q-name')];
      if(v('q-co'))lines.push('Company: '+v('q-co'));
      lines.push('Contact: '+v('q-contact'),'Type of work: '+v('q-type'),'Quantity: '+(v('q-qty')||'1'));
      if(v('q-when'))lines.push('Needed by: '+v('q-when'));
      lines.push('','Description:',v('q-desc'),'','(Please attach a photo of the part)');
      txt.textContent=lines.join('\n');out.hidden=false;
      st.textContent='Open it in your email app, or copy it and email it to us. Attach a photo of the part.';
      document.getElementById('q-mail').href='mailto:"""+EMAIL+r"""?subject='+encodeURIComponent('Quote request: '+v('q-type'))+'&body='+encodeURIComponent(txt.textContent);
    });
    document.getElementById('q-copy').addEventListener('click',function(){
      var t=txt.textContent;
      function sel(){var r=document.createRange();r.selectNodeContents(txt);var s=getSelection();s.removeAllRanges();s.addRange(r);st.textContent='Text selected. Copy it with your keyboard or menu.'}
      try{navigator.clipboard.writeText(t).then(function(){st.textContent='Copied. Paste it into an email with a photo attached.'},sel)}catch(e){sel()}
    });
  }
})();
"""

GLOSS = {t["slug"]: t for t in TERMS}

class Ctx:
    def __init__(self, mode, path):
        self.mode, self.path = mode, path      # path like "", "parts/", "glossary/pla/"
        self.depth = path.count("/")
        self.root = "../" * self.depth
    def link(self, p, anchor=""):
        # p: "" (home), "parts/", "glossary/pla/" ...
        if self.mode == "art":
            target = (p + "index.html")
        else:
            target = p if p else "./"
            if self.depth and not p: target = ""
        url = self.root + target if target not in ("./",) else ("./" if not self.depth else self.root)
        if self.mode == "art" and not p:
            url = self.root + "index.html"
        return (url or "./") + (("#" + anchor) if anchor else "")
    def asset(self, a): return self.root + "assets/" + a

def ld(obj): return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False).replace("</", "<\\/") + "</script>"

ORG = {"@context": "https://schema.org", "@type": "LocalBusiness", "@id": BASE + "/#business", "name": "True Part Fabrication LLC",
       "url": BASE + "/", "logo": BASE + "/assets/img/logo-dark.png", "image": BASE + "/assets/img/og-image.jpg",
       "description": "Custom 3D printing, replacement parts, and small-batch manufacturing in Modesto, California.",
       "email": EMAIL, "address": {"@type": "PostalAddress", "addressLocality": "Modesto", "addressRegion": "CA", "addressCountry": "US"},
       "areaServed": ["Modesto", "Ceres", "Turlock", "Manteca", "Tracy", "Stockton", "Stanislaus County", "San Joaquin County"],
       "sameAs": [EBAY],
       "knowsAbout": ["3D printing", "Replacement parts", "Reverse engineering", "Jigs and fixtures", "Small-batch manufacturing"]}

def crumbs_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": BASE + "/" + p} for i, (n, p) in enumerate(items)]}

def head(c, title, desc, lds=(), og_type="website"):
    canon = BASE + "/" + c.path
    robots = "index,follow" if INDEX else "noindex,follow"
    h = f"""<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{SITE}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{BASE}/assets/img/og-image.jpg">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:image:alt" content="True Part Fabrication logo over 3D-printed parts">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#070708">
<link rel="icon" type="image/png" sizes="32x32" href="{c.asset('img/favicon-32.png')}">
<link rel="icon" type="image/png" sizes="48x48" href="{c.asset('img/favicon-48.png')}">
<link rel="apple-touch-icon" href="{c.asset('img/icon-180.png')}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,300..900&family=Instrument+Serif:ital@0;1&family=Instrument+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="{c.asset('site.css')}">
"""
    return h + "\n".join(ld(x) for x in lds)

def header(c):
    L = c.link
    return f"""<a href="#main" class="skip" style="position:absolute;left:-9999px;top:0;z-index:50;background:var(--accent);color:#fff;padding:10px 16px" onfocus="this.style.left='12px'" onblur="this.style.left='-9999px'">Skip to content</a>
<header id="hdr">
  <div class="wrap bar">
    <a class="brand" href="{L('')}" aria-label="True Part Fabrication home"><img src="{c.asset('img/logo-dark.png')}" alt="True Part Fabrication" width="800" height="493"></a>
    <nav class="main" aria-label="Main">
      <a class="l" href="{L('', 'services')}">Services</a>
      <a class="l" href="{L('', 'business')}">For business</a>
      <a class="l" href="{L('', 'parts')}">Parts</a>
      <a class="l" href="{L('', 'process')}">Process</a>
      <a class="l" href="{L('glossary/')}">Glossary</a>
      <a class="l" href="{L('faq/')}">FAQ</a>
      <a class="l" href="{L('', 'about')}">About</a>
      <a class="btn" href="{L('', 'quote')}">Request a quote</a>
    </nav>
  </div>
</header>"""

def footer(c):
    L = c.link
    return f"""<footer>
  <div class="wrap">
    <div class="foot">
      <div><img src="{c.asset('img/logo-dark.png')}" alt="True Part Fabrication" width="800" height="493" loading="lazy"><p style="color:var(--muted);margin-top:18px;max-width:28em;font-size:.95rem">Replacement parts, custom fabrication, and small-batch manufacturing in Modesto, California.</p></div>
      <div><h4>Explore</h4><ul><li><a href="{L('', 'services')}">Services</a></li><li><a href="{L('', 'business')}">For business</a></li><li><a href="{L('parts/')}">Compatible parts</a></li><li><a href="{L('', 'process')}">Process</a></li><li><a href="{L('glossary/')}">Glossary</a></li><li><a href="{L('faq/')}">FAQ</a></li></ul></div>
      <div><h4>Contact</h4><ul><li><a href="{L('', 'quote')}">Request a quote</a></li><li><span style="color:var(--muted)">{EMAIL}</span></li><li><a href="{EBAY}" target="_blank" rel="noopener">eBay store</a></li><li><a href="{L('privacy/')}">Privacy</a></li></ul></div>
    </div>
    <div class="copy-line"><span>© 2026 True Part Fabrication LLC</span><span>Modesto · Ceres · Turlock · Manteca · Tracy · Stockton</span></div>
  </div>
</footer>
<script src="{c.asset('site.js')}" defer></script>"""

def doc(c, headhtml, body, art_index=False):
    if art_index:
        return headhtml + "\n<meta name=\"claude:viewport-fit-sides\" content=\"cover\">\n" + header(c) + "\n" + body + "\n" + footer(c) + "\n"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
{headhtml}
</head>
<body>
{header(c)}
{body}
{footer(c)}
</body>
</html>
"""

def crumbs(c, items):
    parts = []
    for n, p in items[:-1]:
        parts.append(f'<a href="{c.link(p)}">{esc(n)}</a><span aria-hidden="true">/</span>')
    parts.append(f'<span aria-current="page">{esc(items[-1][0])}</span>')
    return '<nav class="crumbs" aria-label="Breadcrumb">' + "".join(parts) + "</nav>"

def rp(it): return ("Replaces " + it["b"] + " " + it["oem"]) if it["oem"] else ("For " + it["b"] + " " + it["for"])
def part_text(it): return "Compatible part: " + it["n"] + "\n" + rp(it)

def feat_cards(c):
    out = []
    for m in CAT["feat"]:
        it = next((x for x in CAT["items"] if x["oem"] == m), None)
        if not it: continue
        out.append(f"""<article class="pc"><div class="ph"><img src="{c.asset('img/sample-' + it['i'] + '.jpg')}" alt="Sample image of a 3D-printed {it['i']}" width="640" height="480" loading="lazy"><span>Sample image</span></div>
<div class="bd"><div class="br">Fits {esc(it['b'])}</div><h4>{esc(it['n'])}</h4><div class="rp">{esc(rp(it))}</div><div class="ft">{esc('Fits ' + it['f']) if it['f'] else 'Ask us to confirm your model'}</div>
<a class="go" href="{c.link('', 'quote')}" data-part="{esc(part_text(it))}">Request this part →</a></div></article>""")
    return "\n".join(out)

# ---------------- HOME ----------------
def home(c, art=False):
    main = re.search(r'(<main id="top">.*?</main>)', TPL, re.S).group(1)
    main = main.replace('<main id="top">', '<main id="main">')
    # img data URIs -> files
    main = re.sub(r'src="data:image/png;base64,[^"]+"', f'src="{c.asset("img/logo-dark.png")}"', main)
    for k in ["HERO", "ADAPTER", "BRACKET", "ENCLOSURE", "BATCH"]:
        main = main.replace("{{IMG_" + k + "}}", c.asset("img/" + ("hero" if k == "HERO" else "svc-" + k.lower()) + ".jpg"))
    check = '<svg viewBox="0 0 22 22" fill="none" stroke="var(--accent-hi)" stroke-width="1.8" aria-hidden="true"><circle cx="11" cy="11" r="10"/><path d="M6.5 11.5l3 3 6-6.5"/></svg>'
    main = main.replace("{{CHECK}}", check)
    main = main.replace('<img src="' + c.asset("img/svc-"), '<img loading="lazy" src="' + c.asset("img/svc-"))
    # additive: link to the full parts page beside the eBay button
    main = main.replace('<div class="parts-top"><h3>Popular parts</h3><a class="btn ghost" href="https://www.ebay.com/usr/sottero"',
        '<div class="parts-top"><h3>Popular parts</h3><div style="display:flex;gap:10px;flex-wrap:wrap"><a class="btn ghost" href="' + c.link('parts/') + '">Parts catalog page <span class="ar">→</span></a><a class="btn ghost" href="https://www.ebay.com/usr/sottero"',1)
    main = main.replace('Shop ready-made parts on eBay <span class="ar">↗</span></a></div>','Shop ready-made parts on eBay <span class="ar">↗</span></a></div></div>',1)
    # glossary links in materials table + process
    for name, slug in [("PLA / PLA-CF", "pla"), ("PETG", "petg"), ("ASA / ABS", "asa"), ("PA-CF (nylon carbon)", "pa-cf")]:
        main = re.sub(r'(<td class="m"><i style="background:#[0-9A-F]{6}"></i>)' + re.escape(name) + "</td>", r'\1<a href="' + c.link("glossary/" + slug + "/") + '">' + name + "</a></td>", main)
    main = main.replace("<h3>We model</h3><p>Drawn in CAD,", f'<h3>We model</h3><p>Drawn in <a href="{c.link("glossary/cad/")}">CAD</a>,')
    main = main.replace('<p class="note">Heat limits are typical published ranges and vary by brand and print settings.</p>',
        f'<p class="note">Heat limits are typical published ranges and vary by brand and print settings. See <a href="{c.link("glossary/heat-deflection-temperature/")}" style="color:var(--muted)">heat deflection temperature</a>.</p>')
    # learn strip before quote
    strip = "".join(f'<a href="{c.link("glossary/" + s + "/")}">{esc(GLOSS[s]["term"].split(" (")[0])}</a>' for s in ["petg", "asa", "tolerance", "infill", "reverse-engineering", "dust-port-hose-sizes", "small-batch-manufacturing", "fit-types"])
    main = main.replace('<section id="quote"', f"""<section id="learn" style="border-top:1px solid var(--line);padding-block:80px">
  <div class="wrap">
    <div class="head" style="margin-bottom:0">
      <div class="label">Learn the terms</div>
      <h2>Know what to <em class="s">ask for.</em></h2>
      <p>Plain-English explanations of the materials, fits, and printing terms that come up in a quote. Or read the <a href="{c.link('faq/')}" style="color:var(--ink)">frequently asked questions</a>.</p>
    </div>
    <div class="terms-strip">{strip}<a href="{c.link('glossary/')}" style="color:var(--ink);border-color:var(--accent)">See all {len(TERMS)} terms →</a></div>
  </div>
</section>

<section id="quote\"""", 1)
    title = "Custom 3D Printing & Replacement Parts in Modesto, CA | True Part Fabrication"
    desc = "True Part Fabrication designs and 3D prints replacement parts, custom brackets, jigs, fixtures, and small-batch runs for businesses in Modesto, Turlock, Stockton, and the Central Valley. Free reprint if it doesn't fit."
    org = dict(ORG)
    web = {"@context": "https://schema.org", "@type": "WebSite", "name": SITE, "url": BASE + "/"}
    script = TPL[TPL.index('<script id="cat-data"'):]
    sample = json.dumps({k: c.asset('img/sample-' + k + '.jpg') for k in ['adapter','nozzle','brush','separator','clip','roller']})
    script = script.replace('{{CAT}}', json.dumps(CAT, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')).replace('{{IMG_SAMPLE}}', sample)
    main = main + '\n<script>window.TPF_HOME=1</script>\n' + script
    return doc(c, head(c, title, desc, [org, web]), main, art_index=art)

# ---------------- PARTS ----------------
def parts(c):
    items = CAT["items"]; brands = []
    for x in items:
        if x["b"] not in brands: brands.append(x["b"])
    chips = '<button class="chip" type="button" data-b="All" aria-pressed="true">All<i>' + str(len(items)) + "</i></button>" + "".join(
        f'<button class="chip" type="button" data-b="{esc(b)}" aria-pressed="false">{esc(b)}<i>{sum(1 for x in items if x["b"] == b)}</i></button>' for b in brands)
    rows = []
    for it in items:
        k = (it["b"] + " " + it["oem"] + " " + it.get("for", "") + " " + it["n"] + " " + it["f"]).lower()
        badge = "" if it["f"] else '<span class="fitbadge">Fit to confirm</span>'
        rows.append(f"""<div class="row" data-b="{esc(it['b'])}" data-fit="{1 if it['f'] else 0}" data-k="{esc(k)}"><div class="b">{esc(it['b'])}</div><h3 class="n" style="font:600 1rem var(--f-body);text-transform:none;letter-spacing:0">{esc(it['n'])}{badge}</h3><div class="o">{esc(rp(it))}</div><div class="f">{esc(it['f'] or 'Ask us to confirm your model')}</div><a class="btn ghost" style="height:34px;padding:0 14px;font-size:.8rem" href="{c.link('', 'quote')}" data-part="{esc(part_text(it))}">Request</a></div>""")
    body = f"""<main id="main">
<div class="page-hero"><div class="wrap">
  {crumbs(c, [('Home', ''), ('Compatible parts', 'parts/')])}
  <h1>Compatible replacement parts</h1>
  <p class="lead">{len(items)} made-to-order aftermarket parts that fit {', '.join(brands[:-1])}, and {brands[-1]} tools, vacuums, and appliances. Search by part number or model, then request a quote. Every part is covered by our <a href="{c.link('faq/')}" style="color:var(--ink)">fit guarantee</a>.</p>
</div></div>
<section style="padding-block:44px 100px"><div class="wrap">
  <div class="tools">
    <div class="search"><svg viewBox="0 0 16 16" fill="none" stroke="var(--muted)" stroke-width="1.6" aria-hidden="true"><circle cx="7" cy="7" r="5"/><path d="M11 11l3.5 3.5"/></svg><label for="cat-q" style="position:absolute;left:-9999px">Search parts</label><input id="cat-q" type="search" placeholder="Search part number, model, or name"></div>
    <label class="toggle" for="fit-only"><input type="checkbox" id="fit-only" checked> Confirmed fit only</label>
    <span id="cat-count" style="color:var(--faint);font-size:.88rem;margin-left:auto"></span>
  </div>
  <div class="chips" id="cat-chips" role="group" aria-label="Filter by brand" style="margin-bottom:22px">{chips}</div>
  <div class="list" id="plist">
{chr(10).join(rows)}
  </div>
  <p class="empty" id="cat-empty" hidden>No parts match. Turn off "Confirmed fit only," or describe your part in the <a href="{c.link('', 'quote')}" style="color:var(--ink)">quote form</a>.</p>
  <div class="more"><button class="btn ghost" type="button" id="cat-more" hidden>Show more</button></div>
  <p class="legal">These are compatible aftermarket parts made by True Part Fabrication, not original manufacturer parts. Brand names and part numbers belong to their owners and are used only to describe fit. True Part Fabrication is not affiliated with or endorsed by any brand listed. Learn more about <a href="{c.link('glossary/aftermarket-part/')}" style="color:var(--muted)">aftermarket parts</a>.</p>
</div></section>
</main>"""
    title = "Compatible Replacement Parts for DeWalt, Milwaukee, Ryobi & More | True Part Fabrication"
    desc = f"Browse {len(items)} made-to-order aftermarket parts: dust adapters, nozzles, brushes, clips, and fittings that fit DeWalt, Milwaukee, Ryobi, RIDGID, WEN, Shark, and more. 3D printed in Modesto, CA."
    lds = [crumbs_ld([("Home", ""), ("Compatible parts", "parts/")]),
           {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Compatible replacement parts", "url": BASE + "/parts/", "isPartOf": {"@id": BASE + "/#business"}}]
    return doc(c, head(c, title, desc, lds), body)

# ---------------- FAQ ----------------
def FAQS(c):
    G = lambda s, t: f'<a href="{c.link("glossary/" + s + "/")}">{t}</a>'
    return [
     ("What should I send to get a quote?", f"<p>The original part is best, even if it's broken. If you can't send it, send clear photos from a few angles with a ruler or calipers in the shot, plus the make and model of the equipment and any part number you can find.</p><p>Have a 3D file? Attach it. We accept STL, STEP, and most {G('cad','CAD')} formats.</p>"),
     ("How much does a part cost?", "<p>It depends on the part's size, the material, and how many you need. Most business jobs run from about $75 to $800 or more. Every job gets a written quote with the material, price, and turnaround before we print anything.</p>"),
     ("How long does it take?", f"<p>Turnaround depends on whether the part needs to be measured and modeled from scratch or we already have the model. Your written quote states the turnaround before work starts. Repeat orders are faster because your model is already on file.</p>"),
     ("What if the part doesn't fit?", "<p>We reprint it free. Send us your measurements or the part, and we'll adjust the model and make it right. That's our fit guarantee.</p>"),
     ("Can you make a part from a photo?", f"<p>Sometimes. Simple parts can be modeled from good photos with a measurement reference. Parts with precise fits, like hose adapters and clips, usually need the original or careful caliper measurements. See {G('reverse-engineering','reverse engineering')}.</p>"),
     ("Are printed parts as strong as the original?", f"<p>Often, yes, and sometimes stronger, if the material and {G('print-orientation','print orientation')} are right. We choose materials like {G('petg','PETG')}, {G('asa','ASA')}, or {G('pa-cf','carbon-fiber nylon')} for the job and can thicken the spot where the original failed. We'll tell you honestly if a printed part isn't a good fit for your use.</p>"),
     ("What parts won't you make?", f"<p>We don't make parts where a failure could hurt someone: safety-critical, load-bearing, pressurized, electrical, braking or steering, child-safety, medical, pool-safety, or code-compliance parts. We also don't make {G('food-contact','food-contact parts')}.</p>"),
     ("Do you make repeat orders and small batches?", f"<p>Yes. We keep your part's model on file, so reorders match the first run. Five or five hundred, with no molds and no large minimums. See {G('small-batch-manufacturing','small-batch manufacturing')}.</p>"),
     ("Where are you located, and do you ship?", "<p>We're in Modesto, California, and serve Modesto, Ceres, Turlock, Manteca, Tracy, and Stockton, including on-site measuring for parts that can't come off the machine. We also ship statewide.</p>"),
     ("Are your parts genuine brand parts?", f"<p>No. They're compatible {G('aftermarket-part','aftermarket parts')} that we design and make. Brand names and part numbers are used only to show what a part fits.</p>"),
     ("Can I buy parts without a quote?", f'<p>Some ready-made parts are available in our <a href="{EBAY}" target="_blank" rel="noopener">eBay store</a>. Everything else is made to order.</p>'),
    ]
def faq(c):
    items = FAQS(c)
    det = "\n".join(f"<details{' open' if i == 0 else ''}><summary>{esc(q)}</summary><div class=\"a\">{a}</div></details>" for i, (q, a) in enumerate(items))
    body = f"""<main id="main">
<div class="page-hero"><div class="wrap">
  {crumbs(c, [('Home', ''), ('FAQ', 'faq/')])}
  <h1>Frequently asked questions</h1>
  <p class="lead">Quotes, pricing, turnaround, materials, and what we can and can't make.</p>
</div></div>
<div class="wrap faq">{det}</div>
<div class="cta-band"><div class="wrap"><h2>Still have a question?</h2><p>Describe your part and we'll reply with questions or a written quote.</p><a class="btn" href="{c.link('', 'quote')}">Request a quote <span class="ar">→</span></a></div></div>
</main>"""
    strip = lambda s: re.sub("<[^>]+>", "", s).strip()
    faqld = {"@context": "https://schema.org", "@type": "FAQPage",
             "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip(a)}} for q, a in items]}
    return doc(c, head(c, "3D Printing & Replacement Parts FAQ | True Part Fabrication",
                       "Answers about quotes, pricing, turnaround, materials, fit guarantee, and what True Part Fabrication can make. Custom 3D printing in Modesto, CA.",
                       [faqld, crumbs_ld([("Home", ""), ("FAQ", "faq/")])]), body)

# ---------------- GLOSSARY ----------------
CATS = ["Process", "Materials", "Fit", "Design", "Parts", "Production"]
def gloss_index(c):
    groups = []
    for cat in CATS:
        ts = sorted([t for t in TERMS if t["cat"] == cat], key=lambda t: t["term"].lower())
        cards = "".join(f'<a class="gcard" href="{c.link("glossary/" + t["slug"] + "/")}"><h3>{esc(t["term"])}</h3><p>{esc(t["short"])}</p><span>Read more →</span></a>' for t in ts)
        groups.append(f'<div class="gloss-group" id="{cat.lower()}"><h2>{cat}</h2><div class="gloss-grid">{cards}</div></div>')
    jump = " ".join(f'<a href="#{cat.lower()}">{cat}</a>' for cat in CATS)
    body = f"""<main id="main">
<div class="page-hero"><div class="wrap">
  {crumbs(c, [('Home', ''), ('Glossary', 'glossary/')])}
  <h1>3D printing and replacement parts glossary</h1>
  <p class="lead">Plain-English definitions of the materials, fits, and manufacturing terms that come up when you order a custom or replacement part, and what each one means for your part.</p>
  <div class="terms-strip">{jump}</div>
</div></div>
<div class="wrap" style="padding-bottom:60px">{''.join(groups)}</div>
<div class="cta-band"><div class="wrap"><h2>Have a part in mind?</h2><p>You don't need the vocabulary to get a quote. Describe what broke and we'll handle the rest.</p><a class="btn" href="{c.link('', 'quote')}">Request a quote <span class="ar">→</span></a></div></div>
</main>"""
    setld = {"@context": "https://schema.org", "@type": "DefinedTermSet", "name": "True Part Fabrication glossary", "url": BASE + "/glossary/",
             "hasDefinedTerm": [{"@type": "DefinedTerm", "name": t["term"], "description": t["short"], "url": BASE + "/glossary/" + t["slug"] + "/"} for t in TERMS]}
    return doc(c, head(c, "3D Printing Glossary: Materials, Fits & Terms | True Part Fabrication",
                       f"{len(TERMS)} plain-English definitions of 3D printing and replacement part terms: PETG, ASA, tolerance, infill, reverse engineering, hose sizes, and more.",
                       [setld, crumbs_ld([("Home", ""), ("Glossary", "glossary/")])]), body)

def gloss_page(c, t):
    paras = "\n".join(f"<p>{esc(p)}</p>" for p in t["body"])
    rel = "".join(f'<li><a href="{c.link("glossary/" + s + "/")}">{esc(GLOSS[s]["term"])}</a></li>' for s in t["related"] if s in GLOSS)
    same = [x for x in TERMS if x["cat"] == t["cat"] and x["slug"] != t["slug"] and x["slug"] not in t["related"]][:4]
    more = "".join(f'<li><a href="{c.link("glossary/" + x["slug"] + "/")}">{esc(x["term"])}</a></li>' for x in same)
    body = f"""<main id="main">
<div class="page-hero"><div class="wrap">
  {crumbs(c, [('Home', ''), ('Glossary', 'glossary/'), (t['term'], 'glossary/' + t['slug'] + '/')])}
  <h1>{esc(t['term'])}</h1>
  <p class="lead" style="font:500 .72rem var(--f-mono);letter-spacing:.14em;text-transform:uppercase;color:var(--accent-hi)">{t['cat']}</p>
</div></div>
<div class="wrap article">
  <article class="body">
    <p class="def">{esc(t['short'])}</p>
    {paras}
    <div class="callout"><div class="k">What it means for your part</div><p>{esc(t['quote'])}</p></div>
    <p><a class="btn" href="{c.link('', 'quote')}">Request a quote <span class="ar">→</span></a></p>
  </article>
  <aside class="side">
    <div class="box"><h2>Related terms</h2><ul>{rel}</ul></div>
    {f'<div class="box"><h2>More in {t["cat"]}</h2><ul>{more}</ul></div>' if more else ''}
    <div class="box"><h2>Need a part?</h2><p>We design and 3D print replacement parts in Modesto, CA. Free reprint if it doesn't fit.</p><a class="btn ghost" href="{c.link('parts/')}" style="height:40px;font-size:.85rem">Browse compatible parts</a></div>
  </aside>
</div>
</main>"""
    path = "glossary/" + t["slug"] + "/"
    termld = {"@context": "https://schema.org", "@type": "DefinedTerm", "name": t["term"], "description": t["short"], "url": BASE + "/" + path,
              "inDefinedTermSet": BASE + "/glossary/"}
    name = t["term"].split(" (")[0]
    return doc(c, head(c, f"What is {name}? {t['cat']} glossary | True Part Fabrication", t["short"],
                       [termld, crumbs_ld([("Home", ""), ("Glossary", "glossary/"), (t["term"], path)])], og_type="article"), body)

# ---------------- PRIVACY ----------------
def privacy(c):
    body = f"""<main id="main">
<div class="page-hero"><div class="wrap">
  {crumbs(c, [('Home', ''), ('Privacy', 'privacy/')])}
  <h1>Privacy</h1>
  <p class="lead">What happens to the information you share with us.</p>
</div></div>
<div class="wrap"><div class="prose">
  <h2>What we collect</h2>
  <p>This website doesn't use accounts, tracking cookies, or advertising. The quote form doesn't send anything by itself: it prepares a message that you choose to send from your own email.</p>
  <p>When you email us, we receive what you include, such as your name, company, contact details, part description, photos, and files.</p>
  <h2>How we use it</h2>
  <p>We use your information only to answer your request, prepare quotes, make and deliver your parts, and keep records for repeat orders and our accounts. We don't sell or rent your information.</p>
  <h2>Files and part designs</h2>
  <p>Part photos, measurements, and models you send are used for your job and kept on file so we can reprint your part. Tell us if you'd like them deleted.</p>
  <h2>Third-party services</h2>
  <p>This site loads fonts from Google Fonts, which may log your IP address. Links to our eBay store take you to eBay, which has its own privacy policy.</p>
  <h2>Contact</h2>
  <p>Questions or deletion requests: {EMAIL}.</p>
  <p style="color:var(--faint);font-size:.88rem">Last updated October 2026.</p>
</div></div>
</main>"""
    return doc(c, head(c, "Privacy | True Part Fabrication", "How True Part Fabrication handles the information you share with us.", [crumbs_ld([("Home", ""), ("Privacy", "privacy/")])]), body)

# ---------------- BUILD ----------------
def write(root, path, text):
    p = os.path.join(root, path); os.makedirs(os.path.dirname(p), exist_ok=True); open(p, "w").write(text)

def build(mode, root):
    if os.path.exists(root) and root != "/home/claude/site":
        shutil.rmtree(root)
    os.makedirs(root + "/assets/img", exist_ok=True)
    if root != "/home/claude/site":
        for f in os.listdir("/home/claude/site/assets/img"):
            shutil.copy("/home/claude/site/assets/img/" + f, root + "/assets/img/" + f)
    write(root, "assets/site.css", css())
    write(root, "assets/site.js", JS)
    pages = {"": lambda c: home(c, art=(mode == "art")), "parts/": parts, "faq/": faq, "glossary/": gloss_index, "privacy/": privacy}
    for p, fn in pages.items():
        write(root, p + "index.html", fn(Ctx(mode, p)))
    for t in TERMS:
        p = "glossary/" + t["slug"] + "/"
        write(root, p + "index.html", gloss_page(Ctx(mode, p), t))
    urls = [""] + [p for p in pages if p] + ["glossary/" + t["slug"] + "/" for t in TERMS]
    if mode == "render":
        sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
            f"  <url><loc>{BASE}/{u}</loc><lastmod>2026-10-30</lastmod></url>\n" for u in urls) + "</urlset>\n"
        write(root, "sitemap.xml", sm)
        write(root, "robots.txt", (f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n") if INDEX else "# Temporary address: block all crawling until the real domain is live.\nUser-agent: *\nDisallow: /\n")
    return urls

if __name__ == "__main__":
    u = build("render", "/home/claude/site")
    build("art", "/home/claude/site_art")
    print(len(u), "pages")
