/* FULLIN sections.js: venue tabs, accordion + FAQ JSON-LD, lightbox, lead form. Vanilla, no deps. */
(function () {
  'use strict';
  var doc = document;
  function $(s, r) { return (r || doc).querySelector(s); }
  function $$(s, r) { return Array.prototype.slice.call((r || doc).querySelectorAll(s)); }
  function t(key, fb) {
    try {
      if (window.FullinI18n && typeof window.FullinI18n.t === 'function') {
        var v = window.FullinI18n.t(key);
        if (v && v !== key && typeof v === 'string') return v;
      }
    } catch (e) {}
    return fb == null ? '' : fb;
  }
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  function isRTL() { return (doc.documentElement.dir || 'ltr') === 'rtl'; }

  /* ---- Venue tabs ---- */
  function initTabs() {
    var root = $('[data-venues]'); if (!root) return;
    var tabs = $$('[role=tab]', root);
    function select(i, focus) {
      tabs.forEach(function (tab, j) {
        var on = i === j;
        tab.setAttribute('aria-selected', on ? 'true' : 'false');
        tab.tabIndex = on ? 0 : -1;
        var p = doc.getElementById(tab.getAttribute('aria-controls'));
        if (p) p.hidden = !on;
      });
      if (focus) tabs[i].focus();
      tabs[i].scrollIntoView && tabs[i].scrollIntoView({ block: 'nearest', inline: 'nearest', behavior: reduce ? 'auto' : 'smooth' });
    }
    tabs.forEach(function (tab, i) {
      tab.addEventListener('click', function () { select(i, false); });
      tab.addEventListener('keydown', function (e) {
        var n = tabs.length, next = -1, fwd = isRTL() ? 'ArrowLeft' : 'ArrowRight', back = isRTL() ? 'ArrowRight' : 'ArrowLeft';
        if (e.key === fwd || e.key === 'ArrowDown') next = (i + 1) % n;
        else if (e.key === back || e.key === 'ArrowUp') next = (i - 1 + n) % n;
        else if (e.key === 'Home') next = 0;
        else if (e.key === 'End') next = n - 1;
        if (next > -1) { e.preventDefault(); select(next, true); }
      });
    });
  }

  /* ---- FAQ accordion + JSON-LD ---- */
  function initFaq() {
    var root = $('[data-accordion]'); if (!root) return;
    function setH(panel, open, animate) {
      if (open) {
        panel.hidden = false;
        if (!animate || reduce) { panel.style.height = 'auto'; return; }
        panel.style.height = '0px';
        requestAnimationFrame(function () { panel.style.height = panel.scrollHeight + 'px'; });
        var done = function () { panel.style.height = 'auto'; panel.removeEventListener('transitionend', done); };
        panel.addEventListener('transitionend', done);
      } else {
        if (!animate || reduce) { panel.style.height = '0px'; panel.hidden = true; return; }
        panel.style.height = panel.scrollHeight + 'px';
        requestAnimationFrame(function () { requestAnimationFrame(function () { panel.style.height = '0px'; }); });
        var end = function (e) { if (e.propertyName !== 'height') return; if (panel.previousElementSibling || true) { if (panel.style.height === '0px') panel.hidden = true; } panel.removeEventListener('transitionend', end); };
        panel.addEventListener('transitionend', end);
      }
    }
    $$('.s-acc__btn', root).forEach(function (btn) {
      var panel = doc.getElementById(btn.getAttribute('aria-controls'));
      panel.style.height = '0px';
      btn.addEventListener('click', function () {
        var open = btn.getAttribute('aria-expanded') === 'true';
        btn.setAttribute('aria-expanded', open ? 'false' : 'true');
        setH(panel, !open, true);
      });
    });
    // arrow-key movement between headers
    root.addEventListener('keydown', function (e) {
      var btns = $$('.s-acc__btn', root), i = btns.indexOf(doc.activeElement);
      if (i < 0) return;
      var n = -1;
      if (e.key === 'ArrowDown') n = (i + 1) % btns.length;
      else if (e.key === 'ArrowUp') n = (i - 1 + btns.length) % btns.length;
      else if (e.key === 'Home') n = 0; else if (e.key === 'End') n = btns.length - 1;
      if (n > -1) { e.preventDefault(); btns[n].focus(); }
    });
  }
  function buildFaqLd() {
    var items = [], i = 0, q, a;
    while (i < 50) {
      q = t('faq.items.' + i + '.q', ''); a = t('faq.items.' + i + '.a', '');
      if (!q || !a) break;
      items.push({ '@type': 'Question', name: q, acceptedAnswer: { '@type': 'Answer', text: a } });
      i++;
    }
    if (!items.length) return;
    var el = doc.getElementById('faq-jsonld');
    if (!el) { el = doc.createElement('script'); el.type = 'application/ld+json'; el.id = 'faq-jsonld'; doc.head.appendChild(el); }
    el.textContent = JSON.stringify({ '@context': 'https://schema.org', '@type': 'FAQPage', inLanguage: doc.documentElement.lang || undefined, mainEntity: items });
  }

  /* ---- Lightbox ---- */
  function initLightbox() {
    var lb = doc.getElementById('s-lightbox'); if (!lb) return;
    var img = $('.s-lb__img', lb), cap = $('.s-lb__cap', lb), closeBtn = $('[data-lb-close]', lb), last = null;
    function open(btn) {
      last = btn;
      var ti = $('img', btn), c = $('.s-tile__cap', btn);
      img.src = btn.getAttribute('data-lightbox');
      img.alt = ti ? ti.alt : '';
      cap.textContent = c ? c.textContent : '';
      lb.hidden = false;
      doc.documentElement.style.overflow = 'hidden';
      closeBtn.focus();
    }
    function close() {
      lb.hidden = true; img.removeAttribute('src');
      doc.documentElement.style.overflow = '';
      if (last) last.focus();
    }
    $$('[data-lightbox]').forEach(function (b) { b.addEventListener('click', function () { open(b); }); });
    closeBtn.addEventListener('click', close);
    lb.addEventListener('click', function (e) { if (e.target === lb) close(); });
    doc.addEventListener('keydown', function (e) {
      if (lb.hidden) return;
      if (e.key === 'Escape') { e.preventDefault(); close(); }
      else if (e.key === 'Tab') { e.preventDefault(); closeBtn.focus(); } // only one focusable control: trap
    });
    // keep focus inside even if focus escapes by other means
    doc.addEventListener('focusin', function (e) { if (!lb.hidden && !lb.contains(e.target)) closeBtn.focus(); });
  }

  /* ---- Lead form ---- */
  function heCopy() {
    try { var el = doc.getElementById('copy-he'); return el ? JSON.parse(el.textContent) : null; } catch (e) { return null; }
  }
  function initForm() {
    var form = doc.getElementById('lead-form'); if (!form) return;
    var fields = ['interest', 'name', 'business', 'type', 'phone', 'city'];
    var state = {}; // field -> error key or ''
    function el(n) { return doc.getElementById('lf-' + n); }
    function errEl(n) { return doc.getElementById('lf-' + n + '-err'); }
    function check(n) {
      var v = (el(n).value || '').trim();
      if (!v) return 'required';
      if (n === 'phone') {
        var d = v.replace(/[\s\-().]/g, '');
        if (!/^\+?\d{9,14}$/.test(d)) return 'phone';
      }
      return '';
    }
    var FB = { required: 'שדה חובה', phone: 'מספר הטלפון לא נראה תקין' };
    function render(n) {
      var k = state[n], e = errEl(n), inp = el(n);
      if (k) {
        e.textContent = t('contact.form.errors.' + k, FB[k]); e.hidden = false;
        inp.setAttribute('aria-invalid', 'true');
      } else { e.hidden = true; e.textContent = ''; inp.removeAttribute('aria-invalid'); }
    }
    fields.forEach(function (n) {
      el(n).addEventListener('blur', function () { if (state[n] !== undefined || el(n).value) { state[n] = check(n); render(n); } });
      el(n).addEventListener('input', function () { if (state[n]) { state[n] = check(n); render(n); } });
      el(n).addEventListener('change', function () { if (state[n]) { state[n] = check(n); render(n); } });
    });
    // event interest: relabel business/type so the form reads naturally for an event
    function relabel() {
      var ev = el('interest').value === '2';
      var b = doc.getElementById('lf-business-label'), ty = doc.getElementById('lf-type-label');
      if (b) b.textContent = t(ev ? 'contact.form.businessEvent' : 'contact.form.business', b.textContent);
      if (ty) ty.textContent = t(ev ? 'contact.form.typeEvent' : 'contact.form.type', ty.textContent);
    }
    el('interest').addEventListener('change', relabel);
    doc.addEventListener('fullin:lang', function () {
      relabel();
      fields.forEach(function (n) { if (state[n]) render(n); });
      buildFaqLd();
    });
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var first = null;
      fields.forEach(function (n) { state[n] = check(n); render(n); if (state[n] && !first) first = n; });
      var ok = $('#lf-success'); ok.hidden = true;
      if (first) { el(first).focus(); return; }
      var he = heCopy(), c = he && he.contact;
      var tpl = (c && c.waMessageTemplate) || t('contact.waMessageTemplate', '');
      var types = (c && c.form && c.form.typeOptions) || [];
      var idx = parseInt(el('type').value, 10);
      var ints = (c && c.form && c.form.interestOptions) || [];
      var iidx = parseInt(el('interest').value, 10);
      var map = {
        interest: ints[iidx] != null ? ints[iidx] : String(el('interest').selectedOptions[0].textContent).trim(),
        name: el('name').value.trim(), business: el('business').value.trim(),
        type: types[idx] != null ? types[idx] : String(el('type').selectedOptions[0].textContent).trim(),
        phone: el('phone').value.trim(), city: el('city').value.trim()
      };
      var msg = tpl.replace(/\{(\w+)\}/g, function (m, k) { return map[k] != null ? map[k] : m; });
      var url = 'https://wa.me/972542780713?text=' + encodeURIComponent(msg);
      ok.hidden = false;
      var w = window.open(url, '_blank', 'noopener');
      if (!w) window.location.href = url;
    });
  }

  function applyExtras() {
    $$('[data-x]').forEach(function (e) { var v = t(e.getAttribute('data-x'), ''); if (v) e.textContent = v; });
    $$('[data-x-attr]').forEach(function (e) {
      e.getAttribute('data-x-attr').split(',').forEach(function (pr) {
        var kv = pr.split(':'), v = t(kv[1].trim(), ''); if (v) e.setAttribute(kv[0].trim(), v);
      });
    });
  }
  doc.addEventListener('fullin:lang', applyExtras);
  function init() { applyExtras(); initTabs(); initFaq(); initLightbox(); initForm(); buildFaqLd(); }
  if (doc.readyState === 'loading') doc.addEventListener('DOMContentLoaded', init); else init();
  // JSON-LD once i18n is ready (copy may load async)
  doc.addEventListener('fullin:lang', buildFaqLd);
  window.addEventListener('load', buildFaqLd);

  /* scrollable steps list is keyboard-focusable only when it actually scrolls */
  (function () {
    var l = doc.querySelector('.steps__list'); if (!l) return;
    function f() { if (l.scrollWidth > l.clientWidth + 1) l.setAttribute('tabindex', '0'); else l.removeAttribute('tabindex'); }
    f(); window.addEventListener('resize', f); window.addEventListener('load', f);
  })();
})();
