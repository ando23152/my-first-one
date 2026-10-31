"""Spanish pages: /es/ and /es/preguntas-frecuentes/"""
import re, html
import build as B
esc = html.escape
QUOTE_TO = "ando23152@gmail.com"

ES_CSS = r"""
/* ---- spanish pages ---- */
.es-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}
.es-card{padding:28px;border:1px solid var(--line);border-radius:8px;background:var(--surface);display:grid;gap:10px;align-content:start}
.es-card .k{font:500 .7rem var(--f-mono);letter-spacing:.16em;text-transform:uppercase;color:var(--accent-hi)}
.es-card h3{font-family:var(--f-body);font-stretch:100%;font-weight:600;font-size:1.15rem;text-transform:none;letter-spacing:0}
.es-card p{color:var(--muted)}
.es-sec{padding-block:80px;border-top:1px solid var(--line)}
.es-steps{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.es-steps li{padding:24px;border:1px solid var(--line);border-radius:8px}
.es-steps b{display:block;font:500 .75rem var(--f-mono);color:var(--accent-hi);letter-spacing:.12em;margin-bottom:8px}
.es-steps h3{font-family:var(--f-body);font-stretch:100%;font-weight:600;font-size:1.05rem;text-transform:none;letter-spacing:0;margin-bottom:6px}
.es-steps p{color:var(--muted);font-size:.95rem}
.es-no{columns:2;gap:40px;color:var(--ink);padding-left:20px}
.es-no li{margin-bottom:8px;break-inside:avoid}
.es-form{display:grid;grid-template-columns:1fr 1fr;gap:16px;max-width:820px}
.es-form label{display:grid;gap:6px;font:500 .8rem var(--f-mono);letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.es-form input,.es-form select,.es-form textarea{font:400 1rem var(--f-body);color:var(--ink);background:var(--surface);border:1px solid var(--line);border-radius:6px;padding:12px 14px;text-transform:none;letter-spacing:0}
.es-form textarea{min-height:130px;resize:vertical}
.es-form .full{grid-column:1/-1}
.es-form .agree{grid-column:1/-1}
.es-err{color:var(--accent-hi);grid-column:1/-1}
.lang-link{font-size:.88rem}
@media (max-width:860px){.es-grid,.es-steps{grid-template-columns:1fr}.es-no{columns:1}.es-form{grid-template-columns:1fr}}
"""

SERV = [("Piezas de repuesto", "Descontinuada no significa perdida.", "Componentes de plástico difíciles de encontrar para herramientas, aspiradoras de taller, equipos y productos del hogar. Los hacemos iguales al original o mejorados donde falló. Solo piezas que no son críticas para la seguridad."),
        ("Fabricación a medida", "Hecho según su dibujo.", "Soportes, plantillas (jigs), fijaciones (fixtures), organizadores, prototipos y componentes especiales, modelados en CAD a partir de su boceto, muestra o medidas."),
        ("Electrónica y productos", "Carcasas para lo que viene.", "Dispositivos electrónicos prácticos, productos con tarjeta de circuito (PCB) y gabinetes a medida, cada uno con las pruebas y el cumplimiento que corresponden."),
        ("Lotes pequeños", "Cinco o quinientas.", "Producción repetida sin moldes ni mínimos de miles de unidades. Guardamos el modelo de su pieza, así el próximo pedido sale igual al primero.")]
INDS = [("Procesamiento de alimentos", "Soportes, bases para sensores, guías y portaobjetos junto a la línea. Solo piezas que no tocan alimentos."),
        ("Agricultura", "Clips, cubiertas, separadores y bases para equipo agrícola, para productores y distribuidores de maquinaria."),
        ("Almacenes y cámaras frías", "Portaetiquetas, bases para escáneres, guías de cables y organizadores en materiales para baja temperatura."),
        ("Talleres industriales", "Plantillas, fijaciones, conexiones para colección de polvo y ayudas de trabajo hechas según sus dibujos.")]
STEPS = [("Nos cuenta", "Mande fotos, la pieza rota, un boceto o el número de modelo."),
         ("Medimos", "Con calibrador en el taller, o en su sitio si la pieza no se puede quitar."),
         ("Modelamos", "Dibujada en CAD, igual al original o mejorada donde falló."),
         ("Usted aprueba", "Material, precio y tiempo de entrega por escrito antes de empezar."),
         ("Imprimimos", "Impresa, limpia y revisada contra las medidas de ajuste."),
         ("Queda bien", "Entregada o enviada. Si no queda, la reimprimimos gratis.")]
NO = ["Piezas críticas para la seguridad o de soporte de carga", "Piezas a presión o de aire comprimido", "Piezas eléctricas y carcasas eléctricas",
      "Frenos o dirección de vehículos", "Artículos de seguridad infantil o médicos", "Artículos de seguridad para albercas",
      "Piezas para cumplir códigos de construcción", "Piezas que tocan alimentos o bebidas"]

FAQ_ES = [
 ("¿Cuándo abren?", "Abrimos el 1 de enero de 2027. Ya puede mandarnos solicitudes de cotización y le responderemos con preguntas o una cotización por escrito, para que su trabajo esté listo cuando abramos."),
 ("¿Qué necesito mandar para una cotización?", "Lo mejor es la pieza original, aunque esté rota. Si no puede mandarla, mande fotos claras desde varios ángulos con una regla o calibrador en la foto, la marca y el modelo del equipo, y cualquier número de pieza que encuentre. Si tiene un archivo 3D, adjúntelo. Aceptamos STL, STEP y la mayoría de los formatos CAD."),
 ("¿Cuánto cuesta una pieza?", "Depende del tamaño, del material y de cuántas necesite. La mayoría de los trabajos para negocios van de unos $75 a $800 o más. Cada trabajo lleva una cotización por escrito con el material, el precio y el tiempo de entrega antes de imprimir."),
 ("¿Cuánto tardan?", "Depende de si hay que medir y modelar la pieza desde cero o si ya tenemos el modelo. Su cotización indica el tiempo de entrega antes de empezar. Los pedidos repetidos son más rápidos porque el modelo ya está guardado."),
 ("¿Qué pasa si la pieza no queda?", "La reimprimimos gratis. Mándenos sus medidas o la pieza, ajustamos el modelo y la corregimos. Esa es nuestra garantía de ajuste."),
 ("¿Pueden hacer una pieza a partir de una foto?", "A veces. Las piezas sencillas se pueden modelar con buenas fotos y una medida de referencia. Las piezas con ajustes precisos, como adaptadores de manguera y clips, normalmente necesitan la original o medidas cuidadosas con calibrador."),
 ("¿Las piezas impresas son tan fuertes como las originales?", "Muchas veces sí, y a veces más, si el material y la orientación de impresión son los correctos. Elegimos materiales como PETG, ASA o nylon con fibra de carbono según el trabajo, y podemos reforzar el punto donde falló la original. Le diremos con honestidad si una pieza impresa no conviene para su uso."),
 ("¿Qué piezas no hacen?", "No hacemos piezas cuya falla pueda lastimar a alguien: críticas para la seguridad, de soporte de carga, a presión, eléctricas, de frenos o dirección, de seguridad infantil, médicas, de seguridad para albercas o para cumplir códigos. Tampoco hacemos piezas que tocan alimentos."),
 ("¿Hacen pedidos repetidos y lotes pequeños?", "Sí. Guardamos el modelo de su pieza, así los pedidos siguientes salen iguales. Cinco o quinientas, sin moldes ni mínimos grandes."),
 ("¿Dónde están y hacen envíos?", "Estamos en Modesto, California, y atendemos Modesto, Ceres, Turlock, Manteca, Tracy y Stockton, incluso con medición en su sitio para piezas que no se pueden quitar de la máquina. También enviamos a todo el estado."),
 ("¿Sus piezas son originales de la marca?", "No. Son piezas compatibles (de reemplazo) que diseñamos y fabricamos nosotros. Los nombres de marca y números de pieza se usan solo para indicar con qué son compatibles."),
 ("¿Hablan español?", "Sí. Puede escribirnos en español y le responderemos en español. Nuestros Términos de servicio y el catálogo de piezas están en inglés por ahora."),
]

def header_es(c):
    import extras as X
    L = c.link
    mb, mp = X.menu(c, es=True)
    return f"""<a href="#main" class="skip" style="position:absolute;left:-9999px;top:0;z-index:50;background:var(--accent);color:#fff;padding:10px 16px" onfocus="this.style.left='12px'" onblur="this.style.left='-9999px'">Saltar al contenido</a>
<div class="opening" role="note"><div class="wrap">Abrimos el 1 de enero de 2027 <span aria-hidden="true">·</span> <a href="{L('es/', 'cotizar')}">Ya aceptamos solicitudes de cotización</a></div></div>
<header id="hdr">
  <div class="wrap bar">
    <a class="brand" href="{L('es/')}" aria-label="True Part Fabrication, inicio en español"><img src="{c.asset('img/logo-dark.png')}" alt="True Part Fabrication" width="800" height="493"></a>
    <nav class="main" aria-label="Principal">
      <a class="l" href="{L('es/', 'servicios')}">Servicios</a>
      <a class="l" href="{L('es/', 'industrias')}">Industrias</a>
      <a class="l" href="{L('es/', 'proceso')}">Cómo funciona</a>
      <a class="l" href="{L('es/preguntas-frecuentes/')}">Preguntas</a>
      <a class="l" href="{L('es/piezas/')}">Piezas</a>
      <a class="l lang-link" href="{L('')}" hreflang="en" lang="en">English</a>
      <button class="theme-btn" type="button" id="theme-btn" aria-label="Cambiar tema"><svg class="moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg><svg class="sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg></button>
      <a class="btn" href="{L('es/', 'cotizar')}">Pedir cotización</a>
      {mb}
    </nav>
  </div>
</header>
{mp}"""

def footer_es(c):
    L = c.link
    return f"""<footer>
  <div class="wrap">
    <div class="foot">
      <div><img src="{c.asset('img/logo-dark.png')}" alt="True Part Fabrication" width="800" height="493" loading="lazy"><p style="color:var(--muted);margin-top:18px;max-width:28em;font-size:.95rem">Piezas de repuesto, fabricación a medida y producción en lotes pequeños en Modesto, California.</p></div>
      <div><h4>Explorar</h4><ul><li><a href="{L('es/', 'servicios')}">Servicios</a></li><li><a href="{L('es/', 'industrias')}">Industrias</a></li><li><a href="{L('es/preguntas-frecuentes/')}">Preguntas frecuentes</a></li><li><a href="{L('es/piezas/')}">Catálogo de piezas</a></li><li><a href="{L('tools/hose-size-finder/')}" hreflang="en">Tamaños de manguera (inglés)</a></li><li><a href="{L('')}" hreflang="en" lang="en">English</a></li></ul></div>
      <div><h4>Contacto</h4><ul><li><a href="{L('es/', 'cotizar')}">Pedir cotización</a></li><li><a href="{B.EBAY}" target="_blank" rel="noopener">Tienda en eBay</a></li><li><a href="{L('privacy/')}" hreflang="en">Privacidad (inglés)</a></li><li><a href="{L('terms/')}" hreflang="en">Términos de servicio (inglés)</a></li></ul></div>
    </div>
    <div class="copy-line"><span>© 2026 True Part Fabrication LLC</span><span>Modesto · Ceres · Turlock · Manteca · Tracy · Stockton</span></div>
  </div>
</footer>
<script src="{c.asset('site.js')}?v=7" defer></script>"""

def doc_es(c, headhtml, body):
    alt = f'<link rel="alternate" hreflang="en" href="{B.BASE}/">\n<link rel="alternate" hreflang="es" href="{B.BASE}/es/">\n<link rel="alternate" hreflang="x-default" href="{B.BASE}/">'
    h = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
{headhtml}
{alt}
</head>
<body>
{header_es(c)}
{body}
{footer_es(c)}
</body>
</html>
"""
    h = h.replace('<meta property="og:type"', '<meta property="og:locale" content="es_US">\n<meta property="og:type"', 1)
    return B.a11y(B.webp(B.swapimgs(h)))

FORM_JS = r"""<script>
(function(){
  var f=document.getElementById('qf-es');if(!f)return;
  function v(id){return document.getElementById(id).value.trim()}
  f.addEventListener('submit',function(e){
    e.preventDefault();var err=document.getElementById('es-err');
    if(!v('e-name')||!v('e-contact')||!v('e-desc')){err.textContent='Escriba su nombre, cómo contactarle y una descripción de la pieza.';err.hidden=false;return}
    if(!document.getElementById('e-terms').checked){err.textContent='Para continuar, acepte los Términos de servicio.';err.hidden=false;return}
    err.hidden=true;
    var L=['Solicitud de cotización (español)','','Nombre: '+v('e-name')];
    if(v('e-co'))L.push('Empresa: '+v('e-co'));
    L.push('Contacto: '+v('e-contact'),'Tipo de trabajo: '+v('e-type'),'Cantidad: '+(v('e-qty')||'1'),'','Descripción:',v('e-desc'),'','Acepta los Términos de servicio: sí','(Adjunte una foto de la pieza)');
    location.href='mailto:'+f.getAttribute('data-to')+'?subject='+encodeURIComponent('Solicitud de cotización')+'&body='+encodeURIComponent(L.join('\n'));
    document.getElementById('es-st').textContent='Se abrió su programa de correo. Adjunte una foto de la pieza y envíe el mensaje.';
  });
})();
</script>"""

def home_es(c):
    L = c.link
    serv = "".join(f'<div class="es-card"><div class="k">{esc(k)}</div><h3>{esc(h)}</h3><p>{esc(p)}</p></div>' for k, h, p in SERV)
    inds = "".join(f'<div class="es-card"><h3>{esc(h)}</h3><p>{esc(p)}</p></div>' for h, p in INDS)
    steps = "".join(f'<li><b>{i+1:02d}</b><h3>{esc(h)}</h3><p>{esc(p)}</p></li>' for i, (h, p) in enumerate(STEPS))
    no = "".join(f"<li>{esc(x)}</li>" for x in NO)
    body = f"""<main id="main">
<div class="page-hero"><div class="wrap">
  <div class="label">En español</div>
  <h1>Piezas de repuesto y manufactura a medida en Modesto, CA</h1>
  <p class="lead">Diseñamos y fabricamos piezas de repuesto, soportes, plantillas y lotes pequeños para negocios y talleres del Valle Central. Si la pieza no queda, la reimprimimos gratis.</p>
  <div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:26px"><a class="btn" href="{L('es/', 'cotizar')}">Pedir cotización <span class="ar">→</span></a><a class="btn ghost" href="{L('es/piezas/')}">Ver catálogo de piezas</a></div>
</div></div>

<section class="es-sec" id="servicios" style="border-top:0"><div class="wrap">
  <div class="head"><div class="label">Qué hacemos</div><h2>Cuatro formas de <em class="s">resolver la pieza.</em></h2><p>Desde un adaptador roto hasta un pedido repetido de cientos de soportes, cada trabajo se modela, se imprime y se revisa en nuestro taller.</p></div>
  <div class="es-grid">{serv}</div>
</div></section>

<section class="es-sec" id="industrias"><div class="wrap">
  <div class="head"><div class="label">Para negocios</div><h2>Hecho para el <em class="s">Valle Central.</em></h2><p>Atendemos Modesto, Ceres, Turlock, Manteca, Tracy y Stockton, con medición en su sitio cuando la pieza no se puede quitar.</p></div>
  <div class="es-grid">{inds}</div>
</div></section>

<section class="es-sec" id="proceso"><div class="wrap">
  <div class="head"><div class="label">Cómo funciona</div><h2>De la pieza rota a <em class="s">la que queda.</em></h2></div>
  <ol class="es-steps">{steps}</ol>
</div></section>

<section class="es-sec" id="limites"><div class="wrap">
  <div class="head"><div class="label">Lo que no hacemos</div><h2>Si una falla puede <em class="s">lastimar a alguien, no la hacemos.</em></h2></div>
  <ul class="es-no">{no}</ul>
  <div class="callout" style="margin-top:28px;max-width:720px"><div class="k">Garantía de ajuste</div><p>Si una pieza que hicimos no queda en el equipo indicado en su cotización, avísenos dentro de 30 días y la reimprimimos sin costo.</p></div>
</div></section>

<section class="es-sec" id="cotizar"><div class="wrap">
  <div class="head"><div class="label">Cotización</div><h2>Cuéntenos de <em class="s">su pieza.</em></h2><p>Llene el formulario y se abrirá su correo con la solicitud lista. Adjunte una foto de la pieza y envíela. Respondemos en español.</p></div>
  <form class="es-form" id="qf-es" data-to="{QUOTE_TO}" novalidate>
    <label for="e-name">Nombre<input id="e-name" autocomplete="name" required></label>
    <label for="e-co">Empresa (opcional)<input id="e-co" autocomplete="organization"></label>
    <label for="e-contact">Teléfono o correo<input id="e-contact" required></label>
    <label for="e-type">Tipo de trabajo<select id="e-type"><option>Pieza de repuesto</option><option>Fabricación a medida</option><option>Lote pequeño</option><option>Electrónica o gabinete</option><option>Otro</option></select></label>
    <label for="e-qty">Cantidad<input id="e-qty" inputmode="numeric" placeholder="1"></label>
    <label class="full" for="e-desc">Descripción de la pieza<textarea id="e-desc" required placeholder="Qué pieza es, marca y modelo del equipo, número de pieza si lo tiene, y para qué se usa."></textarea></label>
    <label class="agree" for="e-terms"><input type="checkbox" id="e-terms"> <span>He leído y acepto los <a href="{L('terms/')}" hreflang="en">Términos de servicio</a> (en inglés).</span></label>
    <p class="es-err" id="es-err" role="alert" hidden></p>
    <div class="full" style="display:flex;gap:14px;align-items:center;flex-wrap:wrap"><button class="btn" type="submit">Abrir en mi correo <span class="ar">→</span></button><span id="es-st" role="status" style="color:var(--muted);font-size:.92rem"></span></div>
  </form>
  <div style="margin-top:40px">{__import__('extras').notify_block(c, es=True)}</div>
  <p style="margin-top:22px;color:var(--muted)">¿Busca una pieza lista? <a href="{B.EBAY}" target="_blank" rel="noopener" style="color:var(--ink)">Compre en la tienda de True Part Fabrication en eBay</a>.</p>
</div></section>
</main>
{FORM_JS}"""
    org = dict(B.ORG); org["availableLanguage"] = ["English", "Spanish"]
    t = "Piezas de repuesto y manufactura a medida en Modesto, CA | True Part Fabrication"
    d = "Diseñamos y fabricamos piezas de repuesto, soportes, plantillas y lotes pequeños para negocios en Modesto, Turlock, Stockton y el Valle Central. Reimpresión gratis si no queda."
    return doc_es(c, B.head(c, t, d, [org]), body)

def faq_es(c):
    det = "\n".join(f"<details{' open' if i == 0 else ''}><summary>{esc(q)}</summary><div class=\"a\"><p>{esc(a)}</p></div></details>" for i, (q, a) in enumerate(FAQ_ES))
    body = f"""<main id="main">
<div class="page-hero"><div class="wrap">
  {B.crumbs(c, [('Inicio', 'es/'), ('Preguntas frecuentes', 'es/preguntas-frecuentes/')])}
  <h1>Preguntas frecuentes</h1>
  <p class="lead">Cotizaciones, precios, tiempos de entrega, materiales y lo que podemos y no podemos hacer.</p>
</div></div>
<div class="wrap faq">{det}</div>
<div class="cta-band"><div class="wrap"><h2>¿Tiene otra pregunta?</h2><p>Cuéntenos de su pieza y le responderemos con preguntas o una cotización por escrito.</p><a class="btn" href="{c.link('es/', 'cotizar')}">Pedir cotización <span class="ar">→</span></a></div></div>
</main>"""
    faqld = {"@context": "https://schema.org", "@type": "FAQPage", "inLanguage": "es",
             "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ_ES]}
    return doc_es(c, B.head(c, "Preguntas frecuentes sobre manufactura y piezas | True Part Fabrication",
                            "Respuestas sobre cotizaciones, precios, tiempos de entrega, materiales, garantía de ajuste y lo que True Part Fabrication puede hacer en Modesto, CA.",
                            [faqld, B.crumbs_ld([("Inicio", "es/"), ("Preguntas frecuentes", "es/preguntas-frecuentes/")])]), body)

def pages():
    return {"es/": home_es, "es/preguntas-frecuentes/": faq_es}
