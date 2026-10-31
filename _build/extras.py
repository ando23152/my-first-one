"""Pricing, service pages, reorder, projects, search, Spanish catalog, phone menu, notify sign-up."""
import re, html, json
import build as B
esc = html.escape

QUOTE_TO = "ando23152@gmail.com"
NOTIFY_ENDPOINT = ""   # Formspree URL (https://formspree.io/f/XXXX) once Nick creates it; empty = email fallback
PHONE = ""             # business phone, e.g. "(209) 555-0123"; empty = hidden

def tel(p): return "tel:+1" + re.sub(r"\D", "", p)[-10:]

EX_CSS = r"""
/* ---- reset template form box for compact forms ---- */
form.sbox,form.notify{padding:0;border:0;background:none;border-radius:0}
@media (max-width:560px){form.sbox,form.notify{padding:0}}
/* ---- phone menu ---- */
.menu-btn{display:none;width:42px;height:42px;border-radius:50%;border:1px solid var(--line);background:transparent;color:var(--ink);cursor:pointer;place-items:center}
.menu-btn svg{width:20px;height:20px}
.icon-l{display:inline-grid;place-items:center;width:42px;height:42px;border-radius:50%;border:1px solid var(--line);color:var(--ink)}
.icon-l svg{width:18px;height:18px}.icon-l:hover{border-color:var(--accent)}
.mnav{position:fixed;inset:0;top:var(--mnav-top,110px);background:var(--bg);z-index:40;overflow:auto;padding:12px 0 40px;border-top:1px solid var(--line)}
.mnav ul{list-style:none;margin:0;padding:0}
.mnav a{display:block;padding:16px 0;border-bottom:1px solid var(--line);color:var(--ink);text-decoration:none;font:500 1.15rem var(--f-body)}
.mnav .btn{display:inline-flex;margin-top:22px;font-size:1rem}
@media (max-width:900px){.menu-btn{display:inline-grid}nav.main .icon-l.s{display:none}nav.main{gap:10px}}
@media (max-width:420px){nav.main .btn{padding:0 14px;font-size:.8rem}nav.main .theme-btn{display:none}}
@media (max-width:380px){.brand img{height:44px}}
body.menu-open{overflow:hidden}
/* ---- notify ---- */
.notify{display:grid;grid-template-columns:1fr auto;gap:12px;max-width:560px;margin-top:22px}
.notify input{font:400 1rem var(--f-body);color:var(--ink);background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:0 20px;height:48px}
.notify .btn{height:48px}
.notify-msg{margin-top:12px;color:var(--muted);font-size:.92rem;min-height:1.3em}
@media (max-width:520px){.notify{grid-template-columns:1fr}}
/* ---- generic page bits ---- */
.cards3{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.cards2{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}
.card{padding:26px;border:1px solid var(--line);border-radius:8px;background:var(--surface);display:grid;gap:10px;align-content:start}
.card .k{font:500 .7rem var(--f-mono);letter-spacing:.16em;text-transform:uppercase;color:var(--accent-hi)}
.card h3{font-family:var(--f-body);font-stretch:100%;font-weight:600;font-size:1.1rem;text-transform:none;letter-spacing:0;line-height:1.3}
.card p,.card li{color:var(--muted)}
.card ul{margin:0;padding-left:18px;display:grid;gap:6px}
.card a{color:var(--ink)}
a.card{text-decoration:none;transition:border-color .2s}a.card:hover{border-color:var(--accent)}
.sec{padding-block:64px;border-top:1px solid var(--line)}
.sec:first-of-type{border-top:0}
.ptable{width:100%;border-collapse:collapse}
.ptable th,.ptable td{text-align:left;padding:16px 14px;border-bottom:1px solid var(--line);vertical-align:top}
.ptable th{font:500 .7rem var(--f-mono);letter-spacing:.14em;text-transform:uppercase;color:var(--faint)}
.ptable td{color:var(--ink)}.ptable td:first-child{font-weight:600}
.svc-more{display:inline-block;margin-top:14px;color:var(--ink);font-weight:600;font-size:.92rem}
.about-more{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;margin-top:26px}
.about-more div{border:1px solid var(--line);border-radius:6px;padding:16px 18px}
.about-more b{display:block;font:500 .7rem var(--f-mono);letter-spacing:.14em;text-transform:uppercase;color:var(--faint);margin-bottom:6px}
.about-more span{color:var(--ink);font-size:.95rem}
.about-more a{color:var(--ink)}
@media (max-width:960px){.cards3{grid-template-columns:1fr 1fr}}
@media (max-width:640px){.cards3,.cards2,.about-more{grid-template-columns:1fr}}
/* ---- forms on standalone pages ---- */
.xform{display:grid;grid-template-columns:1fr 1fr;gap:16px;max-width:820px}
.xform label{display:grid;gap:6px;font:500 .8rem var(--f-mono);letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.xform input,.xform textarea,.xform select{font:400 1rem var(--f-body);color:var(--ink);background:var(--surface);border:1px solid var(--line);border-radius:6px;padding:12px 14px;text-transform:none;letter-spacing:0}
.xform textarea{min-height:110px;resize:vertical}
.xform .full{grid-column:1/-1}
.xerr{color:var(--accent-hi);grid-column:1/-1}
@media (max-width:640px){.xform{grid-template-columns:1fr}}
/* ---- search ---- */
.sbox{display:flex;gap:12px;max-width:720px}
.sbox input{flex:1;font:400 1.1rem var(--f-body);color:var(--ink);background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:0 22px;height:54px}
.sres{list-style:none;margin:28px 0 0;padding:0;max-width:860px}
.sres li{border-bottom:1px solid var(--line)}
.sres a{display:grid;gap:4px;padding:18px 0;text-decoration:none;color:var(--ink)}
.sres a:hover h3{text-decoration:underline;text-decoration-color:var(--accent);text-underline-offset:3px}
.sres h3{font:600 1.05rem var(--f-body);text-transform:none;letter-spacing:0}
.sres span{font:.7rem var(--f-mono);letter-spacing:.14em;text-transform:uppercase;color:var(--accent-hi)}
.sres p{color:var(--muted);font-size:.92rem}
"""

SEARCH_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg>'
MENU_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>'

def menu(c, es=False):
    L = c.link
    if es:
        items = [("Servicios", L('es/', 'servicios')), ("Industrias", L('es/', 'industrias')), ("Cómo funciona", L('es/', 'proceso')),
                 ("Catálogo de piezas", L('es/piezas/')), ("Preguntas frecuentes", L('es/preguntas-frecuentes/')), ("English", L(''))]
        cta = ("Pedir cotización", L('es/', 'cotizar')); label = "Menú"
    else:
        items = [("Services", L('services/')), ("For business", L('', 'business')), ("Parts catalog", L('parts/')), ("Pricing", L('pricing/')),
                 ("Process", L('', 'process')), ("Resources", L('resources/')), ("FAQ", L('faq/')), ("About", L('', 'about')),
                 ("Reorder a part", L('reorder/')), ("Search", L('search/')), ("Español", L('es/'))]
        cta = ("Request a quote", L('', 'quote')); label = "Menu"
    if PHONE:
        items.append((("Llamar " if es else "Call ") + PHONE, tel(PHONE)))
    lis = "".join(f'<li><a href="{h}">{esc(t)}</a></li>' for t, h in items)
    btn = f'<button class="menu-btn" type="button" id="menu-btn" aria-expanded="false" aria-controls="mnav" aria-label="{label}">{MENU_SVG}</button>'
    tl = ("Tema", "Azul", "Negro", "Claro") if es else ("Theme", "Blue", "Black", "Light")
    themes = f'<div class="theme-row" role="group" aria-label="{tl[0]}"><span>{tl[0]}</span><button type="button" data-set-theme="dark" aria-pressed="false">{tl[1]}</button><button type="button" data-set-theme="black" aria-pressed="false">{tl[2]}</button><button type="button" data-set-theme="light" aria-pressed="false">{tl[3]}</button></div>'
    panel = f'<div class="mnav" id="mnav" hidden><div class="wrap"><nav aria-label="{label}"><ul>{lis}</ul><a class="btn" href="{cta[1]}">{esc(cta[0])} <span class="ar">→</span></a>{themes}</nav></div></div>'
    return btn, panel

MENU_JS = r"""
  var mb=document.getElementById('menu-btn'),mn=document.getElementById('mnav');
  if(mb&&mn){
    function setMenu(o){mn.hidden=!o;mb.setAttribute('aria-expanded',o);document.body.classList.toggle('menu-open',o);if(o){var h=document.getElementById('hdr');mn.style.setProperty('--mnav-top',(h.getBoundingClientRect().bottom)+'px')}}
    mb.addEventListener('click',function(){setMenu(mn.hidden)});
    mn.addEventListener('click',function(e){if(e.target.closest('a'))setMenu(false)});
    document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!mn.hidden){setMenu(false);mb.focus()}});
    addEventListener('resize',function(){if(innerWidth>900&&!mn.hidden)setMenu(false)});
  }
  // notify sign-up
  document.querySelectorAll('form.notify').forEach(function(f){
    f.addEventListener('submit',function(e){
      e.preventDefault();var i=f.querySelector('input[type=email]'),m=document.getElementById(f.getAttribute('data-msg')),es=f.getAttribute('data-lang')==='es';
      var v=i.value.trim();if(!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v)){m.textContent=es?'Escriba un correo válido.':'Enter a valid email address.';i.focus();return}
      var ep=f.getAttribute('data-endpoint');
      if(ep){fetch(ep,{method:'POST',headers:{'Accept':'application/json','Content-Type':'application/json'},body:JSON.stringify({email:v,list:'opening',lang:es?'es':'en'})}).then(function(r){m.textContent=r.ok?(es?'Listo. Le avisaremos cuando abramos.':"You're on the list. We'll email you when we open."):(es?'No se pudo enviar. Intente de nuevo.':'That didn’t go through. Please try again.')}).catch(function(){m.textContent=es?'No se pudo enviar. Intente de nuevo.':'That didn’t go through. Please try again.'});return}
      var subj=es?'Avísenme cuando abran':'Notify me when you open',body=(es?'Por favor avísenme cuando True Part Fabrication abra. Mi correo: ':'Please email me when True Part Fabrication opens. My email: ')+v;
      location.href='mailto:'+f.getAttribute('data-to')+'?subject='+encodeURIComponent(subj)+'&body='+encodeURIComponent(body);
      m.textContent=es?'Se abrió su correo. Envíe el mensaje para quedar en la lista.':'Your email app opened. Send the message to join the list.';
    });
  });
  // simple mailto forms (reorder)
  document.querySelectorAll('form.xform[data-mail]').forEach(function(f){
    f.addEventListener('submit',function(e){
      e.preventDefault();var err=f.querySelector('.xerr'),miss=[].slice.call(f.querySelectorAll('[required]')).filter(function(x){return !x.value.trim()});
      if(miss.length){err.hidden=false;miss[0].focus();return}err.hidden=true;
      var L=[f.getAttribute('data-title'),''];f.querySelectorAll('input,textarea,select').forEach(function(x){if(x.value.trim())L.push(x.getAttribute('data-l')+': '+x.value.trim())});
      location.href='mailto:'+f.getAttribute('data-to')+'?subject='+encodeURIComponent(f.getAttribute('data-title'))+'&body='+encodeURIComponent(L.join('\n'));
      var st=f.querySelector('[role=status]');if(st)st.textContent='Your email app opened with the request. Send it to finish.';
    });
  });
"""

def notify_block(c, es=False, idp="n1"):
    if es:
        h, p, ph, b = "Avísenme cuando abran", "Deje su correo y le avisaremos cuando abramos el 1 de enero de 2027. Nada más.", "su@correo.com", "Avísenme"
    else:
        h, p, ph, b = "Get notified when we open", "Leave your email and we'll send one message when we open on January 1, 2027. Nothing else.", "you@company.com", "Notify me"
    return f"""<div class="callout" style="max-width:760px"><div class="k">{'Apertura' if es else 'Opening day'}</div><h3 style="font:600 1.25rem var(--f-body);text-transform:none;letter-spacing:0;margin-top:8px">{h}</h3><p>{p}</p>
<form class="notify" data-to="{QUOTE_TO}" data-endpoint="{NOTIFY_ENDPOINT}" data-msg="{idp}-msg" data-lang="{'es' if es else 'en'}" novalidate><label for="{idp}-email" style="position:absolute;left:-9999px">{'Correo electrónico' if es else 'Email address'}</label><input type="email" id="{idp}-email" autocomplete="email" placeholder="{ph}" required><button class="btn" type="submit">{b} <span class="ar">→</span></button></form>
<p class="notify-msg" id="{idp}-msg" role="status"></p></div>"""

def hero(c, crumbs_list, h1, lead, extra=""):
    return f"""<div class="page-hero"><div class="wrap">
  {B.crumbs(c, crumbs_list)}
  <h1>{h1}</h1>
  <p class="lead">{lead}</p>{extra}
</div></div>"""

def cta(c, h="Ready to get a quote?", p="Describe your part and we'll reply with questions or a written quote. Free reprint if it doesn't fit."):
    return f'<div class="cta-band"><div class="wrap"><h2>{h}</h2><p>{p}</p><a class="btn" href="{c.link("", "quote")}">Request a quote <span class="ar">→</span></a></div></div>'

def G(c, slug, t): return f'<a href="{c.link("glossary/" + slug + "/")}">{t}</a>'

# ---------------- PRICING ----------------
def pricing(c):
    L = c.link
    rows = [("Size and print time", "Bigger and taller parts take longer to print and use more material. Size is usually the biggest single factor."),
            ("Material", f"{G(c,'petg','PETG')} and {G(c,'pla','PLA')} cost least. {G(c,'asa','ASA')}, {G(c,'tpu','TPU')}, and {G(c,'pa-cf','carbon-fiber nylon')} cost more and take more care to print."),
            ("Design work", f"A part we already have a model for costs least. Measuring and modeling a new part in {G(c,'cad','CAD')} is a one-time charge."),
            ("Quantity", f"The design charge is paid once, so the price per part drops as quantity goes up. See {G(c,'small-batch-manufacturing','small-batch manufacturing')}."),
            ("Fit precision", f"Tight {G(c,'fit-types','press or snap fits')} may need a test print before the final part."),
            ("Turnaround", "Standard turnaround is in your quote. Rush jobs that jump the queue cost more.")]
    tr = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in rows)
    ex = [("One replacement part we already model", "A catalog part, such as a dust adapter or crevice tool, printed to order. No design charge.", "Low end"),
          ("One new part from a broken original", "Measure, model, and print one part, with a test fit if needed.", "Low to middle"),
          ("A custom bracket, jig, or fixture", "Modeled from your drawing or measurements, then printed in the right material.", "Middle"),
          ("A small-batch run of 25 to 500 parts", "One design charge, then a per-part price that drops with quantity.", "Middle to high")]
    cards = "".join(f'<div class="card"><div class="k">{esc(r)} of the range</div><h3>{esc(h)}</h3><p>{esc(p)}</p></div>' for h, p, r in ex)
    body = f"""<main id="main">
{hero(c, [('Home',''),('Pricing','pricing/')], 'How pricing works', 'Most business jobs run from about $75 to $800 or more. Every job gets a written quote with the material, price, and turnaround before we print anything, and every part is covered by our free-reprint fit guarantee.')}
<div class="wrap">
<section class="sec"><div class="head"><div class="label">What sets the price</div><h2>Six things <em class="s">we price on.</em></h2></div>
<div class="ftable"><table class="ptable" style="min-width:560px"><thead><tr><th>Factor</th><th>How it affects your price</th></tr></thead><tbody>{tr}</tbody></table></div></section>
<section class="sec"><div class="head"><div class="label">Typical jobs</div><h2>Where common jobs <em class="s">usually land.</em></h2><p>Each is a rough guide within the $75 to $800+ range; your written quote is the real number.</p></div>
<div class="cards2">{cards}</div></section>
<section class="sec"><div class="head"><div class="label">Save money</div><h2>Ways to <em class="s">lower the cost.</em></h2></div>
<div class="cards3">
<div class="card"><h3>Send the original</h3><p>The broken part, even in pieces, makes modeling faster than working from photos. See the <a href="{L('guides/how-to-measure-a-part/')}">measuring guide</a>.</p></div>
<div class="card"><h3>Order more at once</h3><p>The design charge is paid once. Ordering spares now is cheaper than a second order later.</p></div>
<div class="card"><h3>Buy ready-made</h3><p>Some parts are already listed in our <a href="{B.EBAY}" target="_blank" rel="noopener">eBay store</a> at a fixed price. Repeat customers can <a href="{L('reorder/')}">reorder by part ID</a>.</p></div>
</div></section>
</div>
{cta(c)}
</main>"""
    return B.doc(c, B.head(c, "Custom Part Pricing & How Quotes Work | True Part Fabrication",
                           "How custom part manufacturing and replacement part prices are set: size, material, design work, quantity, and turnaround. Most business jobs run $75 to $800+. Modesto, CA.",
                           [B.crumbs_ld([("Home", ""), ("Pricing", "pricing/")])]), body)

# ---------------- SERVICES ----------------
SERVICES = [
 ("replacement-parts", "Replacement parts", "Discontinued, not done.",
  "Hard-to-find plastic parts for tools, shop vacuums, equipment, and household products, matched to the original or improved where it failed.",
  [("What we make", ["Dust collection adapters and hose fittings", "Vacuum nozzles, brushes, and attachments", "Clips, covers, caps, and battery doors", "Rollers, wheels, and glides", "Handle end caps and trim pieces"]),
   ("How it works", ["Send the broken part, or photos with a ruler and the model number", "We measure it and model it in CAD", "You approve the material, price, and turnaround in writing", "We print, check the fit, and deliver or ship"]),
   ("Good to know", ["Our parts are compatible aftermarket parts, not genuine brand parts", "We fix the weak spot that made the original fail where we can", "Not for safety-critical, pressurized, or electrical parts"])],
  [("Browse 196 compatible parts", "parts/"), ("Hose size finder", "tools/hose-size-finder/"), ("Clips and covers", "glossary/clips-and-covers/"), ("Rollers and wheels", "glossary/roller/")]),
 ("custom-fabrication", "Custom fabrication", "Built to your drawing.",
  "Mounts, brackets, jigs, fixtures, organizers, prototypes, and specialty components, modeled in CAD from your sketch, sample, or measurements.",
  [("What we make", ["Brackets and mounts for sensors, scanners, and tools", "Jigs and fixtures for repeat cuts, drilling, and assembly", "Organizers, trays, and holders shaped to your items", "Prototypes to test fit and function before production"]),
   ("What to send", ["A sketch, drawing, or CAD file (STL, STEP)", "Key measurements, or a sample part", "Where it will be used: indoors, outdoors, heat, cold, chemicals", "How many you need"]),
   ("Good to know", ["We'll recommend a material for your conditions", "We keep your model on file for reorders", "No load-bearing parts where a failure could hurt someone"])],
  [("Brackets", "glossary/bracket/"), ("Jigs", "glossary/jig/"), ("Fixtures", "glossary/fixture/"), ("Prototypes", "glossary/prototyping/"), ("Organizers", "glossary/organizer/"), ("Material picker", "tools/material-picker/")]),
 ("electronics-enclosures", "Electronics and enclosures", "Housings for what's next.",
  "Practical low-voltage devices, circuit-board products, and custom enclosures, each subject to appropriate testing and compliance.",
  [("What we make", ["Enclosures sized to a specific circuit board or device", "Sensor housings and mounting cases", "Prototype product housings", "Cable strain reliefs, lids, and panel parts"]),
   ("What to send", ["Board or device dimensions", "Where each connector, button, display, or vent goes", "Indoor or outdoor use, and the temperature range", "Quantity"]),
   ("Good to know", ["ASA for outdoor and sunny spots", "Low-voltage electronics only", "No mains-voltage housings or parts that must meet an electrical safety code"])],
  [("Enclosures", "glossary/enclosure/"), ("ASA", "glossary/asa/"), ("Prototypes", "glossary/prototyping/"), ("Heat limits", "glossary/heat-deflection-temperature/")]),
 ("small-batch-manufacturing", "Small-batch runs", "Five or five hundred.",
  "Repeat production without molds or large minimums. We keep your part's model on file, so the next run matches the first.",
  [("Good for", ["Parts you need in the tens or hundreds, not thousands", "Products still changing, where a mold would lock you in", "Spare parts kept on hand for a line or fleet", "Bridge production while a mold is being made"]),
   ("How it works", ["We model the part once, or use your file", "A first article is checked against your fit dimensions", "The run is printed and checked", "Reorder any time by part ID"]),
   ("Good to know", ["No tooling cost and no 1,000-unit minimum", "Price per part drops with quantity", "Repeat orders match the first run"])],
  [("Small-batch manufacturing", "glossary/small-batch-manufacturing/"), ("Pricing", "pricing/"), ("Reorder a part", "reorder/"), ("For business", "industries/industrial-shops/")]),
]

def services_index(c):
    cards = "".join(f'<a class="card" href="{c.link("services/" + s + "/")}"><div class="k">{esc(n)}</div><h3>{esc(h)}</h3><p>{esc(p)}</p><span class="svc-more">Learn more →</span></a>' for s, n, h, p, *_ in SERVICES)
    body = f"""<main id="main">
{hero(c, [('Home',''),('Services','services/')], 'Services', 'Four ways we solve the part: replacement parts, custom fabrication, electronics and enclosures, and small-batch runs. Every job is modeled, printed, and checked in our Modesto shop.')}
<div class="wrap" style="padding-block:48px 90px"><div class="cards2">{cards}</div></div>
{cta(c)}
</main>"""
    return B.doc(c, B.head(c, "Custom Manufacturing Services in Modesto, CA | True Part Fabrication",
                           "Replacement parts, custom fabrication, electronics enclosures, and small-batch manufacturing, made in Modesto for the Central Valley.",
                           [B.crumbs_ld([("Home", ""), ("Services", "services/")])]), body)

def service_page(c, svc):
    slug, name, h, lead, blocks, links = svc
    cards = "".join(f'<div class="card"><h3>{esc(t)}</h3><ul>' + "".join(f"<li>{esc(x)}</li>" for x in items) + "</ul></div>" for t, items in blocks)
    rel = "".join(f'<a href="{c.link(p)}">{esc(t)}</a>' for t, p in links)
    others = "".join(f'<a class="card" href="{c.link("services/" + s + "/")}"><div class="k">{esc(n)}</div><h3>{esc(hh)}</h3></a>' for s, n, hh, *_ in SERVICES if s != slug)
    path = "services/" + slug + "/"
    body = f"""<main id="main">
{hero(c, [('Home',''),('Services','services/'),(name, path)], f'{esc(name)}: <em class="s" style="font-family:var(--f-serif)">{esc(h)}</em>', esc(lead) + ' Free reprint if it doesn\'t fit.', f'<div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:26px"><a class="btn" href="{c.link("", "quote")}">Request a quote <span class="ar">→</span></a><a class="btn ghost" href="{c.link("pricing/")}">How pricing works</a></div>')}
<div class="wrap">
<section class="sec"><div class="cards3">{cards}</div></section>
<section class="sec"><div class="head" style="margin-bottom:18px"><div class="label">Related</div></div><div class="terms-strip">{rel}</div></section>
<section class="sec"><div class="head" style="margin-bottom:18px"><div class="label">Other services</div></div><div class="cards3">{others}</div></section>
</div>
{cta(c)}
</main>"""
    sld = {"@context": "https://schema.org", "@type": "Service", "name": name, "description": lead, "serviceType": name,
           "provider": {"@id": B.BASE + "/#business"}, "areaServed": B.ORG["areaServed"], "url": B.BASE + "/" + path}
    return B.doc(c, B.head(c, f"{name} in Modesto, CA | True Part Fabrication", lead + " Serving Modesto, Turlock, Stockton, and the Central Valley.",
                           [sld, B.crumbs_ld([("Home", ""), ("Services", "services/"), (name, path)])]), body)

# ---------------- REORDER ----------------
def reorder(c):
    body = f"""<main id="main">
{hero(c, [('Home',''),('Reorder','reorder/')], 'Reorder a part', 'Already ordered from us? Skip the full quote form. Give us your part ID, or the part number and description from your last invoice, and the quantity. We keep every model on file, so your reorder matches the first run.')}
<div class="wrap" style="padding-block:48px 90px">
<form class="xform" data-mail data-to="{QUOTE_TO}" data-title="Reorder request" novalidate>
  <label for="r-id">Part ID or part number<input id="r-id" data-l="Part ID" required placeholder="From your invoice or quote"></label>
  <label for="r-qty">Quantity<input id="r-qty" data-l="Quantity" inputmode="numeric" required placeholder="10"></label>
  <label for="r-name">Your name<input id="r-name" data-l="Name" autocomplete="name" required></label>
  <label for="r-co">Company<input id="r-co" data-l="Company" autocomplete="organization"></label>
  <label for="r-contact">Phone or email<input id="r-contact" data-l="Contact" required></label>
  <label for="r-when">Needed by<input id="r-when" data-l="Needed by" placeholder="Date, or 'no rush'"></label>
  <label class="full" for="r-notes">Changes from last time (optional)<textarea id="r-notes" data-l="Changes" placeholder="Different color or material, a fix to the fit, a new delivery address"></textarea></label>
  <p class="xerr" role="alert" hidden>Fill in the part ID, quantity, your name, and how to reach you.</p>
  <div class="full" style="display:flex;gap:14px;align-items:center;flex-wrap:wrap"><button class="btn" type="submit">Open in my email <span class="ar">→</span></button><span role="status" style="color:var(--muted);font-size:.92rem"></span></div>
</form>
<p style="margin-top:26px;color:var(--muted);max-width:62ch">Reorders are priced the same as your last order unless the quantity, material, or turnaround changes; we'll confirm before printing. Ordering for the first time? Use the <a href="{c.link('', 'quote')}" style="color:var(--ink)">quote form</a>.</p>
</div>
</main>"""
    return B.doc(c, B.head(c, "Reorder a Part | True Part Fabrication", "Reorder a part by part ID. Your model is on file, so the reorder matches the first run.",
                           [B.crumbs_ld([("Home", ""), ("Reorder", "reorder/")])]), body)

# ---------------- PROJECTS ----------------
def projects(c):
    body = f"""<main id="main">
{hero(c, [('Home',''),('Projects','projects/')], 'Projects', 'Real jobs from our shop, posted with the customer\'s permission. Our first projects go up after we open on January 1, 2027.')}
<div class="wrap" style="padding-block:48px 90px">
<div class="head"><div class="label">What each project will show</div></div>
<div class="cards3">
<div class="card"><h3>The problem</h3><p>What broke or what was missing, and what the customer was facing: a backordered part, a 500-pack minimum, or no part at all.</p></div>
<div class="card"><h3>The part</h3><p>Before and after photos, the material we chose and why, and anything we changed to fix the original's weak spot.</p></div>
<div class="card"><h3>The result</h3><p>Turnaround, quantity, and how the part held up in use.</p></div>
</div>
<div style="margin-top:44px">{notify_block(c, idp="n2")}</div>
<p style="margin-top:28px;color:var(--muted)">Until then, see the kinds of parts we make in the <a href="{c.link('parts/')}" style="color:var(--ink)">parts catalog</a> and our <a href="{c.link('services/')}" style="color:var(--ink)">services</a>.</p>
</div>
</main>"""
    return B.doc(c, B.head(c, "Projects | True Part Fabrication", "Real custom manufacturing and replacement part jobs from True Part Fabrication in Modesto, CA. First projects posted after we open January 1, 2027.",
                           [B.crumbs_ld([("Home", ""), ("Projects", "projects/")])]), body)

# ---------------- SEARCH ----------------
def search_index(c):
    from glossary import TERMS
    import tools as T
    idx = []
    def add(t, k, u, d, x=""): idx.append({"t": t, "k": k, "u": c.link(u), "d": d, "x": x})
    for s, n, h, p, *_ in SERVICES: add(n, "Service", "services/" + s + "/", p)
    for t, u, d in [("How pricing works", "pricing/", "What sets the price of a part, typical jobs, and ways to lower the cost."),
                    ("Reorder a part", "reorder/", "Reorder by part ID."), ("Frequently asked questions", "faq/", "Quotes, pricing, turnaround, materials, fit guarantee."),
                    ("Hose and dust port size finder", "tools/hose-size-finder/", "Look up hose, wand, and dust port sizes for vacs, collectors, and tools."),
                    ("Adapter builder", "tools/adapter-builder/", "Build a custom adapter between any two hose or dust port sizes."),
                    ("Request list", "request-list/", "Send several parts in one quote request."),
                    ("Material picker", "tools/material-picker/", "Five questions to the right material: PLA, PETG, ASA, TPU, nylon."),
                    ("How to measure a part", "guides/how-to-measure-a-part/", "Photograph and measure a broken part for an accurate quote."),
                    ("Terms of Service", "terms/", "Quotes, orders, aftermarket parts, fit guarantee."), ("Privacy", "privacy/", "How we handle your information."),
                    ("Projects", "projects/", "Real jobs from our shop."), ("Español", "es/", "Página en español: piezas de repuesto e impresión 3D.")]:
        add(t, "Page", u, d)
    for slug, nm, desc, *_ in T.INDS: add(nm, "Industry", "industries/" + slug + "/", desc)
    for b, (slug, cat, intro) in T.BRANDS.items(): add(b + " parts", "Brand", "brands/" + slug + "/", intro)
    for t in TERMS: add(t["term"], "Glossary", "glossary/" + t["slug"] + "/", t["short"])
    for it in B.CAT["items"]:
        add(it["n"], it["b"] + " part", "parts/" + it["slug"] + "/", B.rp(it) + (". Fits " + it["f"] if it["f"] else ""), it["oem"] + " " + it.get("for", ""))
    return idx

SEARCH_JS = r"""<script>
(function(){
  var IDX=window.TPF_IDX||[],q=document.getElementById('sq'),out=document.getElementById('sres'),st=document.getElementById('scount');
  function norm(s){return (s||'').toLowerCase().replace(/[^a-z0-9\/\.\- ]+/g,' ')}
  IDX.forEach(function(r){r._t=norm(r.t);r._a=norm(r.t+' '+r.k+' '+r.d+' '+r.x)});
  function run(){
    var v=norm(q.value).trim();out.innerHTML='';
    if(!v){st.textContent='';return}
    var words=v.split(/\s+/),res=[];
    IDX.forEach(function(r){var ok=words.every(function(w){return r._a.indexOf(w)>-1});if(!ok)return;var s=0;words.forEach(function(w){if(r._t.indexOf(w)>-1)s+=3});if(r.k!=='Glossary'&&r.k.indexOf('part')<0)s+=1;res.push([s,r])});
    res.sort(function(a,b){return b[0]-a[0]});
    st.textContent=res.length+(res.length===1?' result':' results');
    res.slice(0,60).forEach(function(x){var r=x[1],li=document.createElement('li'),a=document.createElement('a');a.href=r.u;
      var k=document.createElement('span');k.textContent=r.k;var h=document.createElement('h3');h.textContent=r.t;var p=document.createElement('p');p.textContent=r.d;
      a.appendChild(k);a.appendChild(h);a.appendChild(p);li.appendChild(a);out.appendChild(li)});
    if(!res.length){var li=document.createElement('li');li.innerHTML='<p style="padding:18px 0;color:var(--muted)">No matches. Try a part number, a brand, or a word like "adapter". Or <a href="'+document.getElementById('sq-quote').href+'" style="color:var(--ink)">describe your part in a quote request</a>.</p>';out.appendChild(li)}
  }
  var p=new URLSearchParams(location.search).get('q');if(p){q.value=p}
  q.addEventListener('input',function(){run();try{history.replaceState(null,'',q.value?('?q='+encodeURIComponent(q.value)):location.pathname)}catch(e){}});
  document.getElementById('sform').addEventListener('submit',function(e){e.preventDefault();run()});
  run();
})();
</script>"""

def search(c):
    idx = json.dumps(search_index(c), ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    body = f"""<main id="main">
{hero(c, [('Home',''),('Search','search/')], 'Search the site', 'Parts by name, brand, or part number, plus services, tools, guides, and glossary terms.')}
<div class="wrap" style="padding-block:40px 90px">
  <form class="sbox" id="sform" role="search"><label for="sq" style="position:absolute;left:-9999px">Search</label><input id="sq" type="search" placeholder="Try 49-90-2018, Makita, or bracket" autocomplete="off" autofocus><button class="btn" type="submit">Search</button></form>
  <p id="scount" role="status" style="color:var(--faint);margin-top:14px;font-size:.9rem"></p>
  <ul class="sres" id="sres"></ul>
  <a id="sq-quote" href="{c.link('', 'quote')}" hidden>quote</a>
</div>
</main>
<script>window.TPF_IDX={idx}</script>
{SEARCH_JS}"""
    return B.doc(c, B.head(c, "Search | True Part Fabrication", "Search True Part Fabrication's parts, services, tools, and glossary.",
                           [B.crumbs_ld([("Home", ""), ("Search", "search/")])]), body)

# ---------------- SPANISH CATALOG ----------------
def es_catalog(c):
    import es as E
    items = B.CAT["items"]; brands = []
    for x in items:
        if x["b"] not in brands: brands.append(x["b"])
    chips = '<button class="chip" type="button" data-b="All" aria-pressed="true">Todas<i>' + str(len(items)) + "</i></button>" + "".join(
        f'<button class="chip" type="button" data-b="{esc(b)}" aria-pressed="false">{esc(b)}<i>{sum(1 for x in items if x["b"] == b)}</i></button>' for b in brands)
    def rp(it): return ("Reemplaza " + it["b"] + " " + it["oem"]) if it["oem"] else ("Para " + it["b"] + " " + it.get("for", ""))
    rows = []
    for it in items:
        k = (it["b"] + " " + it["oem"] + " " + it.get("for", "") + " " + it["n"] + " " + it["f"]).lower()
        badge = "" if it["f"] else '<span class="fitbadge">Ajuste por confirmar</span>'
        ptxt = "Pieza compatible: " + it["n"] + "\n" + rp(it)
        rows.append(f"""<div class="row" data-b="{esc(it['b'])}" data-fit="{1 if it['f'] else 0}" data-k="{esc(k)}"><div class="b">{esc(it['b'])}</div><h3 class="n" style="font:600 1rem var(--f-body);text-transform:none;letter-spacing:0"><a href="{c.link('parts/' + it['slug'] + '/')}" hreflang="en" lang="en">{esc(it['n'])}</a>{badge}</h3><div class="o">{esc(rp(it))}</div><div class="f">{('Compatible con: <span lang="en">' + esc(it['f']) + '</span>') if it['f'] else 'Pídanos confirmar su modelo'}</div><a class="btn ghost" style="height:34px;padding:0 14px;font-size:.8rem" href="{c.link('es/', 'cotizar')}" data-part="{esc(ptxt)}">Solicitar</a></div>""")
    body = f"""<main id="main">
<div class="page-hero"><div class="wrap">
  {B.crumbs(c, [('Inicio', 'es/'), ('Catálogo de piezas', 'es/piezas/')])}
  <h1>Catálogo de piezas compatibles</h1>
  <p class="lead">{len(items)} piezas de reemplazo hechas a pedido para herramientas, aspiradoras y electrodomésticos de {', '.join(brands[:-1])} y {brands[-1]}. Busque por número de pieza o modelo y pida una cotización. Los nombres de las piezas están en inglés.</p>
</div></div>
<section style="padding-block:44px 100px"><div class="wrap">
  <div class="tools">
    <div class="search"><svg viewBox="0 0 16 16" fill="none" stroke="var(--muted)" stroke-width="1.6" aria-hidden="true"><circle cx="7" cy="7" r="5"/><path d="M11 11l3.5 3.5"/></svg><label for="cat-q" style="position:absolute;left:-9999px">Buscar piezas</label><input id="cat-q" type="search" placeholder="Número de pieza, modelo o nombre"></div>
    <label class="toggle" for="fit-only"><input type="checkbox" id="fit-only" checked> Solo ajuste confirmado</label>
    <span id="cat-count" style="color:var(--faint);font-size:.88rem;margin-left:auto"></span>
  </div>
  <div class="chips" id="cat-chips" role="group" aria-label="Filtrar por marca" style="margin-bottom:22px">{chips}</div>
  <div class="list" id="plist" data-one="pieza" data-many="piezas" data-more="Ver más">
{chr(10).join(rows)}
  </div>
  <p class="empty" id="cat-empty" hidden>Ninguna pieza coincide. Desmarque "Solo ajuste confirmado" o describa su pieza en el <a href="{c.link('es/', 'cotizar')}" style="color:var(--ink)">formulario de cotización</a>.</p>
  <div class="more"><button class="btn ghost" type="button" id="cat-more" hidden>Ver más</button></div>
  <p class="legal">Estas son piezas compatibles de reemplazo hechas por True Part Fabrication, no piezas originales del fabricante. Los nombres de marca y números de pieza pertenecen a sus dueños y se usan solo para indicar compatibilidad. True Part Fabrication no está afiliada ni respaldada por ninguna de las marcas.</p>
</div></section>
</main>"""
    return E.doc_es(c, B.head(c, "Catálogo de piezas de repuesto compatibles | True Part Fabrication",
                              f"{len(items)} piezas de repuesto compatibles hechas a pedido: adaptadores, boquillas, cepillos y clips para DeWalt, Milwaukee, Ryobi, Makita y más. Impresas en 3D en Modesto, CA.",
                              [B.crumbs_ld([("Inicio", "es/"), ("Catálogo de piezas", "es/piezas/")])]), body)

def pages():
    p = {"pricing/": pricing, "services/": services_index, "reorder/": reorder, "projects/": projects, "search/": search, "es/piezas/": es_catalog}
    for s in SERVICES:
        p["services/" + s[0] + "/"] = (lambda c, s=s: service_page(c, s))
    return p

# ================= functionality upgrades =================
EX_CSS += r"""
/* ---- request list ---- */
.list-pill{display:inline-flex;align-items:center;gap:8px;height:42px;padding:0 16px;border-radius:999px;border:1px solid var(--accent);color:var(--ink);text-decoration:none;font:600 .85rem var(--f-body)}
.list-pill b{display:inline-grid;place-items:center;min-width:22px;height:22px;border-radius:999px;background:var(--accent);color:#fff;font-size:.75rem;padding:0 6px}
.list-pill[hidden]{display:none!important}
.add-list{font:600 .8rem var(--f-body);height:34px;padding:0 14px;border-radius:999px;border:1px dashed var(--line);background:transparent;color:var(--ink);cursor:pointer;margin-left:8px;white-space:nowrap}
.add-list:hover{border-color:var(--accent)}
.add-list[aria-pressed="true"]{border-style:solid;border-color:var(--accent)}
.acts .add-list,.pp .add-list{height:46px;padding:0 20px;font-size:.92rem;margin-left:0}
.row .add-list{grid-column:auto}
.rl-items{list-style:none;margin:0;padding:0;border-top:1px solid var(--line)}
.rl-items li{display:grid;grid-template-columns:1fr 110px auto;gap:14px;align-items:center;padding:16px 0;border-bottom:1px solid var(--line)}
.rl-items .t{white-space:pre-line;color:var(--ink)}
.rl-items input{font:400 1rem var(--f-body);color:var(--ink);background:var(--surface);border:1px solid var(--line);border-radius:6px;padding:10px 12px;width:100%}
.rl-items button{background:none;border:1px solid var(--line);color:var(--ink);border-radius:999px;height:36px;padding:0 14px;cursor:pointer;font:600 .8rem var(--f-body)}
.rl-items button:hover{border-color:var(--accent)}
@media (max-width:600px){.rl-items li{grid-template-columns:1fr auto}.rl-items .t{grid-column:1/-1}}
@media (max-width:900px){.list-pill{height:38px;padding:0 12px;font-size:0;gap:0}.list-pill b{font-size:.75rem}.list-pill::before{content:"List";font:600 .8rem var(--f-body);margin-right:6px}}
/* ---- to top ---- */
.to-top{position:fixed;right:18px;bottom:18px;z-index:30;width:46px;height:46px;border-radius:50%;border:1px solid var(--line);background:var(--surface);color:var(--ink);cursor:pointer;display:grid;place-items:center;box-shadow:0 8px 24px -10px rgba(0,0,0,.5)}
.to-top[hidden]{display:none}
.to-top:hover{border-color:var(--accent)}
/* ---- adapter builder ---- */
.ab{display:grid;grid-template-columns:1fr 1fr;gap:18px;max-width:900px}
.ab fieldset{border:1px solid var(--line);border-radius:8px;padding:22px;margin:0;background:var(--surface);display:grid;gap:14px}
.ab legend{font:500 .72rem var(--f-mono);letter-spacing:.14em;text-transform:uppercase;color:var(--accent-hi);padding:0 6px}
.ab label{display:grid;gap:6px;font:500 .8rem var(--f-mono);letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.ab select,.ab input{font:400 1rem var(--f-body);color:var(--ink);background:var(--bg);border:1px solid var(--line);border-radius:6px;padding:11px 12px;text-transform:none;letter-spacing:0}
.ab .full{grid-column:1/-1}
.ab-out{max-width:900px;margin-top:22px}
.ab-out pre{white-space:pre-wrap;font:500 .95rem var(--f-mono);color:var(--ink);margin:10px 0 0}
@media (max-width:700px){.ab{grid-template-columns:1fr}}
.draft-note{font-size:.85rem;color:var(--faint);margin-top:6px}
.draft-note button{background:none;border:0;color:var(--ink);text-decoration:underline;cursor:pointer;font:inherit;padding:0}
"""

LIST_JS = r"""
  // ---- request list ----
  var LK='tpf-list',ES=document.documentElement.lang==='es';
  function getL(){try{return JSON.parse(localStorage.getItem(LK)||'[]')}catch(e){return []}}
  function setL(a){try{localStorage.setItem(LK,JSON.stringify(a))}catch(e){}updPill();document.dispatchEvent(new CustomEvent('tpf-list'))}
  function inL(t){return getL().some(function(x){return x.t===t})}
  function updPill(){var p=document.getElementById('list-pill'),n=getL().length;if(!p)return;p.hidden=n===0;var b=document.getElementById('list-n');if(b)b.textContent=n;p.setAttribute('aria-label',(ES?'Lista de solicitud: ':'Request list: ')+n+(ES?' piezas':n===1?' part':' parts'))}
  function lbl(on){return on?(ES?'✓ En la lista':'✓ On list'):(ES?'+ Lista':'+ Add to list')}
  document.querySelectorAll('a[data-part]').forEach(function(a){
    if(a.closest('.pc'))return;
    var b=document.createElement('button');b.type='button';b.className='add-list';var t=a.getAttribute('data-part');b.setAttribute('data-add',t);
    var on=inL(t);b.textContent=lbl(on);b.setAttribute('aria-pressed',on);b.setAttribute('aria-label',(on?(ES?'Quitar de la lista: ':'Remove from request list: '):(ES?'Añadir a la lista: ':'Add to request list: '))+t.split('\n')[0].replace(/^[^:]*: /,''));
    a.insertAdjacentElement('afterend',b);
  });
  document.addEventListener('click',function(e){var b=e.target.closest('[data-add]');if(!b)return;var t=b.getAttribute('data-add'),L=getL(),i=L.findIndex(function(x){return x.t===t});
    if(i>-1)L.splice(i,1);else L.push({t:t,q:1});setL(L);
    document.querySelectorAll('[data-add]').forEach(function(x){var on=inL(x.getAttribute('data-add'));x.textContent=lbl(on);x.setAttribute('aria-pressed',on)});
    var st=document.getElementById('list-live');if(st)st.textContent=i>-1?(ES?'Quitado de la lista.':'Removed from your request list.'):(ES?'Añadido a la lista.':'Added to your request list.');});
  if(!document.getElementById('list-live')){var lv=document.createElement('div');lv.id='list-live';lv.setAttribute('role','status');lv.style.cssText='position:absolute;left:-9999px';document.body.appendChild(lv)}
  updPill();
  // ---- shortcuts: "/" to search, back to top ----
  document.addEventListener('keydown',function(e){if(e.key!=='/'||e.ctrlKey||e.metaKey||e.altKey)return;var tg=e.target;if(tg&&(tg.isContentEditable||/^(INPUT|TEXTAREA|SELECT)$/.test(tg.tagName)))return;
    var box=document.getElementById('sq')||document.getElementById('cat-q')||document.getElementById('hf-q');e.preventDefault();if(box){box.focus();box.select&&box.select()}else{var s=document.querySelector('a.icon-l.s');if(s)location.href=s.href}});
  var tt=document.createElement('button');tt.type='button';tt.className='to-top';tt.hidden=true;tt.setAttribute('aria-label',ES?'Volver arriba':'Back to top');tt.innerHTML='<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M12 19V5M5 12l7-7 7 7"/></svg>';
  document.body.appendChild(tt);tt.addEventListener('click',function(){scrollTo({top:0,behavior:'smooth'});var m=document.getElementById('main');if(m){m.setAttribute('tabindex','-1');m.focus({preventScroll:true})}});
  addEventListener('scroll',function(){tt.hidden=scrollY<1200},{passive:true});
"""

DRAFT_JS = r"""
  // ---- save form drafts on this device ----
  ['qf','qf-es','rl-form'].concat([].map.call(document.querySelectorAll('form.xform[id]'),function(f){return f.id})).forEach(function(id){
    var f=document.getElementById(id);if(!f)return;var key='tpf-draft-'+id,ES2=document.documentElement.lang==='es';
    var fields=[].filter.call(f.querySelectorAll('input,textarea,select'),function(x){return x.id&&x.type!=='checkbox'&&x.type!=='hidden'&&x.type!=='file'});
    try{var d=JSON.parse(localStorage.getItem(key)||'null');if(d&&Date.now()-d._t<14*864e5){fields.forEach(function(x){if(d[x.id]!=null&&!x.value)x.value=d[x.id]})}}catch(e){}
    function save(){var d={_t:Date.now()},any=false;fields.forEach(function(x){if(x.value){d[x.id]=x.value;any=true}});try{if(any)localStorage.setItem(key,JSON.stringify(d));else localStorage.removeItem(key)}catch(e){}}
    f.addEventListener('input',save);f.addEventListener('change',save);
    var note=document.createElement('p');note.className='draft-note full';note.style.gridColumn='1/-1';note.innerHTML=(ES2?'Lo que escribe se guarda en este dispositivo. ':'What you type is saved on this device until you send it. ')+'<button type="button">'+(ES2?'Borrar formulario':'Clear form')+'</button>';
    f.appendChild(note);note.querySelector('button').addEventListener('click',function(){fields.forEach(function(x){if(x.tagName!=='SELECT')x.value=''});try{localStorage.removeItem(key)}catch(e){}});
  });
"""

def request_list(c):
    body = f"""<main id="main">
{hero(c, [('Home',''),('Request list','request-list/')], 'Your request list', 'Collect several parts while you browse, then send them to us in one quote request. Set a quantity for each part. The list is saved on this device.')}
<div class="wrap" style="padding-block:40px 90px">
  <ul class="rl-items" id="rl-items"></ul>
  <p id="rl-empty" style="color:var(--muted);margin-top:18px" hidden>Your list is empty. Use <b>+ Add to list</b> on any part in the <a href="{c.link('parts/')}" style="color:var(--ink)">parts catalog</a>, a brand page, or a part page.</p>
  <div id="rl-send" hidden>
    <h2 style="font-size:1.3rem;margin:44px 0 18px">Send the list</h2>
    <form class="xform" id="rl-form" novalidate>
      <label for="rl-name">Your name<input id="rl-name" autocomplete="name" required></label>
      <label for="rl-co">Company<input id="rl-co" autocomplete="organization"></label>
      <label for="rl-contact">Phone or email<input id="rl-contact" required></label>
      <label for="rl-when">Needed by<input id="rl-when" placeholder="Date, or 'no rush'"></label>
      <label class="full" for="rl-notes">Notes (optional)<textarea id="rl-notes" placeholder="Equipment model numbers, colors, delivery address"></textarea></label>
      <label class="agree full" for="rl-terms"><input type="checkbox" id="rl-terms"> <span>I've read and agree to the <a href="{c.link('terms/')}">Terms of Service</a>.</span></label>
      <p class="xerr" id="rl-err" role="alert" hidden></p>
      <div class="full" style="display:flex;gap:12px;align-items:center;flex-wrap:wrap"><button class="btn" type="submit">Open in my email <span class="ar">→</span></button><button class="btn ghost" type="button" id="rl-copy">Copy request</button><button class="btn ghost" type="button" id="rl-clear">Clear list</button><span id="rl-st" role="status" style="color:var(--muted);font-size:.92rem"></span></div>
    </form>
  </div>
</div>
</main>
<script>
(function(){{
  var LK='tpf-list',ul=document.getElementById('rl-items'),em=document.getElementById('rl-empty'),sd=document.getElementById('rl-send'),st=document.getElementById('rl-st');
  function get(){{try{{return JSON.parse(localStorage.getItem(LK)||'[]')}}catch(e){{return []}}}}
  function set(a){{try{{localStorage.setItem(LK,JSON.stringify(a))}}catch(e){{}}var p=document.getElementById('list-pill'),b=document.getElementById('list-n');if(p){{p.hidden=a.length===0}}if(b)b.textContent=a.length}}
  function draw(){{var L=get();ul.textContent='';em.hidden=L.length>0;sd.hidden=L.length===0;
    L.forEach(function(x,i){{var li=document.createElement('li'),t=document.createElement('div');t.className='t';t.textContent=x.t.replace(/^Compatible part: |^Pieza compatible: /,'');
      var lab=document.createElement('label');lab.style.cssText='display:grid;gap:4px;font:500 .7rem var(--f-mono);letter-spacing:.1em;text-transform:uppercase;color:var(--faint)';lab.textContent='Qty';var q=document.createElement('input');q.type='number';q.min='1';q.value=x.q||1;q.setAttribute('aria-label','Quantity for '+t.textContent.split('\\n')[0]);lab.appendChild(q);
      q.addEventListener('change',function(){{var A=get();if(A[i]){{A[i].q=Math.max(1,parseInt(q.value,10)||1);set(A)}}}});
      var rm=document.createElement('button');rm.type='button';rm.textContent='Remove';rm.setAttribute('aria-label','Remove '+t.textContent.split('\\n')[0]);rm.addEventListener('click',function(){{var A=get();A.splice(i,1);set(A);draw();st.textContent='Removed.'}});
      li.appendChild(t);li.appendChild(lab);li.appendChild(rm);ul.appendChild(li)}})}}
  function v(id){{return document.getElementById(id).value.trim()}}
  function text(){{var L=get(),out=['Quote request (request list) — True Part Fabrication','','Name: '+v('rl-name')];if(v('rl-co'))out.push('Company: '+v('rl-co'));out.push('Contact: '+v('rl-contact'));if(v('rl-when'))out.push('Needed by: '+v('rl-when'));out.push('','Parts:');
    L.forEach(function(x,i){{out.push((i+1)+'. Qty '+(x.q||1)+' — '+x.t.replace(/^Compatible part: |^Pieza compatible: /,'').replace(/\\n/g,' — '))}});if(v('rl-notes'))out.push('','Notes:',v('rl-notes'));out.push('','Agreed to the Terms of Service: yes','(Please attach photos of the parts or equipment if you have them)');return out.join('\\n')}}
  function check(){{var er=document.getElementById('rl-err');if(!v('rl-name')||!v('rl-contact')){{er.textContent='Add your name and a way to reach you.';er.hidden=false;return false}}if(!document.getElementById('rl-terms').checked){{er.textContent='Please read and agree to the Terms of Service before sending.';er.hidden=false;return false}}er.hidden=true;return true}}
  document.getElementById('rl-form').addEventListener('submit',function(e){{e.preventDefault();if(!check())return;location.href='mailto:{QUOTE_TO}?subject='+encodeURIComponent('Quote request: '+get().length+' parts')+'&body='+encodeURIComponent(text());st.textContent='Your email app opened with the request. Send it to finish.'}});
  document.getElementById('rl-copy').addEventListener('click',function(){{if(!check())return;var t=text();try{{navigator.clipboard.writeText(t).then(function(){{st.textContent='Copied. Paste it into an email to us.'}},function(){{st.textContent='Copy did not work in this browser.'}})}}catch(e){{st.textContent='Copy did not work in this browser.'}}}});
  document.getElementById('rl-clear').addEventListener('click',function(){{set([]);draw();st.textContent='List cleared.'}});
  draw();
}})();
</script>"""
    return B.doc(c, B.head(c, "Request List | True Part Fabrication", "Collect several compatible parts and send them in one quote request.", [B.crumbs_ld([("Home", ""), ("Request list", "request-list/")])]), body)

AB_SIZES = ["22 mm", "24 mm", "15/16 in", "1 in", "1-1/4 in", "32 mm", "35 mm", "36 mm", "1-3/8 in", "1-1/2 in", "38 mm", "1-3/4 in", "1-7/8 in", "2 in", "2-1/4 in", "2-1/2 in", "4 in"]
def adapter_builder(c):
    opts = "".join(f"<option>{s}</option>" for s in AB_SIZES) + "<option value=\"other\">Other: I'll send measurements</option>"
    kinds = "<option>Vacuum hose end (cuff)</option><option>Power tool dust port</option><option>Dust collector port or fitting</option><option>Vacuum wand or accessory</option><option>Other</option>"
    def side(p, title, dsize):
        o = opts.replace(f"<option>{dsize}</option>", f"<option selected>{dsize}</option>")
        return f"""<fieldset><legend>{title}</legend>
<label for="{p}-kind">What it connects to<select id="{p}-kind">{kinds}</select></label>
<label for="{p}-size">Size<select id="{p}-size">{o}</select></label>
<label for="{p}-fit">Fit on that end<select id="{p}-fit"><option>Slips over it (fits outside)</option><option>Slides into it (fits inside)</option><option>Not sure</option></select></label>
<label for="{p}-model">Brand and model (optional)<input id="{p}-model" placeholder="e.g. Makita XCV11, DeWalt DWE6423"></label>
</fieldset>"""
    ab_lead = "Pick the two things you want to connect, and we'll make an adapter sized to both. Not sure of a size? Look it up in the <a href=\"" + c.link('tools/hose-size-finder/') + "\" style=\"color:var(--ink)\">hose size finder</a> or use the <a href=\"" + c.link('guides/how-to-measure-a-part/') + "\" style=\"color:var(--ink)\">measuring guide</a>."
    body = f"""<main id="main">
{hero(c, [('Home',''),('Resources','resources/'),('Adapter builder','tools/adapter-builder/')], 'Adapter builder', ab_lead)}
<div class="wrap" style="padding-block:40px 90px">
  <form class="ab" id="ab" novalidate>
    {side('a', 'End A', '1-1/4 in')}
    {side('b', 'End B', '2-1/2 in')}
    <fieldset class="full"><legend>Options</legend>
      <label for="ab-mat">Material<select id="ab-mat"><option value="auto">Recommend for me</option><option>PETG (rigid, general use)</option><option>TPU (flexible, grips like rubber)</option><option>ASA (outdoors, heat and sun)</option></select></label>
      <label for="ab-qty">Quantity<input id="ab-qty" type="number" min="1" value="1"></label>
    </fieldset>
  </form>
  <div class="callout ab-out" aria-live="polite"><div class="k">Your adapter</div><pre id="ab-sum"></pre>
    <div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:18px"><a class="btn" id="ab-req" href="{c.link('', 'quote')}" data-part="">Request this adapter <span class="ar">→</span></a></div>
  </div>
  <p class="legal" style="margin-top:28px">Sizes are nominal. We confirm the exact fit from your model numbers or measurements before printing, and reprint free if it doesn't fit. Adapters are for dust collection and vacuum use only, not for pressurized air or water.</p>
</div>
</main>
<script>
(function(){{
  var f=document.getElementById('ab'),sum=document.getElementById('ab-sum'),req=document.getElementById('ab-req');
  function v(id){{var e=document.getElementById(id);return e?e.value.trim():''}}
  function end(p){{var s=v(p+'-size');s=s==='other'?'size to be measured':s;var m=v(p+'-model');return v(p+'-kind')+', '+s+', '+v(p+'-fit').toLowerCase().replace(/ \\(.*\\)/,'')+(m?' ('+m+')':'')}}
  function mat(){{var m=v('ab-mat');if(m!=='auto')return m.split(' (')[0];var k=v('a-kind')+v('b-kind');return /tool dust port/i.test(k)?'TPU on the tool end, PETG body (recommended)':'PETG (recommended)'}}
  function go(){{var t='Custom adapter\\nEnd A: '+end('a')+'\\nEnd B: '+end('b')+'\\nMaterial: '+mat()+'\\nQuantity: '+(parseInt(v('ab-qty'),10)||1);
    sum.textContent=t;req.setAttribute('data-part',t);var ad=document.querySelector('#ab-req + .add-list');if(ad){{ad.setAttribute('data-add',t)}}}}
  f.addEventListener('input',go);f.addEventListener('change',go);
  try{{var P=new URLSearchParams(location.search);['a','b'].forEach(function(p){{var s=P.get(p);if(s){{var sel=document.getElementById(p+'-size');[].forEach.call(sel.options,function(o){{if(o.value===s||o.text===s)sel.value=o.value}})}}}})}}catch(e){{}}
  go();
}})();
</script>"""
    howto = {"@context": "https://schema.org", "@type": "WebApplication", "name": "Vacuum and dust collection adapter builder", "applicationCategory": "UtilitiesApplication", "operatingSystem": "Any",
             "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}, "url": B.BASE + "/tools/adapter-builder/"}
    return B.doc(c, B.head(c, "Vacuum Hose & Dust Port Adapter Builder | True Part Fabrication",
                           "Build a custom adapter between any two vacuum hose, dust port, or dust collector sizes: 1-1/4, 1-7/8, 2-1/2, 4 in., 35 mm, and more. Made to order in Modesto, CA.",
                           [howto, B.crumbs_ld([("Home", ""), ("Resources", "resources/"), ("Adapter builder", "tools/adapter-builder/")])]), body)

_old_pages = pages
def pages():
    p = _old_pages()
    p["request-list/"] = request_list
    p["tools/adapter-builder/"] = adapter_builder
    return p
EX_CSS += r"""
nav.main .btn{white-space:nowrap}
@media (max-width:480px){nav.main{gap:8px}.list-pill{padding:0 10px;height:38px}nav.main .btn{padding:0 12px;font-size:.78rem;height:38px}.menu-btn{width:38px;height:38px}}
@media (max-width:360px){.list-pill::before{content:""!important;margin:0!important}}
"""
