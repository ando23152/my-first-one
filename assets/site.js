
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
  function fill(t){var d=document.getElementById('q-desc');if(!d){var e=document.getElementById('e-desc');if(e){e.value=t+'\nMi modelo: ';}return}document.getElementById('q-type').value=/^Custom adapter/.test(t)?'Custom part or prototype':'Replacement part';d.value=t+'\nMy model: ';setTimeout(function(){document.getElementById('q-name').focus({preventScroll:true})},600)}

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

  // ---- request list ----
  var LK='tpf-list',ES=document.documentElement.lang==='es';
  function getL(){try{return JSON.parse(localStorage.getItem(LK)||'[]')}catch(e){return []}}
  function setL(a){try{localStorage.setItem(LK,JSON.stringify(a))}catch(e){}updPill();document.dispatchEvent(new CustomEvent('tpf-list'))}
  function inL(t){return getL().some(function(x){return x.t===t})}
  function updPill(){var p=document.getElementById('list-pill'),n=getL().length;if(!p)return;p.hidden=n===0;var b=document.getElementById('list-n');if(b)b.textContent=n;p.setAttribute('aria-label',(ES?'Lista de solicitud: ':'Request list: ')+n+(ES?' piezas':n===1?' part':' parts'))}
  function lbl(on){return on?(ES?'✓ En la lista':'✓ On list'):(ES?'+ Lista':'+ Add to list')}
  document.querySelectorAll('a[data-part]').forEach(function(a){
    if(a.closest('.pc')||a.closest('.stickybar'))return;
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
  document.body.appendChild(tt);tt.addEventListener('click',function(){scrollTo({top:0,behavior:innerWidth<=900?'smooth':'instant'});var m=document.getElementById('main');if(m){m.setAttribute('tabindex','-1');m.focus({preventScroll:true})}});
  addEventListener('scroll',function(){tt.hidden=scrollY<1200},{passive:true});

  // ---- recently viewed parts ----
  var RK='tpf-recent',rc=document.getElementById('recent');
  function getR(){try{return JSON.parse(localStorage.getItem(RK)||'[]')}catch(e){return []}}
  if(rc){var me=rc.getAttribute('data-me'),R=getR().filter(function(x){return x.u!==location.pathname});
    if(R.length){var box=document.getElementById('recent-list');R.slice(0,6).forEach(function(x){var a=document.createElement('a');a.href=x.u;a.textContent=x.n;var sp=document.createElement('span');sp.textContent=x.r;a.appendChild(sp);box.appendChild(a)});rc.hidden=false}
    if(me){var parts=me.split('|'),A=getR().filter(function(x){return x.u!==location.pathname});A.unshift({u:location.pathname,n:parts[0],r:parts[1]||''});try{localStorage.setItem(RK,JSON.stringify(A.slice(0,8)))}catch(e){}}}
  // ---- print + share ----
  document.addEventListener('click',function(e){
    var pb=e.target.closest('[data-print]');if(pb){window.print();return}
    var sb=e.target.closest('[data-share]');if(!sb)return;var st=sb.parentNode.querySelector('.tstat'),u=location.href.split('#')[0],t=sb.getAttribute('data-title')||document.title;
    if(navigator.share){navigator.share({title:t,url:u}).catch(function(){})}
    else{try{navigator.clipboard.writeText(u).then(function(){if(st)st.textContent='Link copied.'},function(){if(st)st.textContent=u})}catch(err){if(st)st.textContent=u}}
  });
  // ---- faster page loads: prefetch internal links on hover or touch ----
  var pf={};function pre(e){var a=e.target.closest&&e.target.closest('a[href]');if(!a||a.target||a.hasAttribute('download'))return;var h=a.href.split('#')[0];if(!h||pf[h]||a.origin!==location.origin||h===location.href.split('#')[0]||/^mailto:|^tel:/.test(a.getAttribute('href')))return;pf[h]=1;var l=document.createElement('link');l.rel='prefetch';l.href=h;document.head.appendChild(l)}
  document.addEventListener('mouseover',pre,{passive:true});document.addEventListener('touchstart',pre,{passive:true});

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
