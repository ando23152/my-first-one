
(function(){
  var root=document.documentElement,tb=document.getElementById('theme-btn'),meta=document.querySelector('meta[name="theme-color"]');
  function applyTheme(t){
    if(t==='light')root.setAttribute('data-tpf-theme','light');else root.removeAttribute('data-tpf-theme');
    document.querySelectorAll('img[data-light]').forEach(function(i){if(!i.getAttribute('data-dark'))i.setAttribute('data-dark',i.getAttribute('src'));var want=t==='light'?i.getAttribute('data-light'):i.getAttribute('data-dark');if(i.getAttribute('src')!==want)i.setAttribute('src',want)});
    if(tb)tb.setAttribute('aria-label',t==='light'?'Switch to dark theme':'Switch to light theme');
    if(meta)meta.setAttribute('content',t==='light'?'#ffffff':'#070708');
  }
  applyTheme(root.getAttribute('data-tpf-theme')==='light'?'light':'dark');
  if(tb)tb.addEventListener('click',function(){var t=root.getAttribute('data-tpf-theme')==='light'?'dark':'light';applyTheme(t);try{localStorage.setItem('tpf-theme',t)}catch(e){}});
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
      st.textContent='Copy your request, then send it to us with a photo of the part.';
    });
    document.getElementById('q-copy').addEventListener('click',function(){
      var t=txt.textContent;
      function sel(){var r=document.createRange();r.selectNodeContents(txt);var s=getSelection();s.removeAllRanges();s.addRange(r);st.textContent='Text selected. Copy it with your keyboard or menu.'}
      try{navigator.clipboard.writeText(t).then(function(){st.textContent='Copied. Paste it into an email with a photo attached.'},sel)}catch(e){sel()}
    });
  }
})();
