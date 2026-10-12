/* FULLIN accessibility: pre-paint prefs + widget behaviour. Load in <head>, NOT deferred. */
(function () {
  'use strict';
  var KEY = 'fullin-a11y';
  var root = document.documentElement;
  var DEF = { font: 0, contrast: 0, gray: 0, links: 0, sysfont: 0, motion: 0, cursor: 0 };
  var prefs = {};
  var k;
  for (k in DEF) prefs[k] = DEF[k];

  function load() {
    try {
      var raw = localStorage.getItem(KEY);
      if (raw) {
        var o = JSON.parse(raw);
        for (k in DEF) if (typeof o[k] === 'number') prefs[k] = o[k];
      }
    } catch (e) {}
    prefs.font = Math.max(0, Math.min(3, prefs.font | 0));
  }
  function save() {
    try {
      var any = false;
      for (k in DEF) if (prefs[k]) any = true;
      if (any) localStorage.setItem(KEY, JSON.stringify(prefs));
      else localStorage.removeItem(KEY);
    } catch (e) {}
  }
  function setAttr(name, on, val) {
    if (on) root.setAttribute(name, val || '1');
    else root.removeAttribute(name);
  }
  var FONT_SCALE = [1, 1.12, 1.25, 1.4];
  function applyRoot() {
    setAttr('data-a11y-font', prefs.font, String(prefs.font));
    root.style.setProperty('--a11y-font-scale', FONT_SCALE[prefs.font]);
    setAttr('data-a11y-contrast', prefs.contrast);
    setAttr('data-a11y-gray', prefs.gray);
    setAttr('data-a11y-links', prefs.links);
    setAttr('data-a11y-sysfont', prefs.sysfont);
    setAttr('data-a11y-cursor', prefs.cursor);
    if (prefs.motion) root.setAttribute('data-motion', 'off');
    else root.removeAttribute('data-motion');
    syncMedia();
  }
  /* pause / resume videos and marquees */
  function syncMedia() {
    if (!document.body) return;
    var vids = document.querySelectorAll('video'), i, v;
    for (i = 0; i < vids.length; i++) {
      v = vids[i];
      if (prefs.motion) {
        if (!v.paused) { v.setAttribute('data-a11y-paused', '1'); try { v.pause(); } catch (e) {} }
      } else if (v.getAttribute('data-a11y-paused')) {
        v.removeAttribute('data-a11y-paused');
        try { var p = v.play(); if (p && p.catch) p.catch(function () {}); } catch (e) {}
      }
    }
    var ms = document.querySelectorAll('marquee');
    for (i = 0; i < ms.length; i++) { try { prefs.motion ? ms[i].stop() : ms[i].start(); } catch (e) {} }
  }

  load();
  applyRoot(); /* before first paint */

  /* ---------- widget ---------- */
  var FB_STATUS = 'גודל טקסט: {n} מתוך 3', FB_NORMAL = 'גודל טקסט: רגיל', FB_RESET = 'ההגדרות אופסו';

  function tr(key, fb) {
    try {
      if (window.FullinI18n && typeof window.FullinI18n.t === 'function') {
        var s = window.FullinI18n.t(key);
        if (typeof s === 'string' && s && s !== key) return s;
      }
    } catch (e) {}
    return fb;
  }

  function init() {
    syncMedia();
    var host = document.querySelector('[data-a11yw]');
    if (!host) return;
    var fab = host.querySelector('.a11yw__fab');
    var panel = host.querySelector('.a11yw__panel');
    var closeBtn = host.querySelector('.a11yw__close');
    var status = host.querySelector('[data-a11yw-status]');
    var toggles = host.querySelectorAll('[data-a11yw-toggle]');
    var sizeBtns = host.querySelectorAll('[data-a11yw-size]');
    var inerted = [];
    var open = false;
    var i;

    /* i18n */
    var tEls = host.querySelectorAll('[data-a11yw-t]');
    for (i = 0; i < tEls.length; i++) {
      var el = tEls[i], at = el.getAttribute('data-a11yw-attr');
      el._fb = at ? el.getAttribute(at) : (el.querySelector('[aria-hidden]') ? null : el.textContent);
    }
    function applyLang() {
      for (var j = 0; j < tEls.length; j++) {
        var e = tEls[j], a = e.getAttribute('data-a11yw-attr'), key = e.getAttribute('data-a11yw-t');
        if (a) e.setAttribute(a, tr(key, e._fb));
        else if (e._fb != null) e.textContent = tr(key, e._fb);
      }
      renderStatus();
    }

    function renderStatus(msg) {
      if (msg) { status.textContent = msg; return; }
      status.textContent = prefs.font
        ? tr('a11yw.sizeStatus', FB_STATUS).replace('{n}', prefs.font)
        : tr('a11yw.sizeNormal', FB_NORMAL);
    }
    function render() {
      for (var j = 0; j < toggles.length; j++) {
        var n = toggles[j].getAttribute('data-a11yw-toggle');
        toggles[j].setAttribute('aria-pressed', prefs[n] ? 'true' : 'false');
      }
      sizeBtns[0].disabled = prefs.font <= 0;
      sizeBtns[1].disabled = prefs.font >= 3;
      sizeBtns[0].setAttribute('aria-disabled', sizeBtns[0].disabled);
      sizeBtns[1].setAttribute('aria-disabled', sizeBtns[1].disabled);
      renderStatus();
    }
    function change() { applyRoot(); save(); render(); }

    for (i = 0; i < toggles.length; i++) {
      toggles[i].addEventListener('click', function () {
        var n = this.getAttribute('data-a11yw-toggle');
        prefs[n] = prefs[n] ? 0 : 1;
        change();
      });
    }
    for (i = 0; i < sizeBtns.length; i++) {
      sizeBtns[i].addEventListener('click', function () {
        var d = +this.getAttribute('data-a11yw-size');
        prefs.font = Math.max(0, Math.min(3, prefs.font + d));
        change();
        /* keep focus usable if the pressed button just disabled itself */
        if (this.disabled) sizeBtns[d > 0 ? 0 : 1].focus();
      });
    }
    host.querySelector('[data-a11yw-reset]').addEventListener('click', function () {
      for (var n in DEF) prefs[n] = 0;
      change();
      renderStatus(tr('a11yw.resetDone', FB_RESET));
    });

    /* open / close / trap */
    function focusables() {
      var list = panel.querySelectorAll('button:not([disabled]), a[href], [tabindex]:not([tabindex="-1"])'), out = [];
      for (var j = 0; j < list.length; j++) if (list[j].offsetParent !== null || list[j] === document.activeElement) out.push(list[j]);
      return out;
    }
    function setInert(on) {
      if (on) {
        var node = host;
        while (node && node !== document.documentElement) {
          var p = node.parentNode;
          if (!p) break;
          for (var c = p.firstElementChild; c; c = c.nextElementSibling) {
            if (c !== node && !c.inert && c.tagName !== 'SCRIPT') { c.inert = true; inerted.push(c); }
          }
          node = p;
        }
        fab.inert = true; inerted.push(fab);
      } else {
        while (inerted.length) inerted.pop().inert = false;
      }
    }
    function openPanel() {
      open = true;
      panel.hidden = false;
      fab.setAttribute('aria-expanded', 'true');
      setInert(true);
      render();
      (closeBtn || panel).focus();
    }
    function closePanel(restore) {
      if (!open) return;
      open = false;
      panel.hidden = true;
      fab.setAttribute('aria-expanded', 'false');
      setInert(false);
      if (restore !== false) fab.focus();
    }
    fab.addEventListener('click', function () { open ? closePanel() : openPanel(); });
    closeBtn.addEventListener('click', function () { closePanel(); });
    panel.addEventListener('keydown', function (ev) {
      if (ev.key === 'Escape' || ev.key === 'Esc') { ev.preventDefault(); ev.stopPropagation(); closePanel(); return; }
      if (ev.key !== 'Tab') return;
      var f = focusables();
      if (!f.length) { ev.preventDefault(); return; }
      var first = f[0], last = f[f.length - 1], a = document.activeElement;
      if (ev.shiftKey && (a === first || !panel.contains(a))) { ev.preventDefault(); last.focus(); }
      else if (!ev.shiftKey && (a === last || !panel.contains(a))) { ev.preventDefault(); first.focus(); }
    });
    document.addEventListener('mousedown', function (ev) {
      if (open && !host.contains(ev.target)) closePanel(false);
    });
    document.addEventListener('focusin', function (ev) {
      if (open && !panel.contains(ev.target)) { var f = focusables(); if (f[0]) f[0].focus(); }
    });
    panel.setAttribute('tabindex', '-1');

    render();
    applyLang();
    document.addEventListener('fullin:lang', applyLang);
    if (!window.FullinI18n) {
      var tries = 0, iv = setInterval(function () {
        if (window.FullinI18n || ++tries > 40) { clearInterval(iv); if (window.FullinI18n) applyLang(); }
      }, 250);
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
