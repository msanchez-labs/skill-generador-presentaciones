/* ==========================================================================
   Presentador HTML · engine.js  (vanilla, sin dependencias)
   Navegación · fragmentos · pantalla completa · láser · foco · lupa · trazos
   resaltado de texto · comentarios · notas · edición en vivo · presentador
   vista general · paleta · sonido · guardar como HTML · API para QA
   ========================================================================== */
(function () {
  'use strict';
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const W = 1920, H = 1080;
  let CFG = {};
  try { CFG = JSON.parse($('#deck-config').textContent || '{}'); } catch (e) { CFG = {}; }
  const LANG = CFG.lang || document.documentElement.lang || 'es';
  const stage = $('#stage'), viewport = $('#viewport');
  const slides = $$('#stage > section.slide');
  const N = slides.length;
  const params = new URLSearchParams(location.search);
  const PRESENTER = params.has('presenter');
  const REDUCED = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  const noAnim = () => REDUCED || document.documentElement.classList.contains('no-anim');

  /* ---------------- Estado persistente ---------------- */
  const KEY = 'deck:' + (CFG.id || 'deck') + ':' + (CFG.buildId || '0');
  const S = (function load() {
    let emb = {}, loc = null;
    try { emb = JSON.parse($('#deck-state').textContent || '{}') || {}; } catch (e) { emb = {}; }
    try { loc = JSON.parse(localStorage.getItem(KEY) || 'null'); } catch (e) { loc = null; }
    const s = Object.assign({ ink: {}, notes: {}, comments: {}, html: {}, prefs: {}, score: 0 }, emb);
    if (loc && (loc.ts || 0) >= (emb.ts || 0)) Object.assign(s, loc);
    return s;
  })();
  let saveTimer = null;
  function persist() {
    S.ts = Date.now();
    clearTimeout(saveTimer);
    saveTimer = setTimeout(() => { try { localStorage.setItem(KEY, JSON.stringify(S)); } catch (e) { /* modo privado / file:// */ } }, 250);
  }

  // Restaurar ediciones de texto / resaltados guardados
  slides.forEach(sl => { const h = S.html[sl.dataset.id]; if (typeof h === 'string' && h.length) sl.innerHTML = h; });

  /* ---------------- Utilidades ---------------- */
  const sid = i => slides[i] ? slides[i].dataset.id : '';
  const titleOf = i => (slides[i] && (slides[i].dataset.title || ($('.title', slides[i]) || {}).textContent || ('Slide ' + (i + 1)))).trim();
  const norm = s => (s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '');
  const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const toastEl = $('#toast');
  let toastT;
  function toast(msg) { if (!toastEl) return; toastEl.textContent = msg; toastEl.classList.add('on'); clearTimeout(toastT); toastT = setTimeout(() => toastEl.classList.remove('on'), 1800); }
  function download(name, text, type) {
    const blob = new Blob([text], { type: type || 'text/plain;charset=utf-8' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob); a.download = name;
    document.body.appendChild(a); a.click();
    setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 500);
  }
  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) { navigator.clipboard.writeText(text).then(() => toast('Copiado'), () => fallback()); return; }
    fallback();
    function fallback() {
      const ta = document.createElement('textarea'); ta.value = text; document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); toast('Copiado'); } catch (e) { toast('No se pudo copiar'); }
      ta.remove();
    }
  }

  /* ---------------- Escalado / zoom ---------------- */
  const T = { s: 1, tx: 0, ty: 0, base: 1, ox: 0, oy: 0 };
  const zoom = { on: false, x: W / 2, y: H / 2, k: 2 };
  function fit() {
    const r = viewport.getBoundingClientRect();
    const s = Math.min(r.width / W, r.height / H) || 1;
    T.base = s; T.ox = (r.width - W * s) / 2; T.oy = (r.height - H * s) / 2;
    applyTransform();
  }
  function applyTransform() {
    const r = viewport.getBoundingClientRect();
    if (zoom.on) { T.s = T.base * zoom.k; T.tx = r.width / 2 - zoom.x * T.s; T.ty = r.height / 2 - zoom.y * T.s; }
    else { T.s = T.base; T.tx = T.ox; T.ty = T.oy; }
    stage.style.transform = 'translate(' + T.tx + 'px,' + T.ty + 'px) scale(' + T.s + ')';
  }
  function clientToStage(cx, cy) { const r = viewport.getBoundingClientRect(); return { x: (cx - r.left - T.tx) / T.s, y: (cy - r.top - T.ty) / T.s }; }
  function stageToClient(x, y) { const r = viewport.getBoundingClientRect(); return { x: r.left + T.tx + x * T.s, y: r.top + T.ty + y * T.s }; }
  function setZoom(on, x, y) {
    zoom.on = on; if (on) { zoom.x = x; zoom.y = y; }
    stage.classList.add('zoom-anim'); applyTransform();
    setTimeout(() => stage.classList.remove('zoom-anim'), 480);
    document.body.classList.toggle('zoomed', on);
  }
  if (window.ResizeObserver) new ResizeObserver(fit).observe(viewport); else addEventListener('resize', fit);

  /* ---------------- Fragmentos ---------------- */
  function groupsOf(sl) {
    if (sl._groups) return sl._groups;
    const fr = $$('.frag', sl);
    let auto = 0; const map = new Map();
    fr.forEach(el => {
      const st = el.dataset.step !== undefined && el.dataset.step !== '' ? parseFloat(el.dataset.step) : (++auto);
      if (el.dataset.step === undefined || el.dataset.step === '') auto = Math.max(auto, st);
      if (!map.has(st)) map.set(st, []);
      map.get(st).push(el);
    });
    sl._groups = Array.from(map.keys()).sort((a, b) => a - b).map(k => map.get(k));
    return sl._groups;
  }
  slides.forEach(sl => { sl._groups = null; });

  /* ---------------- Navegación ---------------- */
  let cur = 0, step = 0, started = false, activeVT = null;
  function setStep(n, opts) {
    const g = groupsOf(slides[cur]);
    const prev = step;
    step = Math.max(0, Math.min(n, g.length));
    g.forEach((els, k) => els.forEach(el => {
      el.classList.toggle('visible', k < step);
      el.classList.toggle('dim', !!CFG.dimPrevious && k < step - 1);
    }));
    if (step > prev && !(opts && opts.silent)) {
      const shown = g[step - 1] || [];
      shown.forEach(el => { if (el.dataset.sfx) sfx(el.dataset.sfx); countups(el); });
    }
    updateChrome();
  }
  function goto(i, st, opts) {
    opts = opts || {};
    i = Math.max(0, Math.min(N - 1, i | 0));
    const changing = i !== cur || !started;
    const after = () => {
      const g = groupsOf(slides[cur]);
      const target = opts.all ? g.length : (st === 'last' ? g.length : (st | 0));
      step = -1; setStep(target, { silent: true }); step = Math.max(0, Math.min(target, g.length));
      if (changing) onEnter(opts);
      updateChrome();
      if (!opts.silent) send({ type: 'goto', i: cur, step: step });
    };
    if (!changing) { after(); return; }
    const swap = () => {
      slides.forEach((sl, k) => sl.classList.toggle('active', k === i));
      cur = i; started = true;
      if (zoom.on) { zoom.on = false; applyTransform(); document.body.classList.remove('zoomed'); }
      after();
    };
    if (!opts.instant && started && document.startViewTransition && !noAnim() && !tool) {
      try {
        if (activeVT) { try { activeVT.skipTransition(); } catch (e) { } }
        const vt = document.startViewTransition(swap); activeVT = vt;
        const quiet = () => { };
        vt.ready.catch(quiet); vt.finished.then(() => { if (activeVT === vt) activeVT = null; }, quiet);
        if (vt.updateCallbackDone) vt.updateCallbackDone.catch(quiet);
      } catch (e) { swap(); }
    } else {
      slides[i].classList.toggle('no-vt', started && !opts.instant && !noAnim());
      swap();
    }
  }
  function next() {
    const g = groupsOf(slides[cur]);
    if (step < g.length) { setStep(step + 1); send({ type: 'goto', i: cur, step: step }); }
    else if (cur < N - 1) goto(cur + 1, 0);
  }
  function prev() {
    if (step > 0) { setStep(step - 1); send({ type: 'goto', i: cur, step: step }); }
    else if (cur > 0) goto(cur - 1, 'last');
  }
  function onEnter(opts) {
    const sl = slides[cur];
    if (!opts.all) countups(sl); else countups(sl, true);
    if (sl.dataset.sfx && !opts.silent) sfx(sl.dataset.sfx);
    renderInk(); renderPins(); syncNotesPanel(); updatePresenter();
    const sr = $('#sr'); if (sr) sr.textContent = 'Slide ' + (cur + 1) + ' de ' + N + ': ' + titleOf(cur);
  }
  function updateChrome() {
    const c = $('#count'); if (c) c.textContent = (cur + 1) + ' / ' + N;
    const p = $('#progress'); if (p) p.style.width = (N > 1 ? (cur / (N - 1)) * 100 : 100) + '%';
    const h = '#/' + (cur + 1) + (step ? '/' + step : '');
    if (location.hash !== h) { try { history.replaceState(null, '', h); } catch (e) { /* file:// en algunos navegadores */ } }
  }
  function readHash() {
    const m = /#\/(\d+)(?:\/(\d+))?/.exec(location.hash || '');
    return m ? { i: Math.max(0, parseInt(m[1], 10) - 1), step: m[2] ? parseInt(m[2], 10) : 0 } : { i: 0, step: 0 };
  }
  addEventListener('hashchange', () => { const h = readHash(); if (h.i !== cur || h.step !== step) goto(h.i, h.step); });

  /* ---------------- Contadores animados ---------------- */
  function countups(root, instant) {
    $$('[data-countup]', root).concat(root.matches && root.matches('[data-countup]') ? [root] : []).forEach(el => {
      if (el.closest('.frag:not(.visible)')) return;
      const to = parseFloat(el.dataset.countup), dec = parseInt(el.dataset.decimals || '0', 10);
      const fmt = new Intl.NumberFormat(LANG, { minimumFractionDigits: dec, maximumFractionDigits: dec });
      if (instant || noAnim() || isNaN(to)) { el.textContent = fmt.format(to); return; }
      const t0 = performance.now(), ms = 1200;
      (function f(t) { const p = Math.min(1, (t - t0) / ms), e = 1 - Math.pow(1 - p, 4); el.textContent = fmt.format(to * e); if (p < 1) requestAnimationFrame(f); })(t0);
    });
  }

  /* ---------------- Herramientas ---------------- */
  const DRAW = ['pen', 'hl', 'arrow', 'rect', 'eraser'];
  let tool = null;
  function setTool(t) {
    if (t === tool) t = null;
    tool = t;
    document.body.className = document.body.className.replace(/\btool-\S+/g, '').replace(/\bdrawing\b/g, '').trim();
    if (t) document.body.classList.add('tool-' + t);
    if (t && DRAW.indexOf(t) >= 0) { document.body.classList.add('drawing'); lastDrawTool = t; }
    $$('#hud [data-tool]').forEach(b => b.classList.toggle('on', b.dataset.tool === t));
    if (t !== 'zoom' && zoom.on) setZoom(false);
    if (t === 'laser') laserLoop();
    if (t !== 'spot') { /* nada */ }
    hideMarkBtn();
    const badge = $('#badge-mode'); if (badge) badge.textContent = t === 'comment' ? 'Clic para comentar · Esc para salir' : 'Modo edición · Esc para salir';
    if (t) toast({ laser: 'Puntero láser', spot: 'Foco', zoom: 'Lupa: clic para acercar', pen: 'Lápiz · 1–5 colores', hl: 'Resaltador', arrow: 'Flecha', rect: 'Rectángulo', eraser: 'Borrador', comment: 'Clic donde quieras comentar' }[t] || t);
  }
  let lastDrawTool = 'pen';

  /* ---- Láser (trazo en coordenadas de lienzo; se dibuja en pantalla) ---- */
  const lc = $('#laser'), lctx = lc ? lc.getContext('2d') : null;
  const trail = []; let laserRunning = false;
  function sizeLaser() { if (!lc) return; const d = Math.min(2, window.devicePixelRatio || 1); lc.width = innerWidth * d; lc.height = innerHeight * d; lc.style.width = innerWidth + 'px'; lc.style.height = innerHeight + 'px'; lctx.setTransform(d, 0, 0, d, 0, 0); }
  addEventListener('resize', sizeLaser); sizeLaser();
  function laserPoint(x, y) { trail.push({ x: x, y: y, t: performance.now() }); laserLoop(); }
  function laserLoop() { if (laserRunning || !lctx) return; laserRunning = true; requestAnimationFrame(drawLaser); }
  function drawLaser(now) {
    lctx.clearRect(0, 0, innerWidth, innerHeight);
    while (trail.length && now - trail[0].t > 380) trail.shift();
    lctx.lineCap = 'round'; lctx.lineJoin = 'round';
    for (let k = 1; k < trail.length; k++) {
      const a = 1 - (now - trail[k].t) / 380; const p0 = stageToClient(trail[k - 1].x, trail[k - 1].y), p1 = stageToClient(trail[k].x, trail[k].y);
      lctx.strokeStyle = 'rgba(255,45,45,' + (a * 0.75) + ')'; lctx.lineWidth = Math.max(1, 9 * a);
      lctx.beginPath(); lctx.moveTo(p0.x, p0.y); lctx.lineTo(p1.x, p1.y); lctx.stroke();
    }
    const last = trail[trail.length - 1];
    if (last && (tool === 'laser' || now - last.t < 380)) {
      const p = stageToClient(last.x, last.y);
      lctx.shadowBlur = 22; lctx.shadowColor = 'rgba(255,30,30,.95)'; lctx.fillStyle = '#ff2d2d';
      lctx.beginPath(); lctx.arc(p.x, p.y, 8, 0, Math.PI * 2); lctx.fill();
      lctx.shadowBlur = 0; lctx.fillStyle = '#ffd5d5'; lctx.beginPath(); lctx.arc(p.x, p.y, 3, 0, Math.PI * 2); lctx.fill();
    }
    if (tool === 'laser' || trail.length) requestAnimationFrame(drawLaser);
    else { laserRunning = false; lctx.clearRect(0, 0, innerWidth, innerHeight); }
  }

  /* ---- Trazos ---- */
  const ink = $('#ink'), ictx = ink ? ink.getContext('2d') : null;
  if (ictx) ictx.setTransform(2, 0, 0, 2, 0, 0);
  const COLORS = CFG.inkColors || ['#ff3b30', '#ffcc00', '#34c759', '#0a84ff', '#ffffff'];
  let color = S.prefs.color || COLORS[0];
  const redo = {};
  let board = false;
  const inkKey = () => board ? '__board__' : sid(cur);
  function strokesFor(k) { return S.ink[k] || (S.ink[k] = []); }
  function drawStroke(c, s) {
    c.save();
    c.strokeStyle = s.c; c.fillStyle = s.c; c.lineCap = 'round'; c.lineJoin = 'round';
    if (s.t === 'hl') { c.globalAlpha = 0.34; c.lineWidth = s.w || 30; }
    else c.lineWidth = s.w || 6;
    const p = s.p;
    if (s.t === 'arrow' && p.length > 1) {
      const a = p[0], b = p[p.length - 1], ang = Math.atan2(b[1] - a[1], b[0] - a[0]), hl = 26 + c.lineWidth * 1.5;
      c.beginPath(); c.moveTo(a[0], a[1]); c.lineTo(b[0], b[1]); c.stroke();
      c.beginPath(); c.moveTo(b[0], b[1]);
      c.lineTo(b[0] - hl * Math.cos(ang - 0.45), b[1] - hl * Math.sin(ang - 0.45));
      c.lineTo(b[0] - hl * Math.cos(ang + 0.45), b[1] - hl * Math.sin(ang + 0.45)); c.closePath(); c.fill();
    } else if (s.t === 'rect' && p.length > 1) {
      const a = p[0], b = p[p.length - 1];
      const x = Math.min(a[0], b[0]), y = Math.min(a[1], b[1]), w = Math.abs(b[0] - a[0]), h = Math.abs(b[1] - a[1]), r = Math.min(14, w / 2, h / 2);
      c.beginPath(); c.moveTo(x + r, y); c.arcTo(x + w, y, x + w, y + h, r); c.arcTo(x + w, y + h, x, y + h, r); c.arcTo(x, y + h, x, y, r); c.arcTo(x, y, x + w, y, r); c.closePath(); c.stroke();
    } else if (p.length === 1) {
      c.beginPath(); c.arc(p[0][0], p[0][1], c.lineWidth / 2, 0, Math.PI * 2); c.fill();
    } else {
      c.beginPath(); c.moveTo(p[0][0], p[0][1]);
      for (let k = 1; k < p.length - 1; k++) { const mx = (p[k][0] + p[k + 1][0]) / 2, my = (p[k][1] + p[k + 1][1]) / 2; c.quadraticCurveTo(p[k][0], p[k][1], mx, my); }
      const l = p[p.length - 1]; c.lineTo(l[0], l[1]); c.stroke();
    }
    c.restore();
  }
  function renderInk(extra) {
    if (!ictx) return;
    ictx.clearRect(0, 0, W, H);
    (S.ink[inkKey()] || []).forEach(s => drawStroke(ictx, s));
    if (extra) drawStroke(ictx, extra);
  }
  let live = null;
  function inkDown(e) {
    if (!tool || DRAW.indexOf(tool) < 0) return;
    e.preventDefault(); ink.setPointerCapture && ink.setPointerCapture(e.pointerId);
    const p = clientToStage(e.clientX, e.clientY);
    if (tool === 'eraser') { erase(p); live = { t: 'eraser' }; return; }
    live = { t: tool, c: color, w: tool === 'hl' ? 30 : 6, p: [[Math.round(p.x), Math.round(p.y), +(e.pressure || 0.5).toFixed(2)]] };
    renderInk(live);
  }
  function inkMove(e) {
    if (!live) return;
    const evs = e.getCoalescedEvents ? e.getCoalescedEvents() : [e];
    if (live.t === 'eraser') { evs.forEach(ev => erase(clientToStage(ev.clientX, ev.clientY))); return; }
    if (live.t === 'arrow' || live.t === 'rect') { const p = clientToStage(e.clientX, e.clientY); live.p[1] = [Math.round(p.x), Math.round(p.y), 0.5]; }
    else evs.forEach(ev => { const p = clientToStage(ev.clientX, ev.clientY); const l = live.p[live.p.length - 1]; if (Math.abs(l[0] - p.x) + Math.abs(l[1] - p.y) > 1.5) live.p.push([Math.round(p.x), Math.round(p.y), +(ev.pressure || 0.5).toFixed(2)]); });
    renderInk(live);
  }
  function inkUp() {
    if (!live) return;
    if (live.t !== 'eraser') { strokesFor(inkKey()).push(live); (redo[inkKey()] = []); }
    live = null; renderInk(); persist(); sendInk();
  }
  function erase(p) {
    const arr = S.ink[inkKey()]; if (!arr) return;
    const R = 22; let changed = false;
    for (let k = arr.length - 1; k >= 0; k--) {
      const s = arr[k]; let pts = s.p;
      if ((s.t === 'rect' || s.t === 'arrow') && pts.length > 1) {
        const a = pts[0], b = pts[1]; pts = [];
        const seg = s.t === 'rect' ? [[a[0], a[1], b[0], a[1]], [b[0], a[1], b[0], b[1]], [b[0], b[1], a[0], b[1]], [a[0], b[1], a[0], a[1]]] : [[a[0], a[1], b[0], b[1]]];
        seg.forEach(q => { for (let u = 0; u <= 1; u += 0.05) pts.push([q[0] + (q[2] - q[0]) * u, q[1] + (q[3] - q[1]) * u]); });
      }
      if (pts.some(q => Math.hypot(q[0] - p.x, q[1] - p.y) < R + (s.w || 6) / 2)) { arr.splice(k, 1); changed = true; }
    }
    if (changed) { renderInk(); persist(); sendInk(); }
  }
  function undo() { const a = S.ink[inkKey()]; if (a && a.length) { (redo[inkKey()] = redo[inkKey()] || []).push(a.pop()); renderInk(); persist(); sendInk(); } }
  function redoInk() { const r = redo[inkKey()]; if (r && r.length) { strokesFor(inkKey()).push(r.pop()); renderInk(); persist(); sendInk(); } }
  function clearInk() { const a = S.ink[inkKey()]; if (a && a.length) { redo[inkKey()] = a.slice().reverse(); S.ink[inkKey()] = []; renderInk(); persist(); sendInk(); toast('Trazos eliminados (Ctrl+Z para recuperar uno a uno)'); } }
  function sendInk() { send({ type: 'ink', key: inkKey(), strokes: S.ink[inkKey()] || [] }); }
  if (ink) {
    ink.addEventListener('pointerdown', inkDown);
    ink.addEventListener('pointermove', inkMove);
    ink.addEventListener('pointerup', inkUp);
    ink.addEventListener('pointercancel', inkUp);
    ink.style.touchAction = 'none';
  }
  function setColor(c) { color = c; S.prefs.color = c; persist(); $$('#swatches .swatch').forEach(b => b.classList.toggle('on', b.dataset.c === c)); }
  (function swatches() {
    const box = $('#swatches'); if (!box) return;
    COLORS.forEach((c, k) => { const b = document.createElement('button'); b.className = 'swatch draw-only'; b.dataset.c = c; b.style.background = c; b.title = 'Color ' + (k + 1); b.type = 'button'; b.addEventListener('click', () => setColor(c)); box.appendChild(b); });
    setColor(color);
  })();
  function toggleBoard(on) {
    board = on === undefined ? !board : on;
    document.body.classList.toggle('white', board);
    if (board && (!tool || DRAW.indexOf(tool) < 0)) setTool('pen');
    renderInk(); send({ type: 'cover', black: document.body.classList.contains('black'), white: board });
  }
  function toggleBlack(on) {
    const v = on === undefined ? !document.body.classList.contains('black') : on;
    document.body.classList.toggle('black', v);
    send({ type: 'cover', black: v, white: board });
  }

  /* ---- Puntero sobre el viewport: láser, foco, lupa, comentarios, swipe ---- */
  const spot = $('#spot');
  let swipe = null;
  viewport.addEventListener('pointermove', e => {
    if (tool === 'laser') { const p = clientToStage(e.clientX, e.clientY); laserPoint(p.x, p.y); send({ type: 'laser', x: p.x, y: p.y }); }
  });
  addEventListener('pointermove', e => {
    if (tool === 'spot' && spot) { spot.style.setProperty('--x', e.clientX + 'px'); spot.style.setProperty('--y', e.clientY + 'px'); spot.style.setProperty('--r', Math.round(170 * (T.base || 1) * 1.6) + 'px'); }
    wake();
  });
  viewport.addEventListener('pointerdown', e => {
    if (!tool) swipe = { x: e.clientX, y: e.clientY, t: Date.now() };
  });
  viewport.addEventListener('pointerup', e => {
    if (swipe && !tool && e.pointerType !== 'mouse') {
      const dx = e.clientX - swipe.x, dy = e.clientY - swipe.y;
      if (Math.abs(dx) > 70 && Math.abs(dy) < 80 && Date.now() - swipe.t < 800) { dx < 0 ? next() : prev(); }
    }
    swipe = null;
  });
  viewport.addEventListener('click', e => {
    if (tool === 'zoom') { if (zoom.on) setZoom(false); else { const p = clientToStage(e.clientX, e.clientY); setZoom(true, p.x, p.y); } }
  });
  viewport.addEventListener('wheel', e => { if (zoom.on) { e.preventDefault(); zoom.k = Math.max(1.25, Math.min(4, zoom.k * (e.deltaY < 0 ? 1.1 : 0.9))); applyTransform(); } }, { passive: false });

  /* ---------------- Resaltado de texto seleccionado ---------------- */
  const markBtn = $('#markbtn');
  function hideMarkBtn() { if (markBtn) markBtn.style.display = 'none'; }
  function selectionInSlide() {
    const sel = getSelection(); if (!sel || sel.isCollapsed || !sel.rangeCount) return null;
    const r = sel.getRangeAt(0); const sl = slides[cur];
    if (!sl.contains(r.commonAncestorContainer)) return null;
    return r;
  }
  document.addEventListener('mouseup', () => setTimeout(() => {
    if (tool) return; const r = selectionInSlide(); if (!r || !markBtn) { hideMarkBtn(); return; }
    const b = r.getBoundingClientRect();
    markBtn.style.left = Math.min(innerWidth - 140, Math.max(8, b.left + b.width / 2 - 55)) + 'px';
    markBtn.style.top = Math.min(innerHeight - 50, b.bottom + 10) + 'px';
    markBtn.style.display = 'block';
  }, 0));
  if (markBtn) { markBtn.addEventListener('mousedown', e => e.preventDefault()); markBtn.addEventListener('click', markSelection); }
  function markSelection() {
    const r = selectionInSlide(); if (!r) { hideMarkBtn(); return; }
    const m = document.createElement('mark'); m.className = 'hl';
    try { r.surroundContents(m); } catch (e) { const f = r.extractContents(); m.appendChild(f); r.insertNode(m); }
    getSelection().removeAllRanges(); hideMarkBtn(); saveSlideHtml(slides[cur]); toast('Texto resaltado');
  }
  function saveSlideHtml(sl) {
    const c = sl.cloneNode(true);
    $$('[contenteditable]', c).forEach(e => e.removeAttribute('contenteditable'));
    $$('.frag', c).forEach(e => e.classList.remove('visible', 'dim'));
    S.html[sl.dataset.id] = c.innerHTML; persist();
  }

  /* ---------------- Edición en vivo ---------------- */
  let editing = false;
  function setEditing(on) {
    editing = on === undefined ? !editing : on;
    if (editing && tool) setTool(null);
    document.body.classList.toggle('editing', editing);
    $$('[data-edit]', stage).forEach(el => { if (editing) el.setAttribute('contenteditable', 'true'); else el.removeAttribute('contenteditable'); });
    const badge = $('#badge-mode'); if (badge) badge.textContent = 'Modo edición · Esc para salir';
    $$('#hud [data-act="edit"]').forEach(b => b.classList.toggle('on', editing));
    if (!editing) { slides.forEach(sl => { if (sl._dirty) { saveSlideHtml(sl); sl._dirty = false; } }); if (document.activeElement) document.activeElement.blur(); }
    toast(editing ? 'Edición activada: haz clic en un texto' : 'Cambios guardados');
  }
  let editT;
  stage.addEventListener('input', e => { const sl = e.target.closest && e.target.closest('section.slide'); if (!sl) return; sl._dirty = true; clearTimeout(editT); editT = setTimeout(() => { saveSlideHtml(sl); sl._dirty = false; }, 500); });
  stage.addEventListener('paste', e => { if (!editing) return; e.preventDefault(); const t = (e.clipboardData || window.clipboardData).getData('text'); document.execCommand('insertText', false, t); });

  /* ---------------- Comentarios anclados ---------------- */
  const pinsLayer = $('#comments');
  let pop = null;
  const author = () => S.prefs.author || CFG.author || 'Yo';
  function commentsFor(id) { return S.comments[id] || (S.comments[id] = []); }
  function renderPins() {
    if (!pinsLayer) return;
    pinsLayer.innerHTML = '';
    commentsFor(sid(cur)).forEach((c, k) => {
      const p = document.createElement('div'); p.className = 'pin' + (c.resolved ? ' resolved' : ''); p.style.left = c.x + 'px'; p.style.top = c.y + 'px';
      p.innerHTML = '<b>' + (k + 1) + '</b>'; p.title = c.text;
      p.addEventListener('click', ev => { ev.stopPropagation(); openPop(c); });
      pinsLayer.appendChild(p);
    });
    renderCommentList();
  }
  function closePop() { if (pop) { pop.remove(); pop = null; } }
  function placePop(el, x, y) {
    const c = stageToClient(x, y); document.body.appendChild(el);
    const w = el.offsetWidth || 520, h = el.offsetHeight || 220;
    el.style.left = Math.max(8, Math.min(innerWidth - w - 8, c.x + 16)) + 'px';
    el.style.top = Math.max(8, Math.min(innerHeight - h - 8, c.y - h / 2)) + 'px';
  }
  function openPop(c, isNew) {
    closePop();
    pop = document.createElement('div'); pop.className = 'pin-pop'; pop.style.position = 'fixed'; pop.style.zIndex = 960;
    if (isNew) {
      pop.innerHTML = '<div class="meta">Nuevo comentario · ' + esc(author()) + '</div><textarea placeholder="Escribe tu comentario…"></textarea><div class="row"><button class="ghost" data-x="cancel" type="button">Cancelar</button><button data-x="ok" type="button">Guardar</button></div>';
    } else {
      const d = new Date(c.ts);
      pop.innerHTML = '<div class="meta">' + esc(c.author) + ' · ' + d.toLocaleString(LANG) + (c.resolved ? ' · Resuelto' : '') + '</div><div style="white-space:pre-wrap">' + esc(c.text) + '</div><div class="row"><button class="ghost" data-x="del" type="button">Eliminar</button><button class="ghost" data-x="res" type="button">' + (c.resolved ? 'Reabrir' : 'Resolver') + '</button><button data-x="close" type="button">Cerrar</button></div>';
    }
    placePop(pop, c.x, c.y);
    const ta = $('textarea', pop); if (ta) setTimeout(() => ta.focus(), 30);
    pop.addEventListener('keydown', e => { e.stopPropagation(); if (e.key === 'Escape') closePop(); if (e.key === 'Enter' && (e.ctrlKey || e.metaKey) && ta) $('[data-x="ok"]', pop).click(); });
    pop.addEventListener('click', e => {
      const b = e.target.closest('button'); if (!b) return;
      const arr = commentsFor(sid(cur));
      if (b.dataset.x === 'ok') { const t = ta.value.trim(); if (t) { arr.push({ id: 'c' + Date.now(), x: Math.round(c.x), y: Math.round(c.y), text: t, author: author(), ts: Date.now(), resolved: false }); persist(); toast('Comentario guardado'); } closePop(); setTool(null); renderPins(); }
      else if (b.dataset.x === 'cancel' || b.dataset.x === 'close') closePop();
      else if (b.dataset.x === 'res') { c.resolved = !c.resolved; persist(); closePop(); renderPins(); }
      else if (b.dataset.x === 'del') { const k = arr.indexOf(c); if (k >= 0) arr.splice(k, 1); persist(); closePop(); renderPins(); }
    });
  }
  if (pinsLayer) pinsLayer.addEventListener('click', e => { if (tool !== 'comment' || e.target !== pinsLayer) return; const p = clientToStage(e.clientX, e.clientY); openPop({ x: p.x, y: p.y }, true); });
  function renderCommentList() {
    const box = $('#comment-list'); if (!box) return;
    let html = '';
    slides.forEach((sl, i) => (S.comments[sl.dataset.id] || []).forEach((c, k) => {
      html += '<div class="c-item' + (c.resolved ? ' resolved' : '') + '" data-i="' + i + '" data-k="' + k + '"><small>Slide ' + (i + 1) + ' · #' + (k + 1) + ' · ' + esc(c.author) + (c.resolved ? ' · resuelto' : '') + '</small>' + esc(c.text) + '</div>';
    }));
    box.innerHTML = html || '<p class="slide-ref">Aún no hay comentarios. Usa Shift+C o el botón para agregar uno sobre la slide.</p>';
  }
  const clist = $('#comment-list');
  if (clist) clist.addEventListener('click', e => { const it = e.target.closest('.c-item'); if (!it) return; const i = +it.dataset.i, k = +it.dataset.k; goto(i, 'last'); setTimeout(() => { const c = (S.comments[sid(i)] || [])[k]; if (c) openPop(c); }, 350); });

  /* ---------------- Panel de notas ---------------- */
  const notesInput = $('#notes-input');
  function syncNotesPanel() {
    const ref = $('#notes-ref'); if (ref) ref.textContent = 'Slide ' + (cur + 1) + ' · ' + titleOf(cur);
    if (notesInput && document.activeElement !== notesInput) notesInput.value = S.notes[sid(cur)] || '';
  }
  if (notesInput) notesInput.addEventListener('input', () => { S.notes[sid(cur)] = notesInput.value; persist(); });
  function togglePanel(tab) {
    const open = !document.body.classList.contains('panel-open') || (tab && !$('#panel .tab.on[data-tab="' + tab + '"]'));
    document.body.classList.toggle('panel-open', open);
    if (tab) selectTab(tab);
    if (open) { syncNotesPanel(); renderCommentList(); if (notesInput && (!tab || tab === 'notes')) setTimeout(() => notesInput.focus(), 200); }
    else if (document.activeElement) document.activeElement.blur();
  }
  function selectTab(t) { $$('#panel [data-tab]').forEach(el => el.classList.toggle('on', el.dataset.tab === t)); }
  $$('#panel header [data-tab]').forEach(b => b.addEventListener('click', () => selectTab(b.dataset.tab)));
  function minuteMd() {
    const d = new Date();
    let md = '# ' + (CFG.title || document.title) + '\n\n_Minuta generada el ' + d.toLocaleString(LANG) + '_\n\n';
    slides.forEach((sl, i) => {
      const id = sl.dataset.id, n = (S.notes[id] || '').trim(), cs = S.comments[id] || [], k = (S.ink[id] || []).length;
      if (!n && !cs.length && !k) return;
      md += '## ' + (i + 1) + '. ' + titleOf(i) + '\n\n';
      if (n) md += n + '\n\n';
      if (cs.length) { md += '**Comentarios**\n\n'; cs.forEach(c => { md += '- [' + (c.resolved ? 'x' : ' ') + '] ' + c.text.replace(/\n/g, ' ') + ' — _' + c.author + ', ' + new Date(c.ts).toLocaleString(LANG) + '_\n'; }); md += '\n'; }
      if (k) md += '_Anotaciones a mano alzada: ' + k + '_\n\n';
    });
    if ((S.ink.__board__ || []).length) md += '## Pizarra\n\n_Trazos en pizarra: ' + S.ink.__board__.length + '_\n';
    return md;
  }
  function fileBase() { return (CFG.fileName || 'presentacion').replace(/[<>:"/\\|?*]+/g, '-'); }

  /* ---------------- Guardar como HTML ---------------- */
  function saveHtml() {
    slides.forEach(sl => { if (sl._dirty) { saveSlideHtml(sl); sl._dirty = false; } });
    S.ts = Date.now();
    const doc = document.documentElement.cloneNode(true);
    const body = doc.querySelector('body'); body.className = 'deck'; body.removeAttribute('style');
    $$('[contenteditable]', doc).forEach(e => e.removeAttribute('contenteditable'));
    $$('#stage > section.slide', doc).forEach(e => e.classList.remove('active', 'no-vt'));
    $$('.frag', doc).forEach(e => e.classList.remove('visible', 'dim'));
    ['#stage', '#progress', '#markbtn', '#spot'].forEach(s => { const el = doc.querySelector(s); if (el) el.removeAttribute('style'); });
    ['#overview .grid', '#pv .mini', '#comments'].forEach(s => { const el = doc.querySelector(s); if (el) el.innerHTML = ''; });
    $$('.pin-pop', doc).forEach(e => e.remove());
    const st = doc.querySelector('#deck-state'); if (st) st.textContent = JSON.stringify(S).replace(/</g, '\\u003c');
    download(fileBase() + '-editada.html', '<!doctype html>\n' + doc.outerHTML, 'text/html;charset=utf-8');
    toast('Descargado: incluye ediciones, trazos, notas y comentarios');
  }

  /* ---------------- Vista general ---------------- */
  const ov = $('#overview');
  let ovSel = 0;
  function miniClone(sl) {
    const c = sl.cloneNode(true); c.classList.add('active', 'all-visible'); c.classList.remove('no-vt');
    $$('.frag', c).forEach(e => e.classList.add('visible'));
    $$('[contenteditable]', c).forEach(e => e.removeAttribute('contenteditable'));
    return c;
  }
  function openOverview() {
    const grid = $('.grid', ov); grid.innerHTML = '';
    slides.forEach((sl, i) => {
      const t = document.createElement('div'); t.className = 'thumb' + (i === cur ? ' current' : ''); t.tabIndex = 0; t.dataset.i = i;
      const m = document.createElement('div'); m.className = 'mini'; m.appendChild(miniClone(sl));
      t.appendChild(m); t.insertAdjacentHTML('beforeend', '<span class="num">' + (i + 1) + ' · ' + esc(titleOf(i)) + '</span>');
      t.addEventListener('click', () => { closeOverlays(); goto(i, 0); });
      grid.appendChild(t);
    });
    ov.classList.add('on'); ovSel = cur;
    requestAnimationFrame(() => { $$('.thumb', grid).forEach(t => { $('.mini', t).style.transform = 'scale(' + (t.clientWidth / W) + ')'; }); const c = $('.thumb.current', grid); if (c) { c.scrollIntoView({ block: 'center' }); c.focus(); } });
  }
  function moveOv(d) { const th = $$('#overview .thumb'); if (!th.length) return; const cols = Math.max(1, Math.round($('#overview .grid').clientWidth / (th[0].clientWidth + 24))); const step2 = Math.abs(d) === 2 ? cols : 1; ovSel = Math.max(0, Math.min(th.length - 1, ovSel + Math.sign(d) * step2)); th[ovSel].focus(); }

  /* ---------------- Paleta de comandos ---------------- */
  const pal = $('#palette'), palIn = $('#palette-input');
  const COMMANDS = [
    ['Pantalla completa', () => toggleFS()], ['Vista general', () => openOverview()], ['Vista del presentador', () => openPresenter()],
    ['Puntero láser', () => setTool('laser')], ['Foco', () => setTool('spot')], ['Lupa', () => setTool('zoom')], ['Lápiz', () => setTool('pen')], ['Resaltador', () => setTool('hl')],
    ['Pizarra en blanco', () => toggleBoard()], ['Pantalla negra', () => toggleBlack()], ['Editar textos', () => setEditing()], ['Notas y comentarios', () => togglePanel('notes')],
    ['Nuevo comentario', () => setTool('comment')], ['Exportar minuta (.md)', () => download(fileBase() + '-minuta.md', minuteMd(), 'text/markdown;charset=utf-8')],
    ['Guardar como HTML', () => saveHtml()], ['Imprimir / PDF', () => window.print()], ['Sonido on/off', () => toggleSound()], ['Ayuda: atajos', () => openHelp()],
    ['Restablecer anotaciones locales', () => { if (resetConfirm()) { S.ink = {}; S.notes = {}; S.comments = {}; S.html = {}; persist(); try { localStorage.removeItem(KEY); } catch (e) { } location.reload(); } }]
  ];
  let resetArmed = 0;
  function resetConfirm() { if (Date.now() - resetArmed < 4000) return true; resetArmed = Date.now(); toast('Repite el comando para confirmar'); return false; }
  let palItems = [], palSel = 0;
  function openPalette() { pal.classList.add('on'); palIn.value = ''; renderPal(); setTimeout(() => palIn.focus(), 20); }
  function renderPal() {
    const q = norm(palIn.value);
    palItems = slides.map((s, i) => ({ label: titleOf(i), tag: String(i + 1), run: () => goto(i, 0) })).concat(COMMANDS.map(c => ({ label: c[0], tag: '⌘', run: c[1] })))
      .filter(it => !q || norm(it.label).includes(q) || it.tag === q);
    palSel = 0;
    $('ul', pal).innerHTML = palItems.slice(0, 40).map((it, k) => '<li data-k="' + k + '"' + (k === 0 ? ' class="sel"' : '') + '><small>' + esc(it.tag) + '</small>' + esc(it.label) + '</li>').join('');
  }
  if (palIn) {
    palIn.addEventListener('input', renderPal);
    palIn.addEventListener('keydown', e => {
      e.stopPropagation();
      const lis = $$('li', pal);
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); palSel = Math.max(0, Math.min(lis.length - 1, palSel + (e.key === 'ArrowDown' ? 1 : -1))); lis.forEach((l, k) => l.classList.toggle('sel', k === palSel)); }
      else if (e.key === 'Enter') { const it = palItems[palSel]; closeOverlays(); if (it) it.run(); }
      else if (e.key === 'Escape') closeOverlays();
    });
    $('ul', pal).addEventListener('click', e => { const li = e.target.closest('li'); if (!li) return; const it = palItems[+li.dataset.k]; closeOverlays(); if (it) it.run(); });
  }

  /* ---------------- Ayuda ---------------- */
  const KEYS = [
    ['→ Espacio PgDn', 'Siguiente'], ['← PgUp', 'Anterior'], ['Inicio / Fin', 'Primera / última'], ['nº + Enter', 'Ir a slide'],
    ['F', 'Pantalla completa'], ['O', 'Vista general'], ['S', 'Vista del presentador'], ['G / Ctrl+K', 'Buscar slide o comando'],
    ['L', 'Puntero láser'], ['H', 'Foco'], ['Z', 'Lupa (clic)'], ['D', 'Lápiz'], ['Shift+D', 'Resaltador'], ['1–5', 'Color (dibujando)'],
    ['X', 'Borrador'], ['C', 'Limpiar trazos de la slide'], ['Ctrl+Z / Ctrl+Y', 'Deshacer / rehacer trazo'], ['W', 'Pizarra en blanco'], ['B  .', 'Pantalla negra'],
    ['Seleccionar texto', 'Botón Resaltar (Shift+M)'], ['Shift+C', 'Comentario anclado'], ['T', 'Notas y comentarios'], ['E', 'Editar textos'],
    ['Ctrl+S', 'Guardar como HTML'], ['Ctrl+P', 'Imprimir / PDF'], ['U', 'Sonido'], ['A', 'Avance automático'], ['Esc', 'Salir de herramienta / panel'], ['?', 'Esta ayuda']
  ];
  function openHelp() { $('#help-list').innerHTML = KEYS.map(k => '<div class="k"><span>' + esc(k[1]) + '</span><kbd>' + esc(k[0]) + '</kbd></div>').join(''); $('#help').classList.add('on'); }
  function closeOverlays() { let any = false; $$('.overlay.on').forEach(o => { o.classList.remove('on'); any = true; }); return any; }

  /* ---------------- Pantalla completa ---------------- */
  let wakeLock = null;
  function toggleFS() {
    const d = document, el = d.documentElement;
    if (d.fullscreenElement || d.webkitFullscreenElement) { (d.exitFullscreen || d.webkitExitFullscreen).call(d); }
    else { const req = el.requestFullscreen || el.webkitRequestFullscreen; if (req) { const p = req.call(el); if (p && p.catch) p.catch(() => toast('Pantalla completa no disponible')); } else toast('Pantalla completa no disponible'); }
  }
  document.addEventListener('fullscreenchange', async () => {
    setTimeout(fit, 60);
    try { if (document.fullscreenElement && navigator.wakeLock) wakeLock = await navigator.wakeLock.request('screen'); else if (wakeLock) { wakeLock.release(); wakeLock = null; } } catch (e) { }
  });

  /* ---------------- Sonido (Web Audio sintetizado) ---------------- */
  let AC = null, master = null;
  function audio() { if (!AC) { const C = window.AudioContext || window.webkitAudioContext; if (!C) return null; AC = new C(); master = AC.createGain(); master.gain.value = 0.22; master.connect(AC.destination); } if (AC.state === 'suspended') AC.resume(); return AC; }
  function tone(f, dur, type, vol, slideTo, delay) {
    const a = audio(); if (!a) return; const t = a.currentTime + (delay || 0);
    const o = a.createOscillator(), g = a.createGain(); o.type = type || 'sine'; o.frequency.setValueAtTime(f, t);
    if (slideTo) o.frequency.exponentialRampToValueAtTime(slideTo, t + dur);
    g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(vol || 0.4, t + 0.01); g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    o.connect(g).connect(master); o.start(t); o.stop(t + dur + 0.05);
  }
  function whoosh(dur) {
    const a = audio(); if (!a) return; dur = dur || 0.45;
    const b = a.createBuffer(1, Math.floor(a.sampleRate * dur), a.sampleRate), d = b.getChannelData(0);
    for (let k = 0; k < d.length; k++) d[k] = (Math.random() * 2 - 1) * Math.sin(Math.PI * k / d.length);
    const s = a.createBufferSource(), f = a.createBiquadFilter(), t = a.currentTime; f.type = 'bandpass'; f.Q.value = 0.8;
    f.frequency.setValueAtTime(300, t); f.frequency.exponentialRampToValueAtTime(2800, t + dur); s.buffer = b; s.connect(f).connect(master); s.start();
  }
  const SFX = {
    tick: () => tone(1250, 0.05, 'sine', 0.18), pop: () => tone(620, 0.1, 'triangle', 0.35, 180), ding: () => { tone(1318, 0.7, 'sine', 0.3); tone(1976, 0.5, 'sine', 0.12); },
    whoosh: () => whoosh(), rise: () => tone(280, 0.4, 'sawtooth', 0.07, 1200),
    success: () => { tone(784, 0.18, 'triangle', 0.3); tone(988, 0.18, 'triangle', 0.3, null, 0.12); tone(1319, 0.4, 'triangle', 0.3, null, 0.24); },
    error: () => { tone(220, 0.25, 'square', 0.12); tone(185, 0.3, 'square', 0.1, null, 0.12); }
  };
  function sfx(name) { if (!S.prefs.sound || PRESENTER) return; try { (SFX[name] || SFX.tick)(); } catch (e) { } }
  function toggleSound() {
    S.prefs.sound = !S.prefs.sound; persist(); if (S.prefs.sound) { audio(); SFX.tick(); }
    const b = $('#hud [data-act="sound"]'); if (b && CFG.uiIcons) b.innerHTML = S.prefs.sound ? CFG.uiIcons.soundOn : CFG.uiIcons.soundOff;
    toast(S.prefs.sound ? 'Sonido activado' : 'Sonido desactivado');
  }

  /* ---------------- Quiz ---------------- */
  function answerQuiz(btn) {
    const sl = btn.closest('section.slide'); if (!sl || sl.dataset.answered) return;
    sl.dataset.answered = '1';
    const ok = btn.dataset.correct === '1';
    btn.classList.add(ok ? 'correct' : 'wrong');
    if (!ok) $$('.quiz-opt[data-correct="1"]', sl).forEach(b => b.classList.add('correct'));
    const fb = $('.quiz-feedback', sl); if (fb) fb.classList.add('show');
    if (ok) { S.score = (S.score || 0) + (CFG.quizPoints || 10); persist(); }
    sfx(ok ? 'success' : 'error');
    toast(ok ? '¡Correcto! +' + (CFG.quizPoints || 10) + ' pts · Total ' + S.score : 'Casi… revisa la explicación');
  }
  stage.addEventListener('click', e => { const b = e.target.closest && e.target.closest('.quiz-opt'); if (b && !tool && !editing) answerQuiz(b); });

  /* ---------------- Vista del presentador ---------------- */
  let pw = null; const t0 = Date.now(); let tStart = Date.now();
  function openPresenter() {
    if (PRESENTER) return;
    const url = location.href.split('#')[0].split('?')[0] + '?presenter=1#/' + (cur + 1) + '/' + step;
    pw = window.open(url, 'deck-presenter-' + (CFG.id || 'x'), 'width=1400,height=860');
    if (!pw) toast('Permite ventanas emergentes para la vista del presentador');
  }
  function send(msg) {
    msg.__deck = CFG.id || 'deck';
    const target = PRESENTER ? window.opener : pw;
    if (target && !target.closed) { try { target.postMessage(msg, '*'); } catch (e) { } }
  }
  addEventListener('message', e => {
    const d = e.data; if (!d || d.__deck !== (CFG.id || 'deck')) return;
    if (!PRESENTER && e.source && e.source !== window) pw = e.source;
    if (d.type === 'hello') { send({ type: 'goto', i: cur, step: step }); return; }
    if (d.type === 'goto') { if (d.i !== cur) goto(d.i, d.step, { silent: true }); else if (d.step !== step) setStep(d.step, { silent: true }); updatePresenter(); }
    else if (d.type === 'laser') laserPoint(d.x, d.y);
    else if (d.type === 'ink') { S.ink[d.key] = d.strokes || []; if (d.key === inkKey()) renderInk(); persist(); }
    else if (d.type === 'cover') { document.body.classList.toggle('black', !!d.black); board = !!d.white; document.body.classList.toggle('white', board); renderInk(); }
  });
  const pvFs = () => parseInt(S.prefs.pvFs || 22, 10);
  function updatePresenter() {
    if (!PRESENTER) return;
    const nx = $('#pv .next .mini'), lbl = $('#pv .next .lbl');
    if (nx) { nx.innerHTML = ''; const g = groupsOf(slides[cur]); if (step < g.length) { const c = miniClone(slides[cur]); nx.appendChild(c); lbl.textContent = 'Siguiente: fragmento ' + (step + 1) + ' de ' + g.length; } else if (cur < N - 1) { nx.appendChild(miniClone(slides[cur + 1])); lbl.textContent = 'Siguiente: ' + (cur + 2) + ' · ' + titleOf(cur + 1); } else lbl.textContent = 'Fin de la presentación'; const box = $('#pv .next'); nx.style.transform = 'scale(' + (box.clientWidth / W) + ')'; }
    const notes = $('.notes', slides[cur]);
    const pn = $('#pv-notes'); if (pn) { pn.style.setProperty('--pv-fs', pvFs() + 'px'); pn.innerHTML = '<div class="t">Notas · slide ' + (cur + 1) + ' de ' + N + ' · ' + esc(titleOf(cur)) + '</div>' + (notes && notes.innerHTML.trim() ? notes.innerHTML : '<em>Sin notas para esta slide.</em>'); }
  }
  function tickClock() {
    if (!PRESENTER) return;
    const el = (Date.now() - tStart) / 1000; const mm = String(Math.floor(el / 60)).padStart(2, '0'), ss = String(Math.floor(el % 60)).padStart(2, '0');
    const e1 = $('#pv-elapsed'); if (e1) e1.textContent = mm + ':' + ss;
    const now = $('#pv-now'); if (now) now.textContent = new Date().toLocaleTimeString(LANG, { hour: '2-digit', minute: '2-digit' });
    const plan = slides.slice(0, cur + 1).reduce((a, sl) => a + (parseFloat(sl.dataset.timing) || 0), 0);
    const pace = $('#pv-pace');
    if (pace) { if (plan > 0) { const diff = Math.round(el - plan); pace.className = 'pace ' + (diff > 30 ? 'late' : diff < -60 ? 'early' : 'ok'); pace.textContent = 'Ritmo ' + (diff > 0 ? '+' : '−') + Math.floor(Math.abs(diff) / 60) + ':' + String(Math.abs(diff) % 60).padStart(2, '0'); } else pace.textContent = ''; }
  }
  if (PRESENTER) {
    document.body.classList.add('presenter');
    document.title = 'Presentador · ' + document.title;
    setInterval(tickClock, 1000);
    const r = $('#pv-reset'); if (r) r.addEventListener('click', () => { tStart = Date.now(); tickClock(); });
    const fm = $('#pv-fminus'), fp = $('#pv-fplus');
    if (fm) fm.addEventListener('click', () => { S.prefs.pvFs = Math.max(14, pvFs() - 2); persist(); updatePresenter(); });
    if (fp) fp.addEventListener('click', () => { S.prefs.pvFs = Math.min(44, pvFs() + 2); persist(); updatePresenter(); });
    addEventListener('resize', updatePresenter);
  }

  /* ---------------- Autoavance ---------------- */
  let autoT = null;
  function toggleAuto() { if (autoT) { clearInterval(autoT); autoT = null; toast('Avance automático detenido'); } else { autoT = setInterval(() => { if (cur >= N - 1 && step >= groupsOf(slides[cur]).length) { clearInterval(autoT); autoT = null; } else next(); }, (CFG.autoplaySec || 8) * 1000); toast('Avance automático cada ' + (CFG.autoplaySec || 8) + ' s'); } }

  /* ---------------- HUD ---------------- */
  let idleT;
  function wake() { document.body.classList.remove('idle'); clearTimeout(idleT); if (!PRESENTER) idleT = setTimeout(() => { if (!document.body.classList.contains('panel-open') && !$('.overlay.on')) document.body.classList.add('idle'); }, 2600); }
  const ACTS = {
    prev: prev, next: next, undo: undo, clear: clearInk, panel: () => togglePanel(), edit: () => setEditing(), overview: openOverview, presenter: openPresenter,
    sound: toggleSound, fullscreen: toggleFS, save: saveHtml, help: openHelp, 'comment-mode': () => setTool('comment'),
    'export-md': () => download(fileBase() + '-minuta.md', minuteMd(), 'text/markdown;charset=utf-8'), 'copy-md': () => copyText(minuteMd())
  };
  document.addEventListener('click', e => {
    const b = e.target.closest && e.target.closest('[data-act],[data-tool]'); if (!b || !(b.closest('#hud') || b.closest('#panel'))) return;
    if (b.dataset.tool) setTool(b.dataset.tool); else if (ACTS[b.dataset.act]) ACTS[b.dataset.act]();
  });

  /* ---------------- Teclado ---------------- */
  let numBuf = '', numT;
  document.addEventListener('keydown', e => {
    const tg = e.target, k = e.key, mod = e.ctrlKey || e.metaKey;
    const typing = tg && (tg.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(tg.tagName));
    if (mod && (k === 's' || k === 'S')) { e.preventDefault(); saveHtml(); return; }
    if (typing) { if (k === 'Escape') { if (editing) setEditing(false); else tg.blur(); } return; }
    if ($('.overlay.on')) {
      if (k === 'Escape' || k === 'o' || k === 'O' || k === '?') { e.preventDefault(); closeOverlays(); return; }
      if ($('#overview.on')) { if (k === 'ArrowRight') moveOv(1); else if (k === 'ArrowLeft') moveOv(-1); else if (k === 'ArrowDown') moveOv(2); else if (k === 'ArrowUp') moveOv(-2); else if (k === 'Enter') { const th = $$('#overview .thumb')[ovSel]; if (th) th.click(); } e.preventDefault(); }
      return;
    }
    if (mod && (k === 'k' || k === 'K')) { e.preventDefault(); openPalette(); return; }
    if (mod && (k === 'z' || k === 'Z')) { e.preventDefault(); if (e.shiftKey) redoInk(); else undo(); return; }
    if (mod && (k === 'y' || k === 'Y')) { e.preventDefault(); redoInk(); return; }
    if (mod || e.altKey) return;
    wake();
    const drawing = tool && DRAW.indexOf(tool) >= 0;
    if (/^[0-9]$/.test(k)) {
      if (drawing && k >= '1' && k <= String(COLORS.length)) { setColor(COLORS[+k - 1]); return; }
      const sl = slides[cur];
      if (sl.classList.contains('t-quiz') && !sl.dataset.answered && k >= '1' && k <= '6') { const ops = $$('.quiz-opt', sl); if (ops[+k - 1]) { answerQuiz(ops[+k - 1]); return; } }
      numBuf += k; clearTimeout(numT); numT = setTimeout(() => { numBuf = ''; }, 1600); toast('Ir a slide ' + numBuf + ' · Enter'); return;
    }
    if (k === 'Enter' && numBuf) { goto(parseInt(numBuf, 10) - 1, 0); numBuf = ''; return; }
    switch (k) {
      case 'ArrowRight': case 'ArrowDown': case 'PageDown': case ' ': case 'n': case 'N': case 'Enter': e.preventDefault(); next(); break;
      case 'ArrowLeft': case 'ArrowUp': case 'PageUp': case 'p': case 'P': case 'Backspace': e.preventDefault(); prev(); break;
      case 'Home': e.preventDefault(); goto(0, 0); break;
      case 'End': e.preventDefault(); goto(N - 1, 'last'); break;
      case 'f': case 'F': case 'F5': e.preventDefault(); toggleFS(); break;
      case 'o': case 'O': openOverview(); break;
      case 's': if (!e.shiftKey) openPresenter(); break;
      case 'g': case 'G': e.preventDefault(); openPalette(); break;
      case 'l': case 'L': setTool('laser'); break;
      case 'h': case 'H': setTool('spot'); break;
      case 'z': case 'Z': setTool('zoom'); break;
      case 'd': setTool('pen'); break;
      case 'D': setTool('hl'); break;
      case 'x': case 'X': setTool('eraser'); break;
      case 'c': clearInk(); break;
      case 'C': setTool('comment'); break;
      case 'M': markSelection(); break;
      case 'w': case 'W': toggleBoard(); break;
      case 'b': case 'B': case '.': toggleBlack(); break;
      case 'e': case 'E': setEditing(); break;
      case 't': case 'T': e.preventDefault(); togglePanel('notes'); break;
      case 'u': case 'U': toggleSound(); break;
      case 'a': case 'A': toggleAuto(); break;
      case '?': openHelp(); break;
      case 'Escape':
        if (pop) { closePop(); break; }
        if (zoom.on) { setZoom(false); break; }
        if (tool) { setTool(null); break; }
        if (document.body.classList.contains('black')) { toggleBlack(false); break; }
        if (board) { toggleBoard(false); break; }
        if (document.body.classList.contains('panel-open')) { togglePanel(); break; }
        break;
    }
  });

  /* ---------------- Inicio ---------------- */
  fit();
  const h0 = readHash();
  goto(h0.i, h0.step, { instant: true, silent: true });
  wake();
  if (S.prefs.sound && CFG.uiIcons) { const b = $('#hud [data-act="sound"]'); if (b) b.innerHTML = CFG.uiIcons.soundOn; }
  if (PRESENTER) { setTimeout(() => { send({ type: 'hello' }); fit(); updatePresenter(); tickClock(); }, 120); }
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fit);

  /* API pública (QA, automatización, consola) */
  window.Deck = {
    get count() { return N; }, get index() { return cur; }, get step() { return step; },
    goto: (i, o) => goto(i, o && o.all ? 'last' : 0, Object.assign({ instant: true, silent: true }, o || {})),
    next: next, prev: prev, setTool: setTool, state: S, minute: minuteMd, version: CFG.version || ''
  };
})();
