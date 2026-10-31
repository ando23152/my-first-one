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
EMAIL = ""
EBAY = "https://www.ebay.com/usr/truepartfabrication"
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
.article .body p{color:var(--ink)}
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
.gcard:hover{border-color:#5578A8;transform:translateY(-2px)}
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
.prose p,.prose li{color:var(--ink)}
.cta-band{border-top:1px solid var(--line);padding-block:72px;text-align:center}
.cta-band h2{font-size:clamp(1.5rem,2.6vw,2.2rem)}
.cta-band p{color:var(--muted);margin:14px auto 26px;max-width:40em}
.terms-strip{display:flex;flex-wrap:wrap;gap:10px;margin-top:22px}
.terms-strip a{font:.78rem var(--f-mono);letter-spacing:.04em;text-decoration:none;color:var(--muted);border:1px solid var(--line);border-radius:999px;padding:7px 13px;transition:all .2s}
.terms-strip a:hover{color:var(--ink);border-color:var(--accent)}
td.m a{color:var(--ink);text-decoration:none;border-bottom:1px solid var(--line)}
td.m a:hover{border-color:var(--accent)}
.steps a{color:var(--ink)}
.opening{background:var(--accent);color:#fff;font-size:.85rem;text-align:center;padding-block:9px;position:relative;z-index:21}
.opening a{color:#fff;font-weight:600;text-underline-offset:3px}
.agree{display:flex;gap:10px;align-items:flex-start;font:400 .95rem var(--f-body)!important;letter-spacing:0!important;text-transform:none!important;color:var(--ink)!important;cursor:pointer}
.agree input{width:18px;height:18px;margin-top:2px;flex:none;accent-color:var(--accent)}
.agree a{color:var(--ink)}
.terms h2{scroll-margin-top:110px}
.brands .row a{font-family:var(--f-display);font-stretch:110%;font-weight:600;font-size:1.05rem;letter-spacing:.06em;text-transform:uppercase;color:var(--faint);text-decoration:none;transition:color .2s}
.brands .row a:hover{color:var(--ink)}
.svc li a{color:inherit;text-decoration:none}
.svc li:has(a):hover{border-color:var(--accent);color:var(--ink)}
.facts a.fact{display:block;padding:28px 24px;border-right:1px solid var(--line);text-decoration:none;color:inherit;transition:background .2s}
.facts a.fact:last-child{border-right:0}
.facts a.fact:hover{background:var(--surface)}
.facts a.fact b{display:block;font-family:var(--f-display);font-stretch:106%;font-weight:500;font-size:1.1rem;line-height:1;letter-spacing:-.01em}
.facts a.fact span{display:block;margin-top:8px;color:var(--muted);font-size:.88rem}
@media (max-width:860px){.facts a.fact{border-right:0;border-bottom:1px solid var(--line)}.facts a.fact:last-child{border-bottom:0}}
.statement p.sub a,.svc + .svc a,.scope li a,.quote .info p a,.steps p a{color:var(--ink)}

@media (min-width:861px){.shop{grid-template-columns:repeat(2,1fr)}}
.secpage > section{padding-top:40px}
.hero-shot img{-webkit-mask-image:none!important;mask-image:none!important;border-radius:14px}
.hero-shot{padding-inline:clamp(16px,3vw,40px);max-width:1630px;margin-inline:auto!important;margin-top:20px!important}
"""

LIGHT_CSS = r"""
/* ---- light theme (visitor toggle) ---- */
:root[data-tpf-theme="light"]{--bg:#ffffff;--surface:#f6f6f4;--surface-2:#efefec;--ink:#121214;--muted:#2b2b30;--faint:#626269;--line:#e2e2de;--accent:#d71f28;--accent-hi:#c3141c;color-scheme:light}
:root[data-tpf-theme="light"] header.scrolled{background:rgba(255,255,255,.9)}
:root[data-tpf-theme="light"] .hero::before{background:radial-gradient(closest-side,rgba(215,31,40,.06),rgba(215,31,40,0))}
:root[data-tpf-theme="light"] .hero-logo,:root[data-tpf-theme="light"] .brand img{filter:none}
:root[data-tpf-theme="light"] .hero-shot img{-webkit-mask-image:linear-gradient(to bottom,transparent 0,#000 12%,#000 80%,transparent 100%);mask-image:linear-gradient(to bottom,transparent 0,#000 12%,#000 80%,transparent 100%)}
:root[data-tpf-theme="light"] .facts{background:linear-gradient(to bottom,rgba(255,255,255,0),var(--bg) 40%)}
:root[data-tpf-theme="light"] .btn.ghost{border-color:#cdcdc8}
:root[data-tpf-theme="light"] .btn.ghost:hover{border-color:var(--ink)}
:root[data-tpf-theme="light"] .btn:hover{box-shadow:0 10px 26px -12px rgba(215,31,40,.6)}
:root[data-tpf-theme="light"] .pc:hover,:root[data-tpf-theme="light"] .res:hover,:root[data-tpf-theme="light"] .gcard:hover{border-color:#cdcdc8}
:root[data-tpf-theme="light"] .chip:hover{border-color:#bdbdb8}
:root[data-tpf-theme="light"] .row button{border-color:#cdcdc8}
:root[data-tpf-theme="light"] .row button:hover{color:#fff}
:root[data-tpf-theme="light"] .steps .n{border-color:#cdcdc8}
:root[data-tpf-theme="light"] .statement{background:radial-gradient(60% 80% at 50% 50%,rgba(215,31,40,.06),transparent)}
:root[data-tpf-theme="light"] .price,:root[data-tpf-theme="light"] .callout,:root[data-tpf-theme="light"] .result{background:linear-gradient(135deg,rgba(215,31,40,.08),rgba(215,31,40,.01));border-color:rgba(215,31,40,.35)}
:root[data-tpf-theme="light"] .inds div{background:var(--bg)}
:root[data-tpf-theme="light"] .inds div:hover{background:var(--surface)}
:root[data-tpf-theme="light"] td.m i{box-shadow:inset 0 0 0 1px rgba(0,0,0,.18)}
:root[data-tpf-theme="light"] .pc .ph span{background:rgba(255,255,255,.85);color:var(--ink)}
:root[data-tpf-theme="light"] .cf.Confirmed{color:#1c7f45;border-color:rgba(28,127,69,.4)}
:root[data-tpf-theme="light"] .cf.Likely{color:#9a6200;border-color:rgba(154,98,0,.4)}
:root[data-tpf-theme="light"] .dots i{color:#d6d6d2}
:root[data-tpf-theme="light"] .mq label.o,:root[data-tpf-theme="light"] .sz{border-color:#cdcdc8}
:root[data-tpf-theme="light"] .explain b.ok{color:#1c7f45}
:root[data-tpf-theme="light"] .explain b.lk{color:#9a6200}
.theme-btn{display:inline-grid;place-items:center;width:42px;height:42px;border-radius:50%;border:1px solid var(--line);background:transparent;color:var(--ink);cursor:pointer;transition:border-color .2s}
.theme-btn:hover{border-color:var(--accent)}
.theme-btn svg{width:18px;height:18px}
.theme-btn .sun,.theme-btn .dot{display:none}
:root[data-tpf-theme="black"] .theme-btn .dot{display:block}
:root[data-tpf-theme="black"] .theme-btn .moon{display:none}
/* ---- black theme (the original look) ---- */
:root[data-tpf-theme="black"]{--bg:#070708;--surface:#0f0f11;--surface-2:#16161a;--line:#232328;--accent-hi:#ff3b43}
:root[data-tpf-theme="black"] header.scrolled{background:rgba(7,7,8,.82)}
:root[data-tpf-theme="black"] .facts{background:linear-gradient(to bottom,rgba(7,7,8,0),var(--bg) 40%)}
:root[data-tpf-theme="black"] .btn.ghost,:root[data-tpf-theme="black"] .row button,:root[data-tpf-theme="black"] .steps .n,:root[data-tpf-theme="black"] .sz,:root[data-tpf-theme="black"] .mq label.o{border-color:#3a3a40}
:root[data-tpf-theme="black"] .pc:hover,:root[data-tpf-theme="black"] .res:hover,:root[data-tpf-theme="black"] .gcard:hover,:root[data-tpf-theme="black"] .chip:hover{border-color:#3a3a40}
:root[data-tpf-theme="black"] .dots i{color:#3a3a40}
:root[data-tpf-theme="black"] .hero-shot{padding-inline:0!important;max-width:none!important;margin-top:0!important}
:root[data-tpf-theme="black"] .hero-shot img{border-radius:0!important;-webkit-mask-image:linear-gradient(to bottom,transparent 0,#000 18%,#000 72%,transparent 100%)!important;mask-image:linear-gradient(to bottom,transparent 0,#000 18%,#000 72%,transparent 100%)!important}
.theme-row{display:flex;gap:10px;flex-wrap:wrap;margin-top:22px}
.theme-row span{width:100%;font:500 .7rem var(--f-mono);letter-spacing:.14em;text-transform:uppercase;color:var(--faint)}
.theme-row button{font:500 .95rem var(--f-body);color:var(--ink);background:transparent;border:1px solid var(--line);border-radius:999px;padding:9px 16px;cursor:pointer}
.theme-row button[aria-pressed="true"]{border-color:var(--accent);background:var(--accent);color:#fff}
:root[data-tpf-theme="light"] .theme-btn .sun{display:block}
:root[data-tpf-theme="light"] .theme-btn .moon{display:none}
"""
def css():
    import tools, parts_pages
    base = re.search(r"<style>(.*?)</style>", TPL, re.S).group(1)
    import improve
    return improve.minify_css(base + EXTRA_CSS + tools.EXTRA_CSS + parts_pages.PART_CSS + __import__('es').ES_CSS + __import__('extras').EX_CSS + improve.IMP_CSS + LIGHT_CSS)

JS = r"""
(function(){
  var root=document.documentElement,tb=document.getElementById('theme-btn'),meta=document.querySelector('meta[name="theme-color"]');
  var NAMES={dark:'Blue',black:'Black',light:'Light'},NEXT={dark:'black',black:'light',light:'dark'},COL={dark:'#0A3161',black:'#070708',light:'#ffffff'};
  function cur(){var a=root.getAttribute('data-tpf-theme');return a==='light'||a==='black'?a:'dark'}
  function applyTheme(t){
    if(t==='light'||t==='black')root.setAttribute('data-tpf-theme',t);else{root.removeAttribute('data-tpf-theme');t='dark'}
    document.querySelectorAll('img[data-light]').forEach(function(i){if(!i.getAttribute('data-dark'))i.setAttribute('data-dark',i.getAttribute('src'));var want=i.getAttribute('data-'+t)||i.getAttribute('data-dark');if(i.getAttribute('src')!==want)i.setAttribute('src',want)});
    if(tb){tb.setAttribute('aria-label','Theme: '+NAMES[t]+'. Switch to '+NAMES[NEXT[t]]);tb.setAttribute('title','Theme: '+NAMES[t])}
    document.querySelectorAll('[data-set-theme]').forEach(function(b){b.setAttribute('aria-pressed',b.getAttribute('data-set-theme')===t)});
    if(meta)meta.setAttribute('content',COL[t]);
  }
  function setTheme(t){applyTheme(t);try{localStorage.setItem('tpf-theme',t)}catch(e){}}
  applyTheme(cur());
  if(tb)tb.addEventListener('click',function(){setTheme(NEXT[cur()])});
  document.addEventListener('click',function(e){var b=e.target.closest('[data-set-theme]');if(b)setTheme(b.getAttribute('data-set-theme'))});
  var hdr=document.getElementById('hdr');
  function onS(){hdr.classList.toggle('scrolled',scrollY>24)}addEventListener('scroll',onS,{passive:true});onS();
  function store(k,v){try{sessionStorage.setItem(k,v)}catch(e){}}
  function take(k){try{var v=sessionStorage.getItem(k);sessionStorage.removeItem(k);return v}catch(e){return null}}
  // request buttons on any page
  document.addEventListener('click',function(e){
    var b=e.target.closest('[data-part]');if(!b)return;
    var text=b.getAttribute('data-part');
    var form=document.getElementById('qf');
    if(form){fill(text);e.preventDefault();document.getElementById('quote').scrollIntoView({behavior:innerWidth<=900?'smooth':'instant',block:'start'})}
    else{store('tpf-part',text)}
  });
  function fill(t){var d=document.getElementById('q-desc');if(!d){var e=document.getElementById('e-desc');if(e){e.value=t+'\nMi modelo: ';}return}document.getElementById('q-type').value='Replacement part';d.value=t+'\nMy model: ';setTimeout(function(){document.getElementById('q-name').focus({preventScroll:true})},600)}
@@DRAFT@@
  var pending=take('tpf-part');if(pending)fill(pending);
  // parts filter
  var list=document.getElementById('plist');
  if(list){
    var rows=[].slice.call(list.querySelectorAll('.row')),q=document.getElementById('cat-q'),fit=document.getElementById('fit-only'),more=document.getElementById('cat-more'),empty=document.getElementById('cat-empty'),count=document.getElementById('cat-count');
    var brand='All',limit=40;
    document.querySelectorAll('#cat-chips .chip').forEach(function(c){c.addEventListener('click',function(){brand=c.getAttribute('data-b');limit=40;document.querySelectorAll('#cat-chips .chip').forEach(function(k){k.setAttribute('aria-pressed',k===c)});render()})});
    function render(){var v=q.value.trim().toLowerCase(),n=0,shown=0;
      rows.forEach(function(r){var ok=(brand==='All'||r.getAttribute('data-b')===brand)&&(!fit.checked||r.getAttribute('data-fit')==='1')&&(!v||r.getAttribute('data-k').indexOf(v)>-1);if(ok)n++;var show=ok&&shown<limit;if(show)shown++;r.hidden=!show});
      more.hidden=n<=limit;more.textContent=(list.getAttribute('data-more')||'Show more')+' ('+(n-limit)+')';empty.hidden=n>0;count.textContent=n+' '+(n===1?(list.getAttribute('data-one')||'part'):(list.getAttribute('data-many')||'parts'));}
    function syncURL(){try{var p=new URLSearchParams();if(brand!=='All')p.set('brand',brand);if(q.value.trim())p.set('q',q.value.trim());if(!fit.checked)p.set('all','1');if(srt&&srt.value)p.set('sort',srt.value);var qs=p.toString();history.replaceState(null,'',location.pathname+(qs?'?'+qs:''))}catch(e){}}
    var srt=document.getElementById('cat-sort'),orig=rows.slice();
    function key(r,k){if(k==='name')return r.querySelector('.n').textContent.trim().toLowerCase();if(k==='brand')return (r.getAttribute('data-b')+' '+r.querySelector('.n').textContent).toLowerCase();if(k==='pn')return r.querySelector('.o').textContent.replace(/^\S+\s+\S+\s+/,'').toLowerCase();return ''}
    function applySort(){var k=srt?srt.value:'';rows=k?orig.slice().sort(function(a,b){return key(a,k).localeCompare(key(b,k),undefined,{numeric:true})}):orig.slice();rows.forEach(function(r){list.appendChild(r)})}
    if(srt)srt.addEventListener('change',function(){applySort();limit=40;render()});
    var rr=render;render=function(){rr();syncURL()};
    try{var P=new URLSearchParams(location.search);if(P.get('q'))q.value=P.get('q');if(P.get('all')==='1')fit.checked=false;if(srt&&P.get('sort')){srt.value=P.get('sort');applySort()}var pb=P.get('brand');if(pb){var ch=[].find.call(document.querySelectorAll('#cat-chips .chip'),function(x){return x.getAttribute('data-b').toLowerCase()===pb.toLowerCase()});if(ch){brand=ch.getAttribute('data-b');document.querySelectorAll('#cat-chips .chip').forEach(function(k){k.setAttribute('aria-pressed',k===ch)})}}}catch(e){}
    q.addEventListener('input',function(){limit=40;render()});fit.addEventListener('change',function(){limit=40;render()});more.addEventListener('click',function(){limit+=60;render()});render();
  }
@@MENU@@
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
      st.textContent='Copy your request, then send it to us with a photo of the part.';
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
        if not p and anchor in SECTION_PAGES:
            p, anchor = SECTION_PAGES[anchor], ""
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

SECTION_PAGES = {"quote": "quote/", "business": "business/", "process": "process/", "materials": "materials/", "about": "about/", "services": "services/", "parts": "parts/"}
def ld(obj): return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False).replace("</", "<\\/") + "</script>"

ORG = {"@context": "https://schema.org", "@type": "LocalBusiness", "@id": BASE + "/#business", "name": "True Part Fabrication LLC",
       "url": BASE + "/", "logo": BASE + "/assets/img/logo-dark.png", "image": BASE + "/assets/img/og-image.jpg",
       "description": "Custom part manufacturing, replacement parts, and small-batch production in Modesto, California.",
       "address": {"@type": "PostalAddress", "addressLocality": "Modesto", "addressRegion": "CA", "addressCountry": "US"},
       "areaServed": ["Modesto", "Ceres", "Turlock", "Manteca", "Tracy", "Stockton", "Stanislaus County", "San Joaquin County"],
       "sameAs": [EBAY],
       "knowsAbout": ["Additive manufacturing", "Replacement parts", "Reverse engineering", "Jigs and fixtures", "Small-batch manufacturing"]}

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
<meta property="og:image:alt" content="True Part Fabrication logo over custom manufactured parts">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0A3161">
<script>try{{var t=localStorage.getItem("tpf-theme");if(t==="light"||t==="black")document.documentElement.setAttribute("data-tpf-theme",t)}}catch(e){{}}</script>
<link rel="icon" type="image/png" sizes="32x32" href="{c.asset('img/favicon-32.png')}">
<link rel="icon" type="image/png" sizes="48x48" href="{c.asset('img/favicon-48.png')}">
<link rel="apple-touch-icon" href="{c.asset('img/icon-180.png')}">
<link rel="manifest" href="{c.asset('manifest.webmanifest')}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@100..125,400..700&family=Instrument+Serif:ital@0;1&family=Instrument+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="{c.asset('site.css')}?v=10">
"""
    return h + "\n".join(ld(x) for x in lds)

def header(c):
    import extras as X
    L = c.link
    mb, mp = X.menu(c)
    return f"""<a href="#main" class="skip" style="position:absolute;left:-9999px;top:0;z-index:50;background:var(--accent);color:#fff;padding:10px 16px" onfocus="this.style.left='12px'" onblur="this.style.left='-9999px'">Skip to content</a>
<div class="opening" role="note"><div class="wrap">Opening January 1, 2027 <span aria-hidden="true">·</span> <a href="{L('', 'quote')}">Quote requests welcome now</a> <span aria-hidden="true">·</span> <a href="{L('es/')}" hreflang="es" lang="es">Español</a></div></div>
<header id="hdr">
  <div class="wrap bar">
    <a class="brand" href="{L('')}" aria-label="True Part Fabrication home"><img src="{c.asset('img/logo-dark.png')}" alt="True Part Fabrication" width="800" height="493"></a>
    <nav class="main" aria-label="Main">
      <a class="l" href="{L('services/')}">Services</a>
      <a class="l" href="{L('', 'business')}">For business</a>
      <a class="l" href="{L('', 'parts')}">Parts</a>
      <a class="l" href="{L('', 'process')}">Process</a>
      <a class="l" href="{L('resources/')}">Resources</a>
      <a class="l" href="{L('faq/')}">FAQ</a>
      <a class="l" href="{L('', 'about')}">About</a>
      <button class="theme-btn" type="button" id="theme-btn" aria-label="Theme"><svg class="dot" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="7" fill="currentColor"/></svg><svg class="moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg><svg class="sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg></button>
      <a class="icon-l s" href="{L('search/')}" aria-label="Search the site">{X.SEARCH_SVG}</a>
      <a class="list-pill" id="list-pill" href="{L('request-list/')}" hidden>Request list <b id="list-n">0</b></a>
      <a class="btn" href="{L('', 'quote')}">Request a quote</a>
      {mb}
    </nav>
  </div>
</header>
{mp}"""

def footer(c):
    import extras as X
    L = c.link
    PH = f'<li><a href="{X.tel(X.PHONE)}">Call {X.PHONE}</a></li>' if X.PHONE else ''
    return f"""<footer>
  <div class="wrap">
    <div class="foot">
      <div><img src="{c.asset('img/logo-dark.png')}" alt="True Part Fabrication" width="800" height="493" loading="lazy"><p style="color:var(--muted);margin-top:18px;max-width:28em;font-size:.95rem">Replacement parts, custom fabrication, and small-batch manufacturing in Modesto, California.</p></div>
      <div><h4>Explore</h4><ul><li><a href="{L('services/')}">Services</a></li><li><a href="{L('', 'business')}">For business</a></li><li><a href="{L('parts/')}">Compatible parts</a></li><li><a href="{L('pricing/')}">Pricing</a></li><li><a href="{L('projects/')}">Projects</a></li><li><a href="{L('', 'process')}">Process</a></li><li><a href="{L('resources/')}">Resources</a></li><li><a href="{L('tools/hose-size-finder/')}">Hose size finder</a></li><li><a href="{L('tools/adapter-builder/')}">Adapter builder</a></li><li><a href="{L('glossary/')}">Glossary</a></li><li><a href="{L('faq/')}">FAQ</a></li></ul></div>
      <div><h4>Contact</h4><ul><li><a href="{L('', 'quote')}">Request a quote</a></li><li><a href="{L('reorder/')}">Reorder a part</a></li><li><a href="{L('request-list/')}">Request list</a></li>{PH}<li><a href="{EBAY}" target="_blank" rel="noopener">eBay store</a></li><li><a href="{L('search/')}">Search</a></li><li><a href="{L('es/')}" hreflang="es" lang="es">Español</a></li><li><a href="{L('privacy/')}">Privacy</a></li><li><a href="{L('terms/')}">Terms of Service</a></li><li><a href="{L('sitemap/')}">Site map</a></li></ul></div>
    </div>
    <div class="copy-line"><span>© 2026 True Part Fabrication LLC</span><span>Modesto · Ceres · Turlock · Manteca · Tracy · Stockton</span></div>
  </div>
</footer>
<script src="{c.asset('site.js')}?v=10" defer></script>"""

SWAP = re.compile(r'<img([^>]*?) src="([^"]*assets/img/)(logo-dark\.png|hero\.jpg|svc-[a-z]+\.jpg|sample-[a-z]+\.jpg)"')
def swapimgs(h):
    def r(m):
        name = m.group(3)
        light = "logo-light.png" if name == "logo-dark.png" else name.replace(".jpg", "-light.jpg")
        black = "logo-black.png" if name == "logo-dark.png" else name.replace(".jpg", "-black.jpg")
        return '<img' + m.group(1) + ' src="' + m.group(2) + name + '" data-light="' + m.group(2) + light + '" data-black="' + m.group(2) + black + '"'
    return SWAP.sub(r, h)
MM = {"15/16 in": "23.8 mm", "1 in": "25.4 mm", "1-1/4 in": "31.8 mm", "1-3/8 in": "34.9 mm", "1-1/2 in": "38.1 mm", "1-2/3 in": "42.3 mm", "1-3/4 in": "44.5 mm",
      "1-7/8 in": "47.6 mm", "2 in": "50.8 mm", "2-1/4 in": "57.2 mm", "2-1/2 in": "63.5 mm", "4 in": "101.6 mm",
      "22 mm": "0.87 in", "24 mm": "0.94 in", "32 mm": "1.26 in", "35 mm": "1.38 in", "36 mm": "1.42 in", "38 mm": "1.50 in"}
def _sz(m):
    v = m.group(1); alt = MM.get(html.unescape(v))
    return f'<span class="sz">{v}<small> · {alt}</small></span>' if alt else m.group(0)
def a11y(h):
    h = re.sub(r'<span class=(?:"sz"|sz)>([^<]+)</span>', _sz, h)
    h = h.replace('logo-dark.png"', 'logo-dark.png?v=9"')
    h = h.replace('<div class="ftable">', '<div class="ftable" tabindex="0" role="region" aria-label="Scrollable table">')
    h = h.replace('<div class="tbl">', '<div class="tbl" tabindex="0" role="region" aria-label="Scrollable table">')
    return __import__("improve").post(h)
def webp(h):
    h = re.sub(r"(assets/img/(?:hero|svc-[a-z]+|sample-[a-z]+)(?:-light|-black)?)\.jpg", r"\1.webp?v=6", h)
    return h.replace(".replace('.jpg','-light.jpg')", ".replace('.webp','-light.webp')")
def doc(c, headhtml, body, art_index=False):
    return a11y(webp(swapimgs(_doc(c, headhtml, body, art_index))))
def _doc(c, headhtml, body, art_index=False):
    if art_index:
        return headhtml + "\n<meta name=\"claude:viewport-fit-sides\" content=\"cover\">\n" + header(c) + "\n" + body + "\n" + footer(c) + "\n"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
{headhtml}{ALT if c.path == "" else ""}
</head>
<body>
{header(c)}
{body}
{footer(c)}
</body>
</html>
"""

ALT = f'\n<link rel="alternate" hreflang="en" href="{BASE}/">\n<link rel="alternate" hreflang="es" href="{BASE}/es/">\n<link rel="alternate" hreflang="x-default" href="{BASE}/">'
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
        out.append(f"""<article class="pc"><div class="ph"><img src="{c.asset('img/sample-' + it['i'] + '.jpg')}" alt="Sample image of a custom manufactured {it['i']}" width="640" height="480" loading="lazy"><span>Sample image</span></div>
<div class="bd"><div class="br">Fits {esc(it['b'])}</div><h4><a href="{c.link('parts/' + it['slug'] + '/')}">{esc(it['n'])}</a></h4><div class="rp">{esc(rp(it))}</div><div class="ft">{esc('Fits ' + it['f']) if it['f'] else 'Ask us to confirm your model'}</div>
<a class="go" href="{c.link('', 'quote')}" data-part="{esc(part_text(it))}">Request this part →</a></div></article>""")
    return "\n".join(out)

# ---------------- HOME ----------------
def home(c, art=False, raw=False):
    main = re.search(r'(<main id="top">.*?</main>)', TPL, re.S).group(1)
    main = main.replace('<main id="top">', '<main id="main">').replace('{{TERMS}}', c.link('terms/'))
    # img data URIs -> files
    main = re.sub(r'src="data:image/png;base64,[^"]+"', f'src="{c.asset("img/logo-dark.png")}"', main)
    for k in ["HERO", "ADAPTER", "BRACKET", "ENCLOSURE", "BATCH"]:
        main = main.replace("{{IMG_" + k + "}}", c.asset("img/" + ("hero" if k == "HERO" else "svc-" + k.lower()) + ".jpg"))
    check = '<svg viewBox="0 0 22 22" fill="none" stroke="var(--accent-hi)" stroke-width="1.8" aria-hidden="true"><circle cx="11" cy="11" r="10"/><path d="M6.5 11.5l3 3 6-6.5"/></svg>'
    main = main.replace("{{CHECK}}", check)
    main = main.replace('<img src="' + c.asset("img/svc-"), '<img loading="lazy" src="' + c.asset("img/svc-"))
    # additive: link to the full parts page beside the eBay button
    main = main.replace('<div class="parts-top"><h3>Popular parts</h3><a class="btn ghost" href="https://www.ebay.com/usr/truepartfabrication"',
        '<div class="parts-top"><h3>Popular parts</h3><div style="display:flex;gap:10px;flex-wrap:wrap"><a class="btn ghost" href="' + c.link('parts/') + '">Parts catalog page <span class="ar">→</span></a><a class="btn ghost" href="https://www.ebay.com/usr/truepartfabrication"',1)
    main = main.replace('Shop ready-made parts on eBay <span class="ar">↗</span></a></div>','Shop ready-made parts on eBay <span class="ar">↗</span></a></div></div>',1)
    # ---- link text to matching resource pages (additive; wording unchanged) ----
    def A(p, text, frag=""):
        return '<a href="' + c.link(p, frag) + '">' + text + '</a>'
    for nm, sl in [("DeWalt","dewalt"),("Milwaukee","milwaukee"),("Ryobi","ryobi"),("Ridgid","ridgid"),("Makita","makita"),("Craftsman","craftsman"),("Shop-Vac","shop-vac"),("Vacmaster","vacmaster"),("WEN","wen"),("Shark","shark"),("Prolux","prolux"),("Samsung","samsung"),("Hampton Bay","hampton-bay")]:
        main = main.replace("<span>" + nm + "</span>", '<a href="' + c.link("brands/" + sl + "/") + '">' + nm + "</a>", 1)
    TAGS = [("Dust adapters","tools/hose-size-finder/"),("Hose fittings","glossary/dust-port-hose-sizes/"),("Clips &amp; covers","glossary/clips-and-covers/"),("Rollers","glossary/roller/"),
            ("Brackets","glossary/bracket/"),("Jigs &amp; fixtures","glossary/jig/"),("Prototypes","glossary/prototyping/"),("Organizers","glossary/organizer/"),
            ("Enclosures","glossary/enclosure/"),("No tooling","glossary/small-batch-manufacturing/"),("No 1,000-unit minimums","glossary/small-batch-manufacturing/"),("Repeat orders","faq/")]
    for t_, p_ in TAGS:
        main = main.replace("<li>" + t_ + "</li>", "<li>" + A(p_, t_) + "</li>", 1)
    for b_, p_, f_ in [("Free reprint","faq/",""),("300 mm³","","materials"),("Modesto, CA","faq/","")]:
        main = re.sub(r'<div><b>' + re.escape(b_) + r'</b><span>([^<]*)</span></div>', lambda m: '<a class="fact" href="' + c.link(p_, f_) + '"><b>' + b_ + '</b><span>' + m.group(1) + '</span></a>', main, 1)
    main = main.replace("<p>Send photos, the broken piece,", "<p>" + A("guides/how-to-measure-a-part/", "Send photos") + ", the broken piece,", 1)
    main = main.replace("<p>Calipers in the shop,", "<p>" + A("guides/how-to-measure-a-part/", "Calipers") + " in the shop,", 1)
    main = main.replace("Send us your measurements or the part,", "Send us your " + A("guides/how-to-measure-a-part/", "measurements") + " or the part,", 1)
    main = main.replace("Code-compliance parts and food-contact parts", "Code-compliance parts and " + A("glossary/food-contact/", "food-contact parts"), 1)
    main = main.replace("then email the request to us with a photo of the part.", "then email the request to us with a " + A("guides/how-to-measure-a-part/", "photo of the part") + ".", 1)
    # glossary links in materials table + process
    for name, slug in [("PLA / PLA-CF", "pla"), ("PETG", "petg"), ("ASA / ABS", "asa"), ("PA-CF (nylon carbon)", "pa-cf")]:
        main = re.sub(r'(<td class="m"><i style="background:#[0-9A-F]{6}"></i>)' + re.escape(name) + "</td>", r'\1<a href="' + c.link("glossary/" + slug + "/") + '">' + name + "</a></td>", main)
    main = main.replace("<h3>We model</h3><p>Drawn in CAD,", f'<h3>We model</h3><p>Drawn in <a href="{c.link("glossary/cad/")}">CAD</a>,')
    main = main.replace('<p class="note">Heat limits are typical published ranges and vary by brand and print settings.</p>',
        f'<p class="note">Heat limits are typical published ranges and vary by brand and print settings. See <a href="{c.link("glossary/heat-deflection-temperature/")}" style="color:var(--muted)">heat deflection temperature</a>.</p>')
    # learn strip before quote
    strip = "".join(f'<a href="{c.link("glossary/" + s + "/")}">{esc(GLOSS[s]["term"].split(" (")[0])}</a>' for s in ["petg", "asa", "tolerance", "infill", "reverse-engineering", "dust-port-hose-sizes", "small-batch-manufacturing", "fit-types"])
    tools_sec = f"""<section id="tools" style="border-top:1px solid var(--line);padding-block:100px">
  <div class="wrap">
    <div class="head"><div class="label">Free tools</div><h2>Size it, pick it, <em class="s">measure it.</em></h2><p>Free resources to help you find the right fit and get an accurate quote the first time.</p></div>
    <div class="res-grid">
      <a class="res" href="{c.link('tools/hose-size-finder/')}"><div class="k">Tool</div><h3>Hose &amp; dust port size finder</h3><p>Look up hose and port sizes for hundreds of wet/dry vacs, collectors, and tools.</p><span class="go">Find a size →</span></a>
      <a class="res" href="{c.link('tools/material-picker/')}"><div class="k">Tool</div><h3>Material picker</h3><p>Five questions to the right material, plus a PLA vs PETG vs ASA comparison.</p><span class="go">Pick a material →</span></a>
      <a class="res" href="{c.link('guides/how-to-measure-a-part/')}"><div class="k">Guide</div><h3>How to measure a part</h3><p>Photograph and measure a broken part so we can model it right the first time.</p><span class="go">Read the guide →</span></a>
    </div>
  </div>
</section>

"""
    main = main.replace('<div class="brands">', tools_sec + '<div class="brands">', 1)
    for nm, sl in [("Food processing", "food-processing"), ("Agriculture", "agriculture"), ("Warehouse &amp; cold storage", "warehouse-cold-storage"), ("Industrial shops", "industrial-shops")]:
        main = main.replace("<div><h3>" + nm + "</h3>", '<div><h3><a href="' + c.link("industries/" + sl + "/") + '" style="color:inherit;text-decoration:none">' + nm + "</a></h3>", 1)
    import extras as X
    for k_, s_ in [("Replacement parts","replacement-parts"),("Custom fabrication","custom-fabrication"),("Electronics &amp; products","electronics-enclosures"),("Small-batch runs","small-batch-manufacturing")]:
        main = re.sub(r'(<div class="k">' + re.escape(k_) + r'</div>.*?</ul>)', lambda m: m.group(1) + '<a class="svc-more" href="' + c.link("services/" + s_ + "/") + '">More about ' + re.sub("<[^>]+>","",k_).replace("&amp;","&").lower() + ' →</a>', main, count=1, flags=re.S)
    about_more = f'''<div class="about-more">
          <div><b>Company</b><span>True Part Fabrication LLC, a California company based in Modesto</span></div>
          <div><b>Opening</b><span>January 1, 2027. Quote requests welcome now; hours posted at opening</span></div>
          <div><b>In the shop</b><span>Enclosed additive manufacturing equipment, parts up to 300 mm, CAD modeling, precision measuring</span></div>
          <div><b>On site</b><span>Measuring at your location across Modesto, Ceres, Turlock, Manteca, Tracy, and Stockton</span></div>
          <div><b>Guarantee</b><span><a href="{c.link('terms/')}">Free reprint</a> if a part doesn't fit</span></div>
          <div><b>See more</b><span><a href="{c.link('projects/')}">Projects</a> · <a href="{c.link('pricing/')}">Pricing</a> · <a href="{c.link('services/')}">Services</a></span></div>
        </div>'''
    main = main.replace('''        </div>
      </div>
      <div class="scope">''', '''        </div>
        ''' + about_more + '''
      </div>
      <div class="scope">''', 1)
    if X.PHONE:
        main = main.replace('<div class="ci"><b>Location</b>', f'<div class="ci"><b>Phone</b><span><a href="{X.tel(X.PHONE)}">{X.PHONE}</a></span></div><div class="ci"><b>Location</b>', 1)
    main = main.replace('<section id="quote"', '<section id="notify" style="border-top:1px solid var(--line);padding-block:72px"><div class="wrap">' + X.notify_block(c) + '</div></section>\n\n<section id="quote"', 1)
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
    title = "Custom Part Manufacturing & Replacement Parts in Modesto, CA | True Part Fabrication"
    desc = "True Part Fabrication designs and manufactures replacement parts, custom brackets, jigs, fixtures, and small-batch runs for businesses in Modesto, Turlock, Stockton, and the Central Valley. Free reprint if it doesn't fit."
    org = dict(ORG)
    web = {"@context": "https://schema.org", "@type": "WebSite", "name": SITE, "url": BASE + "/"}
    script = TPL[TPL.index('<script id="cat-data"'):]
    sample = json.dumps({k: c.asset('img/sample-' + k + '.jpg') for k in ['adapter','nozzle','brush','separator','clip','roller']})
    script = script.replace("im.src=IMG[it.i];", "var s0=IMG[it.i],th=document.documentElement.getAttribute('data-tpf-theme');im.setAttribute('data-dark',s0);im.setAttribute('data-light',s0.replace('.webp','-light.webp'));im.setAttribute('data-black',s0.replace('.webp','-black.webp'));im.src=(th==='light'||th==='black')?im.getAttribute('data-'+th):s0;")
    script = script.replace("bd.appendChild(el('h4',null,it.n));", "var h4=el('h4');var ha=el('a',null,it.n);ha.href=it.u;h4.appendChild(ha);bd.appendChild(h4);")
    script = script.replace("r.appendChild(el('div','n',it.n));", "var nd=el('div','n');var na=el('a',null,it.n);na.href=it.u;nd.appendChild(na);r.appendChild(nd);")
    CATU = {"feat": CAT["feat"], "items": [dict(x, u=c.link("parts/" + x["slug"] + "/")) for x in CAT["items"]]}
    script = script.replace('{{CAT}}', json.dumps(CATU, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')).replace('{{IMG_SAMPLE}}', sample)
    main = main.replace('<div class="r"><a class="btn" id="q-mail" href="#">Open in email</a>', '<div class="r"><a class="btn" id="q-mail" href="#">Open in email</a>', 1)
    main = main.replace('''        <div class="r"><a class="btn" id="q-mail"''', '''        <div class="next"><h3>What happens next</h3><ol><li>Send the email with a photo of the part.</li><li>We reply with questions or a written quote: material, price, and turnaround.</li><li>You approve, we model and print, and the part is checked for fit before it ships.</li></ol></div>
        <div class="r"><a class="btn" id="q-mail"''', 1)
    if raw: return main, script
    main = main + '\n<script>window.TPF_HOME=1</script>\n' + script
    return doc(c, head(c, title, desc, [org, web]), main, art_index=art)

# ---------------- SECTION PAGES (own page per menu item) ----------------
SECTION_META = {
 "business": ("For business", "Custom Parts for Businesses in the Central Valley | True Part Fabrication", "Replacement and custom parts for food processing, agriculture, warehouses, cold storage, and industrial shops in Modesto, Turlock, Stockton, and the Central Valley."),
 "process": ("Process", "How It Works: From Broken Part to Perfect Fit | True Part Fabrication", "Our six-step process: you tell us, we measure, we model, you approve the quote, we print, and it fits, or we reprint it free."),
 "materials": ("Materials", "Materials We Print: PLA, PETG, ASA, Nylon & TPU | True Part Fabrication", "Engineering materials for custom and replacement parts, with typical heat limits, strengths, and where each one fits best."),
 "about": ("About", "About True Part Fabrication | Modesto, CA", "True Part Fabrication is a California manufacturing and product development company in Modesto, making replacement parts, custom components, and small-batch runs."),
 "quote": ("Request a quote", "Request a Quote | True Part Fabrication", "Describe your part and get a written quote with material, price, and turnaround. Free reprint if it doesn't fit."),
}
def section_page(c, sid):
    main, script = home(c, raw=True)
    m = re.search(r'(<section id="' + sid + r'"[^>]*>.*?</section>)', main, re.S)
    sec = m.group(1).replace(' style="border-top:1px solid var(--line)"', '', 1)
    name, title, desc = SECTION_META[sid]
    # each page gets one h1: promote the section's first h2, or add one
    if "<h2" in sec:
        i = sec.index("<h2"); j = sec.index("</h2>", i)
        sec = sec[:i] + "<h1" + sec[i+3:j] + "</h1>" + sec[j+5:]
    else:
        sec = sec.replace('<div class="label">About us</div></div>', '<div class="label">About us</div><h1>About True Part Fabrication</h1></div>', 1)
    extra = ""
    if sid == "quote":
        qs = script[script.index("var f=document.getElementById('qf')"):]
        qs = qs[:qs.rindex("})();")]
        extra = "\n<script>window.TPF_HOME=1</script>\n<script>(function(){\n" + qs + "\n})();</script>"
    body = f'''<main id="main" class="secpage">
<div class="wrap" style="padding-top:28px">{crumbs(c, [('Home', ''), (name, sid + '/')])}</div>
{sec}
</main>{extra}'''
    return doc(c, head(c, title, desc, [crumbs_ld([("Home", ""), (name, sid + "/")])]), body)

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
        rows.append(f"""<div class="row" data-b="{esc(it['b'])}" data-fit="{1 if it['f'] else 0}" data-k="{esc(k)}"><div class="b">{esc(it['b'])}</div><h3 class="n" style="font:600 1rem var(--f-body);text-transform:none;letter-spacing:0"><a href="{c.link('parts/' + it['slug'] + '/')}">{esc(it['n'])}</a>{badge}</h3><div class="o">{esc(rp(it))}</div><div class="f">{esc(it['f'] or 'Ask us to confirm your model')}</div><a class="btn ghost" style="height:34px;padding:0 14px;font-size:.8rem" href="{c.link('', 'quote')}" data-part="{esc(part_text(it))}">Request</a></div>""")
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
    <label class="sortbox" for="cat-sort">Sort<select id="cat-sort"><option value="">Featured</option><option value="name">Name A–Z</option><option value="brand">Brand A–Z</option><option value="pn">Part number</option></select></label>
    <span id="cat-count" style="color:var(--faint);font-size:.88rem;margin-left:auto"></span>
  </div>
  <div class="recent" id="recent" hidden><div class="head" style="margin:0 0 14px"><div class="label">Recently viewed</div></div><div class="rel" id="recent-list" style="margin-bottom:28px"></div></div>
  <div class="chips" id="cat-chips" role="group" aria-label="Filter by brand" style="margin-bottom:22px">{chips}</div>
  <div class="list" id="plist">
{chr(10).join(rows)}
  </div>
  <p class="empty" id="cat-empty" hidden>No parts match. Turn off "Confirmed fit only," try the <a href="{c.link('search/')}">site search</a>, build a custom piece in the <a href="{c.link('tools/adapter-builder/')}">adapter builder</a>, or describe your part in the <a href="{c.link('', 'quote')}" style="color:var(--ink)">quote form</a>.</p>
  <div class="more"><button class="btn ghost" type="button" id="cat-more" hidden>Show more</button></div>
  <p class="legal">These are compatible aftermarket parts made by True Part Fabrication, not original manufacturer parts. Brand names and part numbers belong to their owners and are used only to describe fit. True Part Fabrication is not affiliated with or endorsed by any brand listed. Learn more about <a href="{c.link('glossary/aftermarket-part/')}" style="color:var(--muted)">aftermarket parts</a>.</p>
</div></section>
</main>"""
    title = "Compatible Replacement Parts for DeWalt, Milwaukee, Ryobi & More | True Part Fabrication"
    desc = f"Browse {len(items)} made-to-order aftermarket parts: dust adapters, nozzles, brushes, clips, and fittings that fit DeWalt, Milwaukee, Ryobi, RIDGID, WEN, Shark, and more. Made to order in Modesto, CA."
    lds = [crumbs_ld([("Home", ""), ("Compatible parts", "parts/")]),
           {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Compatible replacement parts", "url": BASE + "/parts/", "isPartOf": {"@id": BASE + "/#business"}}]
    return doc(c, head(c, title, desc, lds), body)

# ---------------- FAQ ----------------
def FAQS(c):
    G = lambda s, t: f'<a href="{c.link("glossary/" + s + "/")}">{t}</a>'
    return [
     ("When do you open?", f"<p>We open January 1, 2027. You can send quote requests now, and we'll reply with questions or a written quote so your job is ready to start when we open.</p>"),
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
<div class="wrap"><div class="filterbar"><label for="faq-q" style="position:absolute;left:-9999px">Filter questions</label><input id="faq-q" type="search" placeholder="Filter questions, e.g. price, reprint, material"><button type="button" class="tbtn" id="faq-all">Expand all</button><span id="faq-n" role="status" style="color:var(--faint);font-size:.88rem"></span></div></div>
<div class="wrap faq">{det}</div>
<script>(function(){{var q=document.getElementById('faq-q'),d=[].slice.call(document.querySelectorAll('.faq details')),b=document.getElementById('faq-all'),n=document.getElementById('faq-n');
q.addEventListener('input',function(){{var v=q.value.trim().toLowerCase(),k=0;d.forEach(function(x){{var ok=!v||x.textContent.toLowerCase().indexOf(v)>-1;x.hidden=!ok;if(ok)k++;if(v&&ok)x.open=true}});n.textContent=v?k+(k===1?' question':' questions'):''}});
b.addEventListener('click',function(){{var open=b.textContent==='Expand all';d.forEach(function(x){{x.open=open}});b.textContent=open?'Collapse all':'Expand all'}})}})();</script>
<div class="cta-band"><div class="wrap"><h2>Still have a question?</h2><p>Describe your part and we'll reply with questions or a written quote.</p><a class="btn" href="{c.link('', 'quote')}">Request a quote <span class="ar">→</span></a></div></div>
</main>"""
    strip = lambda s: re.sub("<[^>]+>", "", s).strip()
    faqld = {"@context": "https://schema.org", "@type": "FAQPage",
             "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip(a)}} for q, a in items]}
    return doc(c, head(c, "Custom Manufacturing & Replacement Parts FAQ | True Part Fabrication",
                       "Answers about quotes, pricing, turnaround, materials, fit guarantee, and what True Part Fabrication can make. Custom part manufacturing in Modesto, CA.",
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
    az = "".join(f'<a href="{c.link("glossary/" + t["slug"] + "/")}" title="{esc(t["term"])}">{esc(t["term"].split(" (")[0])}</a>' for t in sorted(TERMS, key=lambda t: t["term"].lower()))
    body = f"""<main id="main">
<div class="page-hero"><div class="wrap">
  {crumbs(c, [('Home', ''), ('Glossary', 'glossary/')])}
  <h1>Manufacturing and replacement parts glossary</h1>
  <p class="lead">Plain-English definitions of the materials, fits, and manufacturing terms that come up when you order a custom or replacement part, and what each one means for your part.</p>
  <div class="terms-strip">{jump}</div>
  <div class="filterbar"><label for="gl-q" style="position:absolute;left:-9999px">Filter terms</label><input id="gl-q" type="search" placeholder="Filter terms, e.g. heat, fit, nylon"><span id="gl-n" role="status" style="color:var(--faint);font-size:.88rem"></span></div>
  <nav class="az" aria-label="Terms A to Z">{az}</nav>
</div></div>
<div class="wrap" style="padding-bottom:60px">{''.join(groups)}</div>
<script>(function(){{var q=document.getElementById('gl-q'),n=document.getElementById('gl-n'),cards=[].slice.call(document.querySelectorAll('.gcard')),grp=[].slice.call(document.querySelectorAll('.gloss-group'));
q.addEventListener('input',function(){{var v=q.value.trim().toLowerCase(),k=0;cards.forEach(function(c){{var ok=!v||c.textContent.toLowerCase().indexOf(v)>-1;c.hidden=!ok;if(ok)k++}});grp.forEach(function(g){{g.hidden=!g.querySelector('.gcard:not([hidden])')}});n.textContent=v?k+(k===1?' term':' terms'):''}})}})();</script>
<div class="cta-band"><div class="wrap"><h2>Have a part in mind?</h2><p>You don't need the vocabulary to get a quote. Describe what broke and we'll handle the rest.</p><a class="btn" href="{c.link('', 'quote')}">Request a quote <span class="ar">→</span></a></div></div>
</main>"""
    setld = {"@context": "https://schema.org", "@type": "DefinedTermSet", "name": "True Part Fabrication glossary", "url": BASE + "/glossary/",
             "hasDefinedTerm": [{"@type": "DefinedTerm", "name": t["term"], "description": t["short"], "url": BASE + "/glossary/" + t["slug"] + "/"} for t in TERMS]}
    return doc(c, head(c, "Manufacturing Glossary: Materials, Fits & Terms | True Part Fabrication",
                       f"{len(TERMS)} plain-English definitions of manufacturing and replacement part terms: PETG, ASA, tolerance, infill, reverse engineering, hose sizes, and more.",
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
    <div class="box"><h2>Need a part?</h2><p>We design and manufacture replacement parts in Modesto, CA. Free reprint if it doesn't fit.</p><a class="btn ghost" href="{c.link('parts/')}" style="height:40px;font-size:.85rem">Browse compatible parts</a></div>
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
  <p>This website doesn't use accounts, tracking cookies, or advertising. The quote form doesn't send anything by itself: it prepares a request that you choose to send to us.</p>
  <p>When you send us a request, we receive what you include, such as your name, company, contact details, part description, photos, and files.</p>
  <h2>How we use it</h2>
  <p>We use your information only to answer your request, prepare quotes, make and deliver your parts, and keep records for repeat orders and our accounts. We don't sell or rent your information.</p>
  <h2>Files and part designs</h2>
  <p>Part photos, measurements, and models you send are used for your job and kept on file so we can reprint your part. Tell us if you'd like them deleted.</p>
  <h2>Third-party services</h2>
  <p>This site loads fonts from Google Fonts, which may log your IP address. Links to our eBay store take you to eBay, which has its own privacy policy.</p>
  <h2>Contact</h2>
  <p>Questions or deletion requests: contact us through the quote form on our home page.</p>
  <p style="color:var(--faint);font-size:.88rem">Last updated October 2026.</p>
</div></div>
</main>"""
    return doc(c, head(c, "Privacy | True Part Fabrication", "How True Part Fabrication handles the information you share with us.", [crumbs_ld([("Home", ""), ("Privacy", "privacy/")])]), body)


TERMS_SECTIONS = [
 ("About these terms", ["These terms apply to quotes, orders, and parts from True Part Fabrication LLC (\"we,\" \"us\"), a California company in Modesto. By sending a quote request or placing an order, you agree to them. Your written quote may add details for a specific job; if the quote and these terms differ, the quote controls for that job."]),
 ("Quotes and orders", ["Every job starts with a written quote that states the part, material, quantity, price, and estimated turnaround. Work begins after you approve the quote.", "Turnaround times are estimates. We'll tell you promptly if a job will take longer than quoted.", "Payment terms, including any deposit, are stated in your quote."]),
 ("Aftermarket parts", ["Our parts are aftermarket parts that we design and make. They are not original manufacturer (OEM) parts. Brand names and part numbers are used only to describe fit. We are not affiliated with or endorsed by any brand we mention.", "Using an aftermarket part may affect a manufacturer's warranty on your equipment. Check your warranty before installing one."]),
 ("Parts we don't make", ["We don't make parts where a failure could hurt someone, including safety-critical, life-safety, or load-bearing parts; pressurized or air-pressure parts; electrical parts and housings; automotive braking or steering parts; child-safety, medical, or pool-safety items; code-compliance parts; and parts that contact food or drink.", "We may decline any job, and we'll tell you why."]),
 ("Your information and designs", ["You're responsible for the accuracy of the measurements, photos, drawings, and files you send, and for describing how the part will be used.", "By sending us a part, drawing, or file, you confirm you have the right to have it reproduced or modified for your own use. We keep your part's model on file so we can reprint it for you; we don't sell it or make it for others without your permission."]),
 ("Fit guarantee", ["If a part we make doesn't fit the equipment described in your quote, tell us within 30 days of delivery. Send your measurements or the part, and we'll adjust the model and reprint it at no charge.", "The fit guarantee covers fit. It doesn't cover parts used outside the conditions described in your quote (for example, higher heat or load), parts that were modified after delivery, or problems caused by incorrect measurements or information you provided. In those cases we'll quote a corrected part."]),
 ("Intended use", ["You're responsible for confirming that a part is suitable for your equipment and use, and for installing it correctly. Additively manufactured (3D-printed) parts have different properties from molded parts; we'll recommend a material, but final suitability is your decision."]),
 ("Limitation of liability", ["To the extent the law allows, our total liability for any part or job is limited to the amount you paid for it, and we aren't liable for indirect or consequential losses such as downtime or lost profits. Nothing in these terms limits rights you have under law that can't be waived."]),
 ("Governing law", ["These terms are governed by the laws of the State of California."]),
 ("Changes and contact", ["We may update these terms. The version in effect when you approve a quote applies to that job. Questions about these terms: use the email link in the quote section of our home page."]),
]
def terms(c):
    toc = "".join(f'<li><a href="#t{i}" style="color:var(--ink)">{esc(h)}</a></li>' for i, (h, _) in enumerate(TERMS_SECTIONS))
    secs = "".join(f'<h2 id="t{i}">{esc(h)}</h2>' + "".join(f"<p>{esc(p)}</p>" for p in ps) for i, (h, ps) in enumerate(TERMS_SECTIONS))
    body = f"""<main id="main">
<div class="page-hero"><div class="wrap">
  {crumbs(c, [('Home', ''), ('Terms of Service', 'terms/')])}
  <h1>Terms of Service</h1>
  <p class="lead">The plain-language terms for quotes, orders, and our fit guarantee.</p>
</div></div>
<div class="wrap"><div class="prose terms">
  <nav aria-label="On this page"><ol style="margin:0;padding-left:20px;display:grid;gap:6px">{toc}</ol></nav>
  {secs}
  <p style="color:var(--faint);font-size:.88rem">Last updated October 2026.</p>
</div></div>
</main>"""
    return doc(c, head(c, "Terms of Service | True Part Fabrication", "Terms for quotes, orders, aftermarket parts, the fit guarantee, and what True Part Fabrication won't make.", [crumbs_ld([("Home", ""), ("Terms of Service", "terms/")])]), body)

def notfound(c):
    body = f"""<main id="main">
<div class="page-hero" style="border-bottom:0"><div class="wrap">
  <div class="label">404</div>
  <h1>We couldn't find that page</h1>
  <p class="lead">It may have moved, or the link may be mistyped. Search for it, or start from one of these pages:</p>
  <form class="sbox" action="{c.link('search/')}" method="get" role="search" style="margin-top:24px"><label for="nf-q" style="position:absolute;left:-9999px">Search the site</label><input id="nf-q" name="q" type="search" placeholder="Part number, brand, or topic"><button class="btn" type="submit">Search</button></form>
  <div class="terms-strip" style="margin-top:26px"><a href="{c.link('')}">Home</a><a href="{c.link('parts/')}">Compatible parts</a><a href="{c.link('tools/hose-size-finder/')}">Hose size finder</a><a href="{c.link('tools/material-picker/')}">Material picker</a><a href="{c.link('resources/')}">All resources</a><a href="{c.link('search/')}">Search</a><a href="{c.link('', 'quote')}">Request a quote</a></div>
</div></div>
</main>"""
    return doc(c, head(c, "Page not found | True Part Fabrication", "This page couldn't be found.", []), body)

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
    write(root, "assets/manifest.webmanifest", json.dumps({"name": "True Part Fabrication", "short_name": "True Part", "description": "Custom part manufacturing and replacement parts in Modesto, CA.",
        "start_url": "../", "scope": "../", "display": "standalone", "background_color": "#0A3161", "theme_color": "#0A3161",
        "icons": [{"src": "img/icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "img/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}]}, indent=1))
    write(root, "assets/site.js", JS.replace("@@MENU@@", __import__("extras").MENU_JS + __import__("extras").LIST_JS + __import__("improve").IMP_JS).replace("@@DRAFT@@", __import__("extras").DRAFT_JS))
    import tools, parts_pages
    parts_pages.assign_slugs(CAT["items"])
    pages = {"": lambda c: home(c, art=(mode == "art")), "parts/": parts, "faq/": faq, "glossary/": gloss_index, "privacy/": privacy, "terms/": terms}
    pages.update(tools.pages())
    for _sid in SECTION_META:
        pages[_sid + "/"] = (lambda c, _sid=_sid: section_page(c, _sid))
    pages.update(parts_pages.pages())
    import es, extras
    pages.update(es.pages())
    pages.update(extras.pages())
    import improve
    pages["sitemap/"] = lambda c: improve.sitemap_page(c, pages)
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
        nf = notfound(Ctx(mode, ""))
        nf = re.sub(r'(href|src)="(?!https?:|/|#|mailto:|data:)', r'\1="/', nf).replace('href="/./"', 'href="/"')
        write(root, "404.html", nf)
        write(root, "robots.txt", (f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n") if INDEX else "# Temporary address: block all crawling until the real domain is live.\nUser-agent: *\nDisallow: /\n")
    return urls

if __name__ == "__main__":
    u = build("render", "/home/claude/site")
    build("art", "/home/claude/site_art")
    print(len(u), "pages")
