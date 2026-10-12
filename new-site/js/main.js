/* FULLIN main: header, menu, anchors, reveal, parallax, battery, progress, nav highlight */
(function () {
  'use strict';
  var doc = document, root = doc.documentElement;
  var $ = function (s, c) { return (c || doc).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || doc).querySelectorAll(s)); };
  var mq = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : { matches: false };
  var reduced = function () { return mq.matches; };
  var T = function (k) { return window.FullinI18n ? window.FullinI18n.t(k) : k; };
  var saveData = !!(navigator.connection && (navigator.connection.saveData || /2g/.test(navigator.connection.effectiveType || '')));

  /* ---------- header scroll state ---------- */
  var header = $('#site-header');
  function onScrollHeader() { header.classList.toggle('is-scrolled', window.scrollY > 24); }
  onScrollHeader();

  /* ---------- mobile menu ---------- */
  var btn = $('#menu-btn'), menu = $('#site-menu');
  var desk = window.matchMedia('(min-width: 960px)');
  function focusables() {
    return $$('a[href], button:not([disabled])', menu).concat([btn, $('.brand', header)]).filter(function (e) { return e.offsetParent !== null || e === btn; });
  }
  function setMenu(open, restore) {
    btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    btn.setAttribute('aria-label', T(open ? btn.dataset.labelClose : btn.dataset.labelOpen));
    menu.classList.toggle('is-open', open);
    root.classList.toggle('menu-open', open);
    if (!desk.matches) { if (open) { menu.removeAttribute('inert'); } else { menu.setAttribute('inert', ''); } }
    if (!open && restore) btn.focus();
  }
  function syncMenuMode() { if (desk.matches) { menu.removeAttribute('inert'); setMenu(false); menu.removeAttribute('inert'); } else if (!menu.classList.contains('is-open')) menu.setAttribute('inert', ''); }
  btn.addEventListener('click', function () { setMenu(btn.getAttribute('aria-expanded') !== 'true'); if (btn.getAttribute('aria-expanded') === 'true') { var f = $('a, button', menu); f && f.focus(); } });
  doc.addEventListener('keydown', function (e) {
    if (btn.getAttribute('aria-expanded') !== 'true' || desk.matches) return;
    if (e.key === 'Escape') { setMenu(false, true); return; }
    if (e.key !== 'Tab') return;
    var all = focusables().sort(function (a, b) { return (a.compareDocumentPosition(b) & 4) ? -1 : 1; });
    // visual order: brand, button, then menu items (menu contents come after brand/btn in DOM, button is before menu)
    var first = all[0], last = all[all.length - 1];
    if (e.shiftKey && doc.activeElement === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && doc.activeElement === last) { e.preventDefault(); first.focus(); }
  });
  desk.addEventListener ? desk.addEventListener('change', syncMenuMode) : desk.addListener(syncMenuMode);
  syncMenuMode();
  doc.addEventListener('fullin:lang', function () { btn.setAttribute('aria-label', T(btn.getAttribute('aria-expanded') === 'true' ? btn.dataset.labelClose : btn.dataset.labelOpen)); });

  /* ---------- smooth anchors + focus management ---------- */
  doc.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href^="#"]');
    if (!a || e.defaultPrevented || e.metaKey || e.ctrlKey || e.shiftKey) return;
    var id = a.getAttribute('href').slice(1);
    if (!id) return;
    var tgt = doc.getElementById(id);
    if (!tgt) return;
    e.preventDefault();
    if (menu.classList.contains('is-open')) setMenu(false);
    var smooth = !reduced();
    if (id === 'top') window.scrollTo({ top: 0, behavior: smooth ? 'smooth' : 'auto' });
    else tgt.scrollIntoView({ behavior: smooth ? 'smooth' : 'auto', block: 'start' });
    try { history.pushState(null, '', location.pathname + location.search + '#' + id); } catch (er) {}
    var h = id === 'top' ? $('h1', tgt) : ($('h2, h1', tgt) || tgt);
    if (id === 'main') h = tgt;
    if (h) { if (!h.hasAttribute('tabindex')) h.setAttribute('tabindex', '-1'); setTimeout(function () { try { h.focus({ preventScroll: true }); } catch (er) { h.focus(); } }, smooth ? 600 : 0); }
  });

  /* ---------- reveal ---------- */
  var io;
  function observeReveal(scope) {
    var els = $$('.reveal:not(.is-in)', scope);
    if (!('IntersectionObserver' in window) || reduced()) { els.forEach(function (el) { el.classList.add('is-in'); }); return; }
    io = io || new IntersectionObserver(function (es) {
      es.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); if (en.target.querySelector('[data-count]')) counters(en.target); } });
    }, { threshold: .12, rootMargin: '0px 0px -6% 0px' });
    els.forEach(function (el) { io.observe(el); });
  }
  window.FullinReveal = observeReveal;
  observeReveal(doc);
  window.addEventListener('load', function () { observeReveal(doc); });

  /* number counters (step numbers) */
  function counters(scope) {
    $$('[data-count]', scope).forEach(function (el) {
      if (el.dataset.done || reduced()) return; el.dataset.done = 1;
      var span = el.firstElementChild || el, target = span.textContent, n = parseInt(target, 10);
      if (!n) return;
      var t0 = null, dur = 700 + n * 200, pad = /^0/.test(target);
      function f(t) { t0 = t0 || t; var p = Math.min(1, (t - t0) / dur), v = Math.round(n * (1 - Math.pow(1 - p, 3))); span.textContent = (pad && v < 10 ? '0' : '') + v; if (p < 1) requestAnimationFrame(f); else span.textContent = target; }
      requestAnimationFrame(f);
    });
  }

  /* ---------- hero: video, app link, parallax ---------- */
  var hero = $('#top');
  var app = $('#hero-app');
  if (app && /android/i.test(navigator.userAgent)) app.href = app.dataset.android;
  var vid = $('.hero__video');
  if (vid && desk.matches && !reduced() && !saveData) {
    vid.src = vid.dataset.src;
    vid.addEventListener('canplay', function () { vid.classList.add('is-on'); }, { once: true });
    var pl = function () { var p = vid.play(); p && p.catch && p.catch(function () {}); };
    pl();
    if ('IntersectionObserver' in window) new IntersectionObserver(function (es) { es[0].isIntersecting ? pl() : vid.pause(); }).observe(hero);
  }
  var px = $$('.px', hero);
  var tx = 0, ty = 0, cx = 0, cy = 0, raf = 0;
  function tick() {
    cx += (tx - cx) * .08; cy += (ty - cy) * .08;
    px.forEach(function (el) { var d = +el.dataset.depth || 10; el.style.transform = 'translate3d(' + (cx * d).toFixed(2) + 'px,' + (cy * d).toFixed(2) + 'px,0)'; });
    raf = (Math.abs(tx - cx) > .001 || Math.abs(ty - cy) > .001) ? requestAnimationFrame(tick) : 0;
  }
  if (window.matchMedia('(hover: hover) and (pointer: fine)').matches && !reduced()) {
    hero.addEventListener('mousemove', function (e) {
      var r = hero.getBoundingClientRect();
      tx = (e.clientX - r.left) / r.width - .5; ty = (e.clientY - r.top) / r.height - .5;
      if (!raf) raf = requestAnimationFrame(tick);
    });
    hero.addEventListener('mouseleave', function () { tx = ty = 0; if (!raf) raf = requestAnimationFrame(tick); });
  }

  /* ---------- battery counter ---------- */
  var bat = $('#bat');
  if (bat) (function () {
    var num = $('#bat-num'), fill = $('#bat-fill'), msg = $('#bat-msg'), live = $('#bat-live');
    var CLIMB = 4200, STALL = 2400, HOLD = 3800;
    var state = 'idle', t0 = 0, last = -1, announced = false, visible = true, timer = 0, rafId = 0;
    function set(v) {
      if (v === last) return; last = v;
      num.textContent = v;
      fill.style.transform = 'scaleX(' + (v / 100) + ')';
      var lv = v >= 100 ? 'full' : v >= 70 ? 'high' : v >= 30 ? 'mid' : 'low';
      if (bat.dataset.level !== lv) bat.dataset.level = lv;
    }
    function setState(s) { state = s; bat.dataset.state = s; }
    function punch() {
      setState('punch'); set(100); msg.textContent = T('hero.batteryPunch');
      if (!announced) { live.textContent = T('hero.batteryPunch'); announced = true; }
      timer = setTimeout(restart, HOLD);
    }
    function stall() { setState('stall'); set(99); msg.textContent = T('hero.batteryStall'); timer = setTimeout(punch, STALL); }
    function frame(t) {
      if (state !== 'climb') return;
      var p = Math.min(1, (t - t0) / CLIMB), e = 1 - Math.pow(1 - p, 2.2);
      set(Math.max(1, Math.min(99, Math.round(e * 99))));
      if (p < 1) rafId = requestAnimationFrame(frame); else stall();
    }
    function restart() {
      clearTimeout(timer); cancelAnimationFrame(rafId);
      if (!visible || doc.hidden) { setState('idle'); return; }
      setState('climb'); last = -1; set(1); msg.innerHTML = '&nbsp;';
      t0 = performance.now(); rafId = requestAnimationFrame(frame);
    }
    function pause() { clearTimeout(timer); cancelAnimationFrame(rafId); if (state === 'climb') setState('idle'); else if (state === 'stall' || state === 'punch') { var s = state; setState('paused-' + s); } }
    function resume() { if (/^paused|idle/.test(state)) restart(); }
    if (reduced()) { set(100); setState('punch'); msg.textContent = T('hero.batteryPunch'); live.textContent = T('hero.batteryPunch'); doc.addEventListener('fullin:lang', function () { msg.textContent = T('hero.batteryPunch'); live.textContent = T('hero.batteryPunch'); }); return; }
    if ('IntersectionObserver' in window) new IntersectionObserver(function (es) { visible = es[0].isIntersecting; visible ? resume() : pause(); }, { threshold: .2 }).observe(bat);
    doc.addEventListener('visibilitychange', function () { doc.hidden ? pause() : (visible && resume()); });
    doc.addEventListener('fullin:lang', function () { if (state === 'stall') msg.textContent = T('hero.batteryStall'); if (state === 'punch') { msg.textContent = T('hero.batteryPunch'); } if (announced) live.textContent = T('hero.batteryPunch'); });
    restart();
  })();

  /* ---------- scroll progress (how steps, price timeline) ---------- */
  var prog = $$('[data-progress]');
  var ticking = false;
  function progress() {
    var vh = window.innerHeight;
    prog.forEach(function (el) {
      var r = el.getBoundingClientRect();
      var horizontal = el.classList.contains('steps') && desk.matches || (el.classList.contains('ptl') && desk.matches);
      var p;
      if (horizontal) p = (vh * .85 - r.top) / (r.height + vh * .25);
      else p = (vh * .7 - r.top) / (r.height * .92);
      p = Math.max(0, Math.min(1, p));
      el.style.setProperty('--p', p.toFixed(3));
      var items = $$('.step, .pstep', el), n = items.length;
      items.forEach(function (it, i) { it.classList.toggle('is-on', p * 1.08 >= (i + .35) / n); });
    });
  }
  /* ---------- nav highlight ---------- */
  var links = $$('.nav-list a'), secs = [];
  links.forEach(function (a) { var s = doc.getElementById(a.getAttribute('href').slice(1)); if (s) secs.push([a, s]); });
  function highlight() {
    var y = window.innerHeight * .35, cur = null;
    secs.forEach(function (p) { var r = p[1].getBoundingClientRect(); if (r.top <= y && r.bottom > y) cur = p[0]; });
    links.forEach(function (a) { if (a === cur) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current'); });
  }
  function onScroll() { if (ticking) return; ticking = true; requestAnimationFrame(function () { ticking = false; onScrollHeader(); progress(); highlight(); }); }
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll);
  doc.addEventListener('fullin:lang', function () { setTimeout(onScroll, 50); });
  window.addEventListener('load', onScroll);
  onScroll();
})();
