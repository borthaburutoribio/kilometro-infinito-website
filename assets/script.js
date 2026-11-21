// Kilómetro Infinito · sin dependencias
(() => {
  const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const R = document.documentElement.dataset.root || './';
  const norm = s => s.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9 ]/g, ' ').replace(/\s+/g, ' ').trim();
  const pesos = n => '$ ' + n.toLocaleString('es-AR');
  const MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
  const fecha = s => { const [y, m, d] = s.split('-').map(Number); return `${d} de ${MESES[m - 1]} de ${y}`; };
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  // Barra transparente sobre la foto, blanca al bajar
  const barEl = $('.bar');
  const onS = () => barEl.classList.toggle('solid', scrollY > 60);
  addEventListener('scroll', onS, { passive: true }); onS();
  // Botón flotante: solo después de la portada, que ya tiene el suyo
  const fabEl = $('.fab'), fabTop = $('.hero') || $('.ph');
  if (fabEl && fabTop) {
    const onF = () => fabEl.classList.toggle('wait', fabTop.getBoundingClientRect().bottom > 0);
    addEventListener('scroll', onF, { passive: true }); addEventListener('resize', onF); onF();
  }
  // Menú móvil
  const mt = $('.menu-t'), nav = $('.nav');
  if (mt) mt.addEventListener('click', () => { const o = nav.classList.toggle('open'); barEl.classList.toggle('open', o); mt.setAttribute('aria-expanded', o); mt.textContent = o ? 'Cerrar' : 'Menú'; });

  // Entradas al hacer scroll
  $$('.ph>.wrap,.sec>.wrap').forEach(x => { if (!x.querySelector('.rv') && !x.classList.contains('rv')) x.classList.add('rv'); });
  const rv = $$('.rv');
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { rootMargin: '0px 0px -8% 0px' });
    rv.forEach(x => io.observe(x));
  } else rv.forEach(x => x.classList.add('in'));

  // Fotos que cambian dentro del marco de la portada
  $$('.frame[data-swap]').forEach(f => {
    const im = $$('img', f); let i = 0; if (im.length < 2) return;
    setInterval(() => { im[i].classList.remove('on'); i = (i + 1) % im.length; const n = im[i]; if (n.dataset.src) { n.src = n.dataset.src; n.removeAttribute('data-src'); } n.style.animation = 'none'; void n.offsetWidth; n.style.animation = ''; n.classList.add('on'); }, 4200);
  });

  // Reloj hasta la próxima carrera
  const races = (() => { try { return JSON.parse($('#races-data').textContent); } catch { return []; } })();
  const clockEls = $$('[data-clock]');
  if (clockEls.length) {
    const tick = () => {
      clockEls.forEach(el => {
        const t = new Date(el.dataset.clock) - Date.now();
        if (t <= 0) { el.textContent = el.dataset.done || 'Ya largó'; return; }
        const d = Math.floor(t / 864e5), h = Math.floor(t / 36e5) % 24, m = Math.floor(t / 6e4) % 60, s = Math.floor(t / 1e3) % 60;
        const p = x => String(x).padStart(2, '0');
        el.textContent = `${d}d ${p(h)}:${p(m)}:${p(s)}`;
      });
    };
    tick(); setInterval(tick, 1000);
  }
  // La barra de la portada siempre muestra la que sigue
  const nb = $('[data-nextbar]');
  if (nb && races.length) {
    const now = Date.now(), r = races.find(x => new Date(x.start) > now);
    if (r) { $('[data-n-name]', nb).firstChild.textContent = r.name; $('[data-n-name]', nb).href = R + 'calendario/' + r.id + '/'; $('[data-n-when]', nb).textContent = r.when; $('[data-clock]', nb).dataset.clock = r.start; $('[data-n-btn]', nb).href = R + 'calendario/' + r.id + '/'; }
  }
  // Marca las pasadas en las listas
  $$('[data-race-date]').forEach(li => { if (new Date(li.dataset.raceDate) < Date.now()) { const t = $('.st', li); if (t) t.textContent = 'Ya se corrió'; } });

  // Buscador de corredores
  let namesP = null;
  const loadNames = () => namesP || (namesP = fetch(R + 'assets/data/names.json').then(r => r.json()).then(a => a.map(x => ({ d: x[0], c: x[1], k: norm(x[0]) }))));
  $$('[data-finder]').forEach(form => {
    const inp = $('input', form), ul = $('.sug', form); let sel = -1;
    const go = n => { location.href = R + 'corredor/?n=' + encodeURIComponent(n); };
    inp.addEventListener('focus', loadNames, { once: true });
    inp.addEventListener('input', async () => {
      const q = norm(inp.value); sel = -1;
      if (q.length < 3) { ul.innerHTML = ''; return; }
      const all = await loadNames(), tk = q.split(' ');
      const hits = all.filter(x => tk.every(t => x.k.includes(t))).slice(0, 8);
      ul.innerHTML = hits.length ? hits.map(h => `<li><a href="${R}corredor/?n=${encodeURIComponent(h.d)}">${esc(h.d)}<span>${h.c} ${h.c === 1 ? 'carrera' : 'carreras'}</span></a></li>`).join('') : '<li><a>No encontramos ese nombre. Probá solo con el apellido.</a></li>';
    });
    inp.addEventListener('keydown', e => {
      const a = $$('a[href]', ul);
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); sel = (sel + (e.key === 'ArrowDown' ? 1 : -1) + a.length) % (a.length || 1); a.forEach((x, i) => x.classList.toggle('sel', i === sel)); }
      if (e.key === 'Escape') ul.innerHTML = '';
    });
    form.addEventListener('submit', e => { e.preventDefault(); const a = $$('a[href]', ul); const t = a[sel] || a[0]; if (t) location.href = t.href; });
    document.addEventListener('click', e => { if (!form.contains(e.target)) ul.innerHTML = ''; });
  });

  // Ficha del corredor
  const prof = $('#perfil');
  if (prof) (async () => {
    const q = new URLSearchParams(location.search).get('n');
    if (!q) return;
    const key = norm(q);
    const crc = s => { let c, r = -1; for (let i = 0; i < s.length; i++) { c = (r ^ s.charCodeAt(i)) & 255; for (let k = 0; k < 8; k++) c = c & 1 ? (c >>> 1) ^ 0xEDB88320 : c >>> 1; r = (r >>> 8) ^ c; } return (r ^ -1) >>> 0; };
    const [races2, shard] = await Promise.all([fetch(R + 'assets/data/races.json').then(r => r.json()), fetch(R + `assets/data/r/${crc(key) % 96}.json`).then(r => r.json()).catch(() => ({}))]);
    const rows = shard[key];
    $('#p-name').textContent = q;
    document.title = q + ' · resultados en Kilómetro Infinito';
    if (!rows) { $('#p-none').hidden = false; return; }
    const pos = r => parseInt(r[1], 10);
    const pods = rows.filter(r => pos(r) >= 1 && pos(r) <= 3).length, wins = rows.filter(r => pos(r) === 1).length;
    const years = {}; const places = {};
    rows.forEach(r => { const e = races2[r[0]]; const y = e[1].slice(0, 4); years[y] = (years[y] || 0) + 1; if (e[2]) places[e[2]] = (places[e[2]] || 0) + 1; });
    const ys = Object.keys(years).sort(), mn = +ys[0], mx = +ys[ys.length - 1];
    $('#p-figs').innerHTML = [[rows.length, rows.length === 1 ? 'carrera' : 'carreras'], [pods, 'veces en el podio'], [Object.keys(places).length, Object.keys(places).length === 1 ? 'localidad' : 'localidades'], [mn === mx ? mn : `${mn} a ${mx}`, 'años con crono de KMI']].map(([a, b]) => `<div><b>${a}</b>${b}</div>`).join('');
    const big = Math.max(...Object.values(years)); let bars = '';
    for (let y = mn; y <= mx; y++) bars += `<i title="${y}: ${years[y] || 0}" style="height:${Math.max(2, (years[y] || 0) / big * 100)}%"></i>`;
    $('#p-bars').innerHTML = bars; $('#p-bl').innerHTML = `<span>${mn}</span><span>${mx}</span>`;
    const top = Object.entries(places).sort((a, b) => b[1] - a[1]).slice(0, 12);
    $('#p-places').innerHTML = top.map(([a, b]) => `<li>${esc(a)} <b>${b}</b></li>`).join('');
    $('#p-rows').innerHTML = rows.map(r => { const e = races2[r[0]], p = pos(r); return `<tr class="${p >= 1 && p <= 3 ? 'pod' : ''}"><td>${esc(r[1] || '')}</td><td class="n"><a href="${R}p/${r[4]}.html?n=${encodeURIComponent(q)}">${esc(e[0])}</a></td><td style="white-space:nowrap">${fecha(e[1]).replace(/ de (\d{4})/, ' $1').replace(' de ', ' ')}</td><td class="hm">${esc(e[2])}</td><td class="hm">${esc(r[3])}</td><td>${esc(r[2])}</td></tr>`; }).join('');
    $('#p-data').hidden = false;
    const sh = $('#p-share');
    sh.addEventListener('click', async () => { const url = location.href, text = `Mis ${rows.length} carreras con el crono de KMI`; try { if (navigator.share) await navigator.share({ title: text, url }); else { await navigator.clipboard.writeText(url); sh.textContent = 'Link copiado'; } } catch { } });
  })();

  // Tabla de resultados: filtro y resaltar al corredor
  const rt = $('#res');
  if (rt) {
    const f = $('#res-q'), secs = $$('.sect', rt), rowsAll = $$('tbody tr', rt);
    rowsAll.forEach(tr => { tr._k = norm(tr.textContent); });
    const q0 = new URLSearchParams(location.search).get('n');
    const apply = () => { const tk = norm(f.value).split(' ').filter(Boolean); secs.forEach(s => { let any = false; $$('tbody tr', s).forEach(tr => { const m = tk.every(t => tr._k.includes(t)); tr.hidden = !m; any = any || m; }); s.hidden = !any; }); };
    if (f) f.addEventListener('input', apply);
    if (q0) { const k = norm(q0).split(' '); const hit = rowsAll.filter(tr => k.every(t => tr._k.includes(t))); hit.forEach(h => h.classList.add('me')); if (hit[0]) setTimeout(() => hit[0].scrollIntoView({ block: 'center' }), 200); }
    const sel = $('#res-cat');
    if (sel) sel.addEventListener('change', () => { if (sel.value) $('#' + sel.value).scrollIntoView(); });
  }

  // Listado de carreras con filtros
  const rl = $('#race-list');
  if (rl) {
    const q = $('#rl-q'), y = $('#rl-y'), d = $('#rl-d'), p = $('#rl-p'), cnt = $('#rl-c');
    const items = $$('li[data-y]', rl).map(li => ({ li, k: norm(li.dataset.k), y: li.dataset.y, d: li.dataset.d, p: li.dataset.p }));
    const heads = $$('[data-year]', rl);
    const run = () => {
      const tk = norm(q.value).split(' ').filter(Boolean); let n = 0; const seen = new Set();
      items.forEach(i => { const m = (!y.value || i.y === y.value) && (!d.value || i.d === d.value) && (!p.value || i.p === p.value) && tk.every(t => i.k.includes(t)); i.li.hidden = !m; if (m) { n++; seen.add(i.y); } });
      heads.forEach(h => { h.hidden = !seen.has(h.dataset.year); });
      cnt.textContent = n + (n === 1 ? ' carrera' : ' carreras');
    };
    [q, y, d, p].forEach(x => x.addEventListener('input', run));
  }

  // Tu categoría: modalidad y rama con botones + año de nacimiento
  const rdEl = $('#races-data');
  const RACES = rdEl ? JSON.parse(rdEl.textContent) : {};
  const catOf = (race, mod, g, y) => {
    const age = race.year - y;
    const list = ((race.cats[mod] || {})[g]) || [];
    return { age, c: list.find(c => age >= (c[1] ?? 0) && age <= (c[2] ?? 200)) };
  };
  const pickState = new Map();
  $$('.cp').forEach(cp => {
    const race = RACES[cp.dataset.race]; if (!race) return;
    const st = { mod: '', g: '', y: 0, cat: '' }; pickState.set(cp, st);
    const out = $('.cp-out', cp), yr = $('.cp-y', cp);
    const run = () => {
      const ok = st.mod && st.g && st.y >= 1920 && st.y <= 2020;
      st.cat = '';
      if (!ok) { out.hidden = !(st.y && (st.y < 1920 || st.y > 2020)); if (!out.hidden) out.innerHTML = '<p>Revisá el año: tiene que tener 4 números, por ejemplo 1971.</p>'; return; }
      const { age, c } = catOf(race, st.mod, st.g, st.y);
      out.hidden = false;
      if (!c) { out.innerHTML = `<b class="big">Consultanos</b><p>Con ${age} años al 31/12 no entrás en las categorías publicadas de esta modalidad. Escribinos y lo vemos.</p>`; return; }
      st.cat = c[0];
      out.innerHTML = `<b class="big">${esc(c[0])}</b><p>${age} años al 31 de diciembre · ${esc(race.dist[st.mod] || '')}</p>`;
    };
    $$('.seg', cp).forEach(seg => seg.addEventListener('click', e => {
      const b = e.target.closest('.seg-b'); if (!b) return;
      $$('.seg-b', seg).forEach(x => x.setAttribute('aria-pressed', String(x === b)));
      st[seg.dataset.k] = b.dataset.v; run(); cp.dispatchEvent(new Event('cpchange'));
    }));
    yr.addEventListener('input', () => { st.y = parseInt(yr.value, 10) || 0; run(); cp.dispatchEvent(new Event('cpchange')); });
    // si viene ?mod=&g=&y= (desde la página de la carrera), se completa solo
    const q = new URLSearchParams(location.search);
    if (q.get('c') === cp.dataset.race) {
      ['mod', 'g'].forEach(k => { const b = $(`.seg[data-k="${k}"] .seg-b[data-v="${q.get(k)}"]`, cp); if (b) b.click(); });
      if (q.get('y')) { yr.value = q.get('y'); yr.dispatchEvent(new Event('input')); }
    }
  });
  // En la página de la carrera, "Inscribirme" lleva lo que ya eligió
  const cf = $('#catfinder');
  if (cf) {
    const cp = $('.cp', cf), go = $('.btn.y', cf), base = go.getAttribute('href');
    cp.addEventListener('cpchange', () => { const s = pickState.get(cp); const u = new URLSearchParams(base.split('?')[1]); if (s.mod) u.set('mod', s.mod); if (s.g) u.set('g', s.g); if (s.y) u.set('y', s.y); go.href = base.split('?')[0] + '?' + u; });
  }

  // Inscripción completa: carrera, datos, pago, comprobante
  const ins = $('#ins');
  if (ins) {
    const cfg = JSON.parse($('#ins-cfg').textContent);
    const sel = $('#i-race'), err = $('#i-err'), steps = $$('.steps li', ins);
    const q = new URLSearchParams(location.search);
    if (q.get('c') && RACES[q.get('c')]) sel.value = q.get('c');
    const showRace = () => $$('[data-for]', ins).forEach(d => { d.hidden = d.dataset.for !== sel.value; });
    sel.addEventListener('change', showRace); showRace();
    const curPick = () => pickState.get($(`[data-for="${sel.value}"] .cp`, ins));
    const today = new Date(); today.setHours(0, 0, 0, 0);
    const tierOf = race => race.tiers.find(t => today <= new Date(t.to + 'T23:59:00') && today >= new Date(t.from + 'T00:00:00'));
    const F = ['nombre', 'apellido', 'dni', 'nac', 'cel', 'mail', 'ciudad', 'equipo', 'pareja', 'coment'];
    const KEY = 'kmi-corredor';
    try { const saved = JSON.parse(localStorage.getItem(KEY) || 'null'); if (saved) { F.forEach(k => { if (saved[k]) $('#i-' + k).value = saved[k]; }); $('#i-recordado').hidden = false; } } catch (e) {}
    let n = 1;
    const say = m => { err.textContent = m; err.hidden = !m; };
    const go = k => {
      n = k; $$('.st', ins).forEach(f => { f.hidden = +f.dataset.st !== n; });
      steps.forEach((li, i) => { li.classList.toggle('on', i === n - 1); li.classList.toggle('ok', i < n - 1); });
      say(''); const t = $(`.st[data-st="${n}"]`, ins); ins.scrollIntoView({ behavior: 'smooth', block: 'start' });
      const f = $('input,select,button', t); if (f && n > 1) f.focus({ preventScroll: true });
    };
    const check = () => {
      if (n === 1) {
        const s = curPick(), race = RACES[sel.value];
        if (!s || !s.mod) return 'Elegí en qué te anotás: Competitiva, Promocional o Principiantes.';
        if (!s.g) return 'Elegí Damas o Caballeros.';
        if (!s.cat) return 'Poné tu año de nacimiento (4 números) para ver tu categoría.';
        if (!tierOf(race)) return 'La inscripción de esta carrera no está abierta hoy. Escribinos y lo vemos.';
      }
      if (n === 2) {
        for (const k of ['nombre', 'apellido', 'dni', 'nac', 'cel', 'mail', 'ciudad']) { const el = $('#i-' + k); if (!el.value.trim()) { el.focus(); return 'Falta completar: ' + el.labels[0].textContent + '.'; } }
        if (!/^\d{7,8}$/.test($('#i-dni').value.replace(/\D/g, ''))) return 'Revisá el DNI: van 7 u 8 números, sin puntos.';
        if (!$('#i-mail').checkValidity()) return 'Revisá el mail.';
        const y = +$('#i-nac').value.slice(0, 4); if (y !== curPick().y) return `La fecha de nacimiento dice ${y || '-'} y arriba elegiste ${curPick().y}. Revisá cuál es.`;
      }
      return '';
    };
    const fillPay = () => {
      const race = RACES[sel.value], s = curPick(), t = tierOf(race), i = race.tiers.indexOf(t), nx = race.tiers[i + 1];
      $('#i-monto').textContent = pesos(t[s.mod]);
      $('#i-tramo').textContent = `${race.name} · ${s.cat}. Este precio vale hasta el ${fecha(t.to)}` + (nx ? `; desde el día siguiente es ${pesos(nx[s.mod])}.` : '.');
    };
    ins.addEventListener('click', e => {
      if (e.target.closest('[data-next]')) { const m = check(); if (m) return say(m); if (n === 2) fillPay(); go(n + 1); }
      if (e.target.closest('[data-prev]')) go(n - 1);
      const cp = e.target.closest('.copy'); if (cp) { navigator.clipboard?.writeText($('#' + cp.dataset.copy).textContent.trim()); cp.textContent = 'Copiado'; setTimeout(() => { cp.textContent = 'Copiar'; }, 1600); }
    });
    if (q.get('mod') && q.get('g') && q.get('y')) { const m = check(); if (!m) go(2); }
    const comp = $('#i-comp');
    comp.addEventListener('change', () => { const f = comp.files[0]; $('#i-comp-n').textContent = f ? `${f.name} · ${(f.size / 1048576).toFixed(1)} MB` : 'La captura de la transferencia, hasta 8 MB'; $('.drop', ins).classList.toggle('has', !!f); say(''); });
    // Achica las fotos antes de mandarlas (los PDF van como están)
    const toData = f => new Promise((ok, no) => {
      const rd = new FileReader(); rd.onerror = no;
      if (!f.type.startsWith('image/')) { rd.onload = () => ok({ name: f.name, type: f.type, data: rd.result.split(',')[1] }); return rd.readAsDataURL(f); }
      rd.onload = () => { const im = new Image(); im.onerror = () => ok({ name: f.name, type: f.type, data: rd.result.split(',')[1] }); im.onload = () => {
        const k = Math.min(1, 1600 / Math.max(im.width, im.height)), c = document.createElement('canvas'); c.width = Math.round(im.width * k); c.height = Math.round(im.height * k);
        c.getContext('2d').drawImage(im, 0, 0, c.width, c.height); ok({ name: f.name.replace(/\.\w+$/, '') + '.jpg', type: 'image/jpeg', data: c.toDataURL('image/jpeg', 0.82).split(',')[1] });
      }; im.src = rd.result; }; rd.readAsDataURL(f);
    });
    ins.addEventListener('submit', async e => {
      e.preventDefault();
      if (n !== 4) return;
      const f = comp.files[0];
      if (!f) return say('Falta el comprobante: sin comprobante no queda hecha la preinscripción.');
      if (f.size > 8 * 1048576) return say('El archivo pesa más de 8 MB. Mandá una captura de pantalla del comprobante.');
      const race = RACES[sel.value], s = curPick(), t = tierOf(race);
      const d = Object.fromEntries(F.map(k => [k, $('#i-' + k).value.trim()]));
      try { if ($('#i-rec').checked) localStorage.setItem(KEY, JSON.stringify(d)); else localStorage.removeItem(KEY); } catch (er) {}
      const btn = $('#i-send'); btn.disabled = true; btn.textContent = 'Enviando…';
      try {
        if (cfg.url) {
          const body = { carrera: race.name, carreraId: sel.value, modalidad: s.mod, rama: s.g === 'd' ? 'Damas' : 'Caballeros', categoria: s.cat, monto: t[s.mod], ...d, comprobante: await toData(f) };
          const r = await fetch(cfg.url, { method: 'POST', headers: { 'Content-Type': 'text/plain;charset=utf-8' }, body: JSON.stringify(body) });
          const j = await r.json(); if (!j.ok) throw new Error(j.error || 'error');
        } else { await toData(f); $('#i-demo').hidden = false; }
        $('#i-res').textContent = `${d.nombre} ${d.apellido}, ${s.cat} en ${race.name}.`;
        if (race.insc) { const l = $('#i-lista'); l.href = race.insc; l.hidden = false; }
        go(5); $('.steps', ins).hidden = true;
      } catch (er) {
        say('No se pudo enviar. Revisá la conexión y probá de nuevo. Si sigue sin andar, escribinos a kminfinito@live.com.ar.');
      } finally { btn.disabled = false; btn.textContent = 'Enviar preinscripción'; }
    });
  }

  // Fotos de cada carrera: salen de las carpetas de Drive de Adrián (o un ejemplo, si todavía no está conectado)
  const alb = $('#albums');
  if (alb) {
    const url = alb.dataset.url, list = $('.albs', alb), view = $('.alb-view', alb), grid = $('.alb-g', alb);
    const demo = JSON.parse($('#albums-demo').textContent);
    const th = (id, w) => `https://drive.google.com/thumbnail?id=${encodeURIComponent(id)}&sz=w${w}`;
    const lb = document.createElement('figure'); lb.className = 'lb'; lb.setAttribute('role', 'dialog'); lb.setAttribute('aria-modal', 'true'); lb.setAttribute('aria-label', 'Foto ampliada');
    lb.innerHTML = '<img alt=""><figcaption><a class="btn y dl" target="_blank" rel="noopener">Bajar la foto</a></figcaption><button class="x" aria-label="Cerrar">×</button><button class="p" aria-label="Anterior">‹</button><button class="n" aria-label="Siguiente">›</button>';
    document.body.append(lb);
    let fotos = [], k = 0, last;
    const big = f => f.full, show = j => { k = (j + fotos.length) % fotos.length; $('img', lb).src = big(fotos[k]); $('.dl', lb).href = fotos[k].dl; };
    const close = () => { lb.classList.remove('open'); last?.focus(); };
    $('.x', lb).onclick = close; $('.p', lb).onclick = () => show(k - 1); $('.n', lb).onclick = () => show(k + 1);
    lb.addEventListener('click', e => { if (e.target === lb) close(); });
    document.addEventListener('keydown', e => { if (!lb.classList.contains('open')) return; if (e.key === 'Escape') close(); if (e.key === 'ArrowLeft') show(k - 1); if (e.key === 'ArrowRight') show(k + 1); });
    const open = (nombre, fs) => {
      fotos = fs; list.hidden = true; view.hidden = false; $('.alb-t', view).textContent = nombre;
      grid.innerHTML = fs.map((f, j) => `<figure style="margin:0"><button data-j="${j}" aria-label="Ampliar foto ${j + 1}"><img src="${esc(f.small)}" alt="Foto ${j + 1} de ${esc(nombre)}" loading="lazy" decoding="async"></button></figure>`).join('');
      view.scrollIntoView({ block: 'start' });
    };
    grid.addEventListener('click', e => { const b = e.target.closest('[data-j]'); if (!b) return; last = b; show(+b.dataset.j); lb.classList.add('open'); $('.x', lb).focus(); });
    $('.alb-back', view).onclick = () => { view.hidden = true; list.hidden = false; };
    const card = (nombre, n, tapa, act) => `<button type="button" class="alb" data-act="${esc(act)}"><img src="${esc(tapa)}" alt="" loading="lazy"><b>${esc(nombre)}</b><span class="small">${n} fotos</span></button>`;
    if (!url) {
      const fs = demo.fotos.map(u => ({ small: u, full: u, dl: u }));
      list.innerHTML = card(demo.nombre, fs.length, fs[0].small, 'demo');
      list.onclick = e => { if (e.target.closest('.alb')) open(demo.nombre, fs); };
    } else {
      list.innerHTML = '<p>Cargando las carreras…</p>';
      fetch(url + '?fotos=lista').then(r => r.json()).then(al => {
        if (!al.length) { list.innerHTML = '<p>Todavía no hay fotos cargadas.</p>'; return; }
        list.innerHTML = al.map(a => card(a.nombre, a.n, th(a.tapa, 600), a.id)).join('');
        list.onclick = e => { const b = e.target.closest('.alb'); if (!b) return; b.disabled = true;
          fetch(url + '?fotos=' + encodeURIComponent(b.dataset.act)).then(r => r.json()).then(d => open(d.nombre, d.fotos.map(id => ({ small: th(id, 600), full: th(id, 1600), dl: 'https://drive.google.com/uc?export=download&id=' + encodeURIComponent(id) })))).finally(() => { b.disabled = false; }); };
      }).catch(() => { list.innerHTML = '<p>No pudimos cargar las fotos. Probá de nuevo en un rato.</p>'; });
    }
  }

  // Presupuesto por WhatsApp
  const bud = $('#budget');
  if (bud) {
    const send = $('#b-send');
    const up = () => {
      const v = id => $('#' + id).value.trim();
      const m = `Hola Adrián! Quiero cronometrar una carrera con KMI.\nEvento: ${v('b-name') || 'a definir'}\nDisciplina: ${v('b-disc')}\nFecha: ${v('b-date') || 'a definir'}\nLugar: ${v('b-place') || 'a definir'}\nCorredores estimados: ${v('b-n') || 'a definir'}\nMe pasás un presupuesto?`;
      send.href = 'https://wa.me/' + send.dataset.wa + '?text=' + encodeURIComponent(m);
    };
    $$('input,select', bud).forEach(x => x.addEventListener('input', up)); up();
  }

  // Visor de fotos
  const trig = $$('[data-lb]');
  if (trig.length) {
    const lb = document.createElement('figure'); lb.className = 'lb'; lb.setAttribute('role', 'dialog'); lb.setAttribute('aria-modal', 'true'); lb.setAttribute('aria-label', 'Foto ampliada');
    lb.innerHTML = '<img alt=""><figcaption></figcaption><button class="x" aria-label="Cerrar">×</button><button class="p" aria-label="Anterior">‹</button><button class="n" aria-label="Siguiente">›</button>';
    document.body.append(lb); let i = 0, last;
    const show = k => { i = (k + trig.length) % trig.length; const im = $('img', trig[i]); $('img', lb).src = trig[i].dataset.lb; $('img', lb).alt = im.alt; $('figcaption', lb).textContent = im.alt; };
    const close = () => { lb.classList.remove('open'); if (last) last.focus(); };
    trig.forEach((t, k) => t.addEventListener('click', () => { last = t; show(k); lb.classList.add('open'); $('.x', lb).focus(); }));
    $('.x', lb).onclick = close; $('.p', lb).onclick = () => show(i - 1); $('.n', lb).onclick = () => show(i + 1);
    lb.addEventListener('click', e => { if (e.target === lb) close(); });
    document.addEventListener('keydown', e => { if (!lb.classList.contains('open')) return; if (e.key === 'Escape') close(); if (e.key === 'ArrowLeft') show(i - 1); if (e.key === 'ArrowRight') show(i + 1); });
  }

  // Año fijo de la historia
  const sbg = $$('.story-bg img');
  if (sbg.length && 'IntersectionObserver' in window) {
    const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { const k = +e.target.dataset.i; sbg.forEach((im, n) => im.classList.toggle('on', n === k)); } }), { rootMargin: '-45% 0px -45% 0px' });
    $$('.step[data-i]').forEach(s => io.observe(s));
  }

  // Número que sube
  $$('[data-count]').forEach(el => {
    const to = +el.dataset.count;
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const io = new IntersectionObserver(([e]) => {
      if (!e.isIntersecting) return; io.disconnect(); const t0 = performance.now();
      const f = t => { const p = Math.min(1, (t - t0) / 1400), v = Math.round(to * (1 - Math.pow(1 - p, 3))); el.textContent = v.toLocaleString('es-AR'); if (p < 1) requestAnimationFrame(f); };
      requestAnimationFrame(f);
    }); io.observe(el);
  });
})();
