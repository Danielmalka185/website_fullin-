/* FULLIN i18n: inline JSON -> fetch -> he fallback. Exposes window.FullinI18n */
(function () {
  'use strict';
  var LANGS = ['he', 'en', 'ar', 'ru'];
  var RTL = { he: 1, ar: 1 };
  var LOCALE = { he: 'he_IL', en: 'en_US', ar: 'ar_AR', ru: 'ru_RU' };
  var KEY = 'fullin.lang';
  var cache = {};
  var cur = 'he';

  function inline(l) {
    var el = document.getElementById('copy-' + l);
    if (!el) return null;
    try { return JSON.parse(el.textContent); } catch (e) { return null; }
  }
  function load(l) {
    if (cache[l]) return Promise.resolve(cache[l]);
    var d = inline(l);
    if (d) { cache[l] = d; return Promise.resolve(d); }
    if (!/^https?:/.test(location.protocol)) return Promise.resolve(null);
    return fetch('content/copy.' + l + '.json').then(function (r) { return r.ok ? r.json() : null; })
      .then(function (j) { if (j) cache[l] = j; return j; }).catch(function () { return null; });
  }
  function get(obj, path) {
    var p = path.split('.'), o = obj;
    for (var i = 0; i < p.length; i++) { if (o == null) return undefined; o = o[p[i]]; }
    return o;
  }
  function t(key) {
    var v = cache[cur] && get(cache[cur], key);
    if (v === undefined && cache.he) v = get(cache.he, key);
    return v === undefined ? key : v;
  }
  function str(key) { var v = t(key); return typeof v === 'string' ? v : (v === key ? null : null); }

  function apply(root) {
    root = root || document;
    var n, i, v;
    var els = root.querySelectorAll('[data-i18n]');
    for (i = 0; i < els.length; i++) { v = t(els[i].getAttribute('data-i18n')); if (typeof v === 'string') els[i].textContent = v; }
    els = root.querySelectorAll('[data-i18n-html]');
    for (i = 0; i < els.length; i++) { v = t(els[i].getAttribute('data-i18n-html')); if (typeof v === 'string') els[i].innerHTML = v; }
    els = root.querySelectorAll('[data-i18n-attr]');
    for (i = 0; i < els.length; i++) {
      var pairs = els[i].getAttribute('data-i18n-attr').split(',');
      for (n = 0; n < pairs.length; n++) {
        var kv = pairs[n].split(':');
        if (kv.length < 2) continue;
        v = t(kv.slice(1).join(':').trim());
        if (typeof v === 'string') els[i].setAttribute(kv[0].trim(), v);
      }
    }
  }
  function meta() {
    var m = t('meta'); if (!m || typeof m !== 'object') return;
    if (m.title) document.title = m.title;
    var ol = document.querySelector('meta[property="og:locale"]'); if (ol) ol.setAttribute('content', LOCALE[cur]);
  }
  function syncSwitcher() {
    var b = document.querySelectorAll('[data-lang]');
    for (var i = 0; i < b.length; i++) b[i].setAttribute('aria-pressed', b[i].getAttribute('data-lang') === cur ? 'true' : 'false');
  }
  function detect() {
    var q = null, s = null;
    try { q = new URLSearchParams(location.search).get('lang'); } catch (e) {}
    try { s = localStorage.getItem(KEY); } catch (e) {}
    return LANGS.indexOf(q) > -1 ? q : (LANGS.indexOf(s) > -1 ? s : 'he');
  }
  function setLang(l, opts) {
    if (LANGS.indexOf(l) < 0) l = 'he';
    opts = opts || {};
    return Promise.all([load('he'), load(l)]).then(function () {
      if (!cache[l]) l = 'he';
      cur = l;
      var h = document.documentElement;
      h.setAttribute('lang', l); h.setAttribute('dir', RTL[l] ? 'rtl' : 'ltr');
      apply(document); meta(); syncSwitcher();
      if (!opts.silent) {
        try { localStorage.setItem(KEY, l); } catch (e) {}
        try {
          var u = new URL(location.href);
          if (l === 'he') u.searchParams.delete('lang'); else u.searchParams.set('lang', l);
          history.replaceState(null, '', u.pathname + u.search + u.hash);
        } catch (e) {}
      }
      document.dispatchEvent(new CustomEvent('fullin:lang', { detail: { lang: l } }));
    });
  }
  window.FullinI18n = {
    t: t,
    get lang() { return cur; },
    setLang: setLang,
    apply: apply,
    data: function () { return cache[cur] || cache.he || {}; }
  };
  function init() {
    var b = document.querySelectorAll('[data-lang]');
    for (var i = 0; i < b.length; i++) b[i].addEventListener('click', function (e) { setLang(e.currentTarget.getAttribute('data-lang')); });
    setLang(detect(), { silent: true });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
