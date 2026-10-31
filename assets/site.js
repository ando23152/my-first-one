
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
    if(form){fill(text);e.preventDefault();document.getElementById('quote').scrollIntoView({behavior:'smooth'})}
    else{store('tpf-part',text)}
  });
  function fill(t){var d=document.getElementById('q-desc');if(!d){var e=document.getElementById('e-desc');if(e){e.value=t+'\nMi modelo: ';}return}document.getElementById('q-type').value='Replacement part';d.value=t+'\nMy model: ';setTimeout(function(){document.getElementById('q-name').focus({preventScroll:true})},600)}

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
    function syncURL(){try{var p=new URLSearchParams();if(brand!=='All')p.set('brand',brand);if(q.value.trim())p.set('q',q.value.trim());if(!fit.checked)p.set('all','1');var qs=p.toString();history.replaceState(null,'',location.pathname+(qs?'?'+qs:''))}catch(e){}}
    var rr=render;render=function(){rr();syncURL()};
    try{var P=new URLSearchParams(location.search);if(P.get('q'))q.value=P.get('q');if(P.get('all')==='1')fit.checked=false;var pb=P.get('brand');if(pb){var ch=[].find.call(document.querySelectorAll('#cat-chips .chip'),function(x){return x.getAttribute('data-b').toLowerCase()===pb.toLowerCase()});if(ch){brand=ch.getAttribute('data-b');document.querySelectorAll('#cat-chips .chip').forEach(function(k){k.setAttribute('aria-pressed',k===ch)})}}}catch(e){}
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
