"""Online ordering: cart page, prices.json, order pages, checkout config.

Everything here is switched off until CHECKOUT["enabled"] is True and
CHECKOUT["endpoint"] points at the checkout server (see _build/checkout-server/README.md).
Only parts with a price AND a confirmed fit can be bought online; everything else
stays on the quote request.
"""
import json, html
import build as B
esc = html.escape

# ---- switches (the only things to change when checkout goes live) ----
CHECKOUT = {
    "enabled": False,          # True once Stripe keys are in Render and prices are set
    "endpoint": "",            # e.g. "https://truepart-checkout.onrender.com" (no trailing slash)
    "opens": "January 1, 2027",
}
# Shipping placeholder tiers, in cents. Matches the eBay rates; confirm before launch.
SHIP = [
    {"id": "small", "label": "Small part", "cents": 400},
    {"id": "medium", "label": "Medium part", "cents": 475},
    {"id": "large", "label": "Large part", "cents": 550},
]
SHIP_BY_KIND = {"clip": "small", "brush": "small", "adapter": "medium", "nozzle": "medium", "roller": "medium", "separator": "large"}
PICKUP = {"label": "Local pickup in Modesto", "cents": 0}
MAX_QTY = 25

def key(it):
    """What the cart stores for a part, minus the 'Compatible part: ' prefix."""
    return it["n"] + "\n" + B.rp(it)

def buyable(it):
    return bool(it.get("price")) and bool(it.get("f"))

def prices_data(items):
    out = {}
    for it in items:
        if not buyable(it):
            continue
        out[key(it)] = {"s": it["slug"], "n": it["n"], "p": int(round(float(it["price"]) * 100)),
                        "sh": SHIP_BY_KIND.get(it["i"], "medium")}
    return {"enabled": CHECKOUT["enabled"] and bool(CHECKOUT["endpoint"]), "endpoint": CHECKOUT["endpoint"],
            "opens": CHECKOUT["opens"], "ship": SHIP, "pickup": PICKUP, "maxQty": MAX_QTY, "items": out}

def server_prices(items):
    """Price list for the checkout server, keyed by slug (the server never trusts browser prices)."""
    return {"ship": SHIP, "pickup": PICKUP, "maxQty": MAX_QTY,
            "items": {it["slug"]: {"name": it["n"], "ref": B.rp(it), "cents": int(round(float(it["price"]) * 100)),
                                   "ship": SHIP_BY_KIND.get(it["i"], "medium")}
                      for it in items if buyable(it)}}

SHOP_CSS = r"""
.buy{margin:30px 0 0;padding:22px;border:1px solid var(--line);border-radius:14px;background:var(--panel,rgba(255,255,255,.03))}
.buy h2{font-size:1.2rem;margin:0 0 6px}
.buy .sum{display:grid;grid-template-columns:1fr auto;gap:6px 18px;margin:16px 0;max-width:460px}
.buy .sum dt{color:var(--muted)}.buy .sum dd{margin:0;text-align:right;font-variant-numeric:tabular-nums}
.buy .sum .tot{font-weight:700;color:var(--ink)}
.buy .note{color:var(--muted);font-size:.9rem;margin:8px 0 0}
.buy button[disabled]{opacity:.55;cursor:not-allowed}
.rl-items .pr{font:600 .95rem var(--f-body);color:var(--ink);white-space:nowrap}
.rl-items .pr small{display:block;font:400 .75rem var(--f-body);color:var(--faint)}
.rl-items .needq{font:500 .72rem var(--f-mono);letter-spacing:.08em;text-transform:uppercase;color:var(--faint)}
.row .pr,.feat .pr{font:600 .9rem var(--f-body);color:var(--ink);white-space:nowrap}
.order-box{max-width:640px}
@media (max-width:900px){html[lang="es"] .list-pill::before{content:"Carrito"}}
.rl-items li{grid-template-columns:1fr auto 96px auto}
.rl-items .pr{text-align:right;min-width:84px}
@media (max-width:600px){.rl-items li{grid-template-columns:1fr 96px auto}.rl-items .t{grid-column:1/-1}.rl-items .pr{grid-column:1/-1;text-align:left}}
@media print{.buy button,.buy .agree{display:none!important}}
"""

CART_JS = r"""
(function(){
  var LK='tpf-list',ul=document.getElementById('rl-items'),em=document.getElementById('rl-empty'),sd=document.getElementById('rl-send'),st=document.getElementById('rl-st'),buy=document.getElementById('buy'),P=null;
  function get(){try{return JSON.parse(localStorage.getItem(LK)||'[]')}catch(e){return []}}
  function set(a){try{localStorage.setItem(LK,JSON.stringify(a))}catch(e){}var p=document.getElementById('list-pill'),b=document.getElementById('list-n');if(p){p.hidden=a.length===0}if(b)b.textContent=a.length}
  function clean(t){return t.replace(/^Compatible part: |^Pieza compatible: /,'')}
  function money(c){return '$'+(c/100).toFixed(2)}
  function priced(x){return P&&P.items[clean(x.t)]||null}
  function live(){return !!(P&&P.enabled)}
  function quoteItems(){return get().filter(function(x){return !live()||!priced(x)})}
  function draw(){var L=get();ul.textContent='';em.hidden=L.length>0;
    L.forEach(function(x,i){var li=document.createElement('li'),t=document.createElement('div');t.className='t';t.textContent=clean(x.t);
      var lab=document.createElement('label');lab.style.cssText='display:grid;gap:4px;font:500 .7rem var(--f-mono);letter-spacing:.1em;text-transform:uppercase;color:var(--faint)';lab.textContent='Qty';var q=document.createElement('input');q.type='number';q.min='1';q.max=String(P?P.maxQty:25);q.value=x.q||1;q.setAttribute('aria-label','Quantity for '+t.textContent.split('\n')[0]);lab.appendChild(q);
      q.addEventListener('change',function(){var A=get();if(A[i]){A[i].q=Math.min(P?P.maxQty:25,Math.max(1,parseInt(q.value,10)||1));q.value=A[i].q;set(A);sum();drawPrice(li,A[i])}});
      var rm=document.createElement('button');rm.type='button';rm.textContent='Remove';rm.setAttribute('aria-label','Remove '+t.textContent.split('\n')[0]);rm.addEventListener('click',function(){var A=get();A.splice(i,1);set(A);draw();st.textContent='Removed.'});
      var pr=document.createElement('div');pr.className='pr';
      li.appendChild(t);li.appendChild(pr);li.appendChild(lab);li.appendChild(rm);ul.appendChild(li);drawPrice(li,x)});
    sum()}
  function drawPrice(li,x){var pr=li.querySelector('.pr'),p=priced(x);if(!pr)return;if(p){pr.innerHTML='';pr.appendChild(document.createTextNode(money(p.p*(x.q||1))));var s=document.createElement('small');s.textContent=(x.q||1)>1?money(p.p)+' each':(live()?'Buy online':'Listed price');pr.appendChild(s)}else{pr.innerHTML='<span class="needq">Needs a quote</span>'}}
  function shipFor(L){var r={small:0,medium:1,large:2},m=-1;L.forEach(function(x){var p=priced(x);if(p&&r[p.sh]>m)m=r[p.sh]});return m<0?null:P.ship[m]}
  function sum(){var L=get(),B=L.filter(priced),Q=quoteItems().length;sd.hidden=Q===0;
    var qh=document.getElementById('rl-qh');if(qh)qh.textContent=live()&&B.length&&Q?(Q===1?'Request a quote for the other part':'Request a quote for the other '+Q+' parts'):(B.length?'Or send your cart as a quote request':'Send your cart as a quote request');
    if(!buy)return;buy.hidden=B.length===0;if(!B.length)return;
    var sub=B.reduce(function(s,x){return s+priced(x).p*(x.q||1)},0),sh=shipFor(B);
    document.getElementById('b-n').textContent=B.reduce(function(s,x){return s+(x.q||1)},0);
    document.getElementById('b-sub').textContent=money(sub);document.getElementById('b-ship').textContent=money(sh.cents)+' or free pickup';
    document.getElementById('b-tot').textContent=money(sub+sh.cents);}
  var go=document.getElementById('b-go'),bst=document.getElementById('b-st');
  if(go)go.addEventListener('click',function(){if(!P||!P.enabled)return;var B=get().filter(priced).map(function(x){return {slug:priced(x).s,qty:x.q||1}});if(!B.length)return;
    if(!document.getElementById('b-terms').checked){bst.textContent='Please read and agree to the Terms of Service first.';return}
    go.disabled=true;bst.textContent='Opening secure checkout…';
    fetch(P.endpoint+'/api/checkout',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({items:B})}).then(function(r){return r.json().then(function(j){return {ok:r.ok,j:j}})})
      .then(function(r){if(r.ok&&r.j.url){location.href=r.j.url}else{go.disabled=false;bst.textContent=(r.j&&r.j.error)||'Checkout is not available right now. Send the list as a quote request instead.'}})
      .catch(function(){go.disabled=false;bst.textContent='Checkout could not be reached. Try again, or send the list as a quote request.'})});
  function v(id){return document.getElementById(id).value.trim()}
  function text(){var L=quoteItems(),out=['Quote request (cart) — True Part Fabrication','','Name: '+v('rl-name')];if(v('rl-co'))out.push('Company: '+v('rl-co'));out.push('Contact: '+v('rl-contact'));if(v('rl-when'))out.push('Needed by: '+v('rl-when'));out.push('','Parts:');
    L.forEach(function(x,i){out.push((i+1)+'. Qty '+(x.q||1)+' — '+clean(x.t).replace(/\n/g,' — '))});if(v('rl-notes'))out.push('','Notes:',v('rl-notes'));out.push('','Agreed to the Terms of Service: yes','(Please attach photos of the parts or equipment if you have them)');return out.join('\n')}
  function check(){var er=document.getElementById('rl-err');if(!v('rl-name')||!v('rl-contact')){er.textContent='Add your name and a way to reach you.';er.hidden=false;return false}if(!document.getElementById('rl-terms').checked){er.textContent='Please read and agree to the Terms of Service before sending.';er.hidden=false;return false}er.hidden=true;return true}
  document.getElementById('rl-form').addEventListener('submit',function(e){e.preventDefault();if(!check())return;location.href='mailto:@@TO@@?subject='+encodeURIComponent('Quote request: '+quoteItems().length+' parts'+(v('rl-co')?' ('+v('rl-co')+')':''))+'&body='+encodeURIComponent(text());st.textContent='Your email app opened with the request. Send it to finish.'});
  document.getElementById('rl-copy').addEventListener('click',function(){if(!check())return;var t=text();try{navigator.clipboard.writeText(t).then(function(){st.textContent='Copied. Paste it into an email to us.'},function(){st.textContent='Copy did not work in this browser.'})}catch(e){st.textContent='Copy did not work in this browser.'}});
  document.getElementById('rl-clear').addEventListener('click',function(){set([]);draw();st.textContent='Cart cleared.'});
  document.getElementById('rl-print').addEventListener('click',function(){window.print()});
  document.getElementById('rl-csv').addEventListener('click',function(){var L=get(),rows=[['Line','Quantity','Part','Replaces / fits','Price each','Line total']];L.forEach(function(x,i){var t=clean(x.t).split('\n'),p=priced(x);rows.push([i+1,x.q||1,t[0],t.slice(1).join(' '),p?(p.p/100).toFixed(2):'Quote',p?(p.p*(x.q||1)/100).toFixed(2):''])});
    var csv=rows.map(function(r){return r.map(function(c){c=String(c);return /[",\n]/.test(c)?'"'+c.replace(/"/g,'""')+'"':c}).join(',')}).join('\r\n');
    var a=document.createElement('a');a.href=URL.createObjectURL(new Blob([csv],{type:'text/csv'}));a.download='TPF-cart.csv';document.body.appendChild(a);a.click();setTimeout(function(){URL.revokeObjectURL(a.href);a.remove()},500);st.textContent='Spreadsheet downloaded.'});
  // reorder links: the whole cart in one URL to bookmark or send to whoever buys
  function enc(L){return btoa(unescape(encodeURIComponent(JSON.stringify(L.map(function(x){return {t:x.t,q:x.q||1}}))))).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'')}
  function dec(s){try{s=s.replace(/-/g,'+').replace(/_/g,'/');while(s.length%4)s+='=';var a=JSON.parse(decodeURIComponent(escape(atob(s))));return Array.isArray(a)?a.filter(function(x){return x&&typeof x.t==='string'&&x.t.length<400}).slice(0,60).map(function(x){return {t:x.t,q:Math.min(999,Math.max(1,parseInt(x.q,10)||1))}}):[]}catch(e){return []}}
  document.getElementById('rl-link').addEventListener('click',function(){var L=get();if(!L.length)return;var u=location.origin+location.pathname+'?r='+enc(L);try{navigator.clipboard.writeText(u).then(function(){st.textContent='Reorder link copied. Bookmark it, or send it to whoever places orders.'},function(){st.textContent=u})}catch(e){st.textContent=u}});
  (function(){var r=new URLSearchParams(location.search).get('r');if(!r)return;var A=dec(r);if(!A.length)return;var box=document.createElement('div');box.className='qr-note';box.setAttribute('role','region');box.setAttribute('aria-label','Reorder link');
    var p=document.createElement('p');p.style.margin='0 0 10px';p.textContent='This reorder link has '+A.length+(A.length===1?' part':' parts')+': '+A.map(function(x){return 'Qty '+x.q+' '+clean(x.t).split('\n')[0]}).join('; ')+'.';
    var b=document.createElement('button');b.type='button';b.className='btn';b.textContent='Add them to my cart';b.addEventListener('click',function(){var L=get();A.forEach(function(x){var i=L.findIndex(function(y){return y.t===x.t});if(i>-1)L[i].q=x.q;else L.push(x)});set(L);draw();box.remove();history.replaceState(null,'',location.pathname);st.textContent='Added to your cart.'});
    box.appendChild(p);box.appendChild(b);ul.parentNode.insertBefore(box,ul)})();
  draw();
  fetch('@@PRICES@@').then(function(r){return r.json()}).then(function(j){P=j;
    if(go){go.disabled=!j.enabled;document.getElementById('b-off').hidden=j.enabled}draw()}).catch(function(){});
})();
"""

def cart(c):
    body = f"""<main id="main">
<div class="page-hero"><div class="wrap">
  {B.crumbs(c, [('Home', ''), ('Cart', 'request-list/')])}
  <h1>Your cart</h1>
  <p class="lead">Collect parts while you browse. Parts with a listed price and a confirmed fit can be bought online. Everything else goes to us as one quote request. Your cart is saved on this device.</p>
</div></div>
<div class="wrap" style="padding-block:40px 90px">
  <ul class="rl-items" id="rl-items"></ul>
  <p id="rl-empty" style="color:var(--muted);margin-top:18px" hidden>Your cart is empty. Use <b>+ Add to cart</b> on any part in the <a href="{c.link('parts/')}" style="color:var(--ink)">parts catalog</a>, a brand page, or a part page, or design a custom piece in the <a href="{c.link('tools/adapter-builder/')}" style="color:var(--ink)">adapter builder</a>.</p>
  <section class="buy" id="buy" aria-labelledby="buy-h" hidden>
    <h2 id="buy-h">Buy online</h2>
    <p class="note">Priced parts with a confirmed fit, made to order in Modesto.</p>
    <dl class="sum">
      <dt>Pieces</dt><dd id="b-n">0</dd>
      <dt>Subtotal</dt><dd id="b-sub">$0.00</dd>
      <dt>Shipping (estimate)</dt><dd id="b-ship">–</dd>
      <dt>Sales tax</dt><dd>Shown at checkout</dd>
      <dt class="tot">Estimated total</dt><dd class="tot" id="b-tot">$0.00</dd>
    </dl>
    <label class="agree" for="b-terms" style="display:flex;gap:10px;align-items:flex-start;margin:6px 0 14px"><input type="checkbox" id="b-terms"> <span>I've read and agree to the <a href="{c.link('terms/')}#t2">Terms of Service</a>, including the online order terms.</span></label>
    <div style="display:flex;gap:12px;align-items:center;flex-wrap:wrap"><button class="btn" type="button" id="b-go" disabled>Check out securely <span class="ar">→</span></button><span id="b-st" role="status" style="color:var(--muted);font-size:.92rem"></span></div>
    <p class="note" id="b-off">Online checkout opens {esc(CHECKOUT['opens'])}. Until then, send your cart as a quote request below and we'll reply with a total.</p>
    <p class="note">Payment is handled by Stripe on a secure page. We never see your full card number.</p>
  </section>
  <div id="rl-send" hidden>
    <h2 id="rl-qh" style="font-size:1.3rem;margin:44px 0 18px">Send the list</h2>
    <form class="xform" id="rl-form" novalidate>
      <label for="rl-name">Your name<input id="rl-name" autocomplete="name" required></label>
      <label for="rl-co">Company<input id="rl-co" autocomplete="organization"></label>
      <label for="rl-contact">Phone or email<input id="rl-contact" required></label>
      <label for="rl-when">Needed by<input id="rl-when" placeholder="Date, or 'no rush'"></label>
      <label class="full" for="rl-notes">Notes (optional)<textarea id="rl-notes" placeholder="Equipment model numbers, colors, delivery address"></textarea></label>
      <label class="agree full" for="rl-terms"><input type="checkbox" id="rl-terms"> <span>I've read and agree to the <a href="{c.link('terms/')}">Terms of Service</a>.</span></label>
      <p class="xerr" id="rl-err" role="alert" hidden></p>
      <div class="full" style="display:flex;gap:12px;align-items:center;flex-wrap:wrap"><button class="btn" type="submit">Open in my email <span class="ar">→</span></button><button class="btn ghost" type="button" id="rl-copy">Copy request</button><button class="btn ghost" type="button" id="rl-csv">Download spreadsheet (CSV)</button><button class="btn ghost" type="button" id="rl-print">Print cart</button><button class="btn ghost" type="button" id="rl-link">Copy reorder link</button><button class="btn ghost" type="button" id="rl-clear">Clear cart</button><span id="rl-st" role="status" style="color:var(--muted);font-size:.92rem"></span></div>
    </form>
  </div>
</div>
</main>
<script>{CART_JS.replace('@@TO@@', __import__('extras').QUOTE_TO).replace('@@PRICES@@', c.asset('prices.json'))}</script>"""
    return B.doc(c, B.head(c, "Cart | True Part Fabrication", "Your cart: buy priced compatible parts online or send the rest in one quote request.", [B.crumbs_ld([("Home", ""), ("Cart", "request-list/")])]), body)

def cart_alias(c):
    to = c.link("request-list/")
    body = f"""<main id="main"><div class="page-hero" style="border-bottom:0"><div class="wrap"><h1>Cart</h1><p class="lead">Your cart is at <a href="{to}" style="color:var(--ink)">this page</a>.</p></div></div></main>
<script>location.replace({json.dumps(to)})</script>"""
    return B.doc(c, B.head(c, "Cart | True Part Fabrication", "Go to your cart.", []), body)

def order_success(c):
    body = f"""<main id="main">
<div class="page-hero"><div class="wrap">
  {B.crumbs(c, [('Home', ''), ('Order received', 'order/success/')])}
  <h1>Thank you. Your order is in.</h1>
  <p class="lead">Stripe has emailed your receipt. We'll make your parts to order in Modesto and email you when they ship or are ready for pickup.</p>
</div></div>
<div class="wrap order-box" style="padding-block:40px 90px">
  <p id="o-ref" style="color:var(--muted)" hidden>Order reference: <b id="o-id" style="color:var(--ink)"></b>. Keep it if you need to contact us.</p>
  <p>Questions about your order? Call <a href="tel:+12095544800" style="color:var(--ink)">(209) 554-4800</a> or reply to your receipt email.</p>
  <p>Every part is covered by our <a href="{c.link('terms/')}" style="color:var(--ink)">fit guarantee</a>: if it doesn't fit the model listed, we'll reprint it at no charge.</p>
  <div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:22px"><a class="btn" href="{c.link('parts/')}">Keep browsing <span class="ar">→</span></a><a class="btn ghost" href="{c.link('request-list/')}">View cart</a></div>
</div>
</main>
<script>(function(){{var id=new URLSearchParams(location.search).get('session_id');if(id){{document.getElementById('o-id').textContent=id.slice(-10).toUpperCase();document.getElementById('o-ref').hidden=false}}
  try{{fetch('{c.asset('prices.json')}').then(function(r){{return r.json()}}).then(function(P){{var L=JSON.parse(localStorage.getItem('tpf-list')||'[]');L=L.filter(function(x){{return !P.items[x.t.replace(/^Compatible part: |^Pieza compatible: /,'')]}});localStorage.setItem('tpf-list',JSON.stringify(L));var p=document.getElementById('list-pill'),b=document.getElementById('list-n');if(p)p.hidden=!L.length;if(b)b.textContent=L.length}})}}catch(e){{}}}})();</script>"""
    return B.doc(c, B.head(c, "Order received | True Part Fabrication", "Thank you for your order from True Part Fabrication.", []), body)

def order_cancelled(c):
    body = f"""<main id="main">
<div class="page-hero"><div class="wrap">
  {B.crumbs(c, [('Home', ''), ('Checkout cancelled', 'order/cancelled/')])}
  <h1>Checkout cancelled</h1>
  <p class="lead">No payment was taken. Your cart is still saved on this device.</p>
</div></div>
<div class="wrap order-box" style="padding-block:40px 90px">
  <div style="display:flex;gap:12px;flex-wrap:wrap"><a class="btn" href="{c.link('request-list/')}">Back to cart <span class="ar">→</span></a><a class="btn ghost" href="{c.link('', 'quote')}">Ask a question</a></div>
</div>
</main>"""
    return B.doc(c, B.head(c, "Checkout cancelled | True Part Fabrication", "Your checkout was cancelled and no payment was taken.", []), body)

TERMS_ONLINE = ("Online orders", [
    "Some parts can be bought online at a listed price. Online ordering is available only for parts with a confirmed fit for the models listed on the part page.",
    "Prices are in US dollars. Shipping and any sales tax are shown before you pay. Payment is processed by Stripe; we don't receive or store your full card number.",
    "Online orders are made to order. We'll email you if we can't make a part as ordered, and refund that part in full.",
    "You can cancel an online order for a full refund until we start making it. After that, the fit guarantee below applies.",
])
PRIVACY_PAY = '<h2>Payments</h2>\n  <p>When you buy online, checkout happens on a secure page run by Stripe, which processes the payment under its own privacy policy. We receive your name, email, phone, shipping address, and what you ordered so we can fill the order. We don\'t receive or store your full card number.</p>\n  '

def pages():
    return {"request-list/": cart, "cart/": cart_alias, "order/success/": order_success, "order/cancelled/": order_cancelled}
