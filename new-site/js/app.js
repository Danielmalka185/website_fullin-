/* FULLIN app section: play the phone demo only while visible; pause control. Vanilla. */
(function () {
  'use strict';
  var sec = document.getElementById('app'); if (!sec) return;
  var btn = sec.querySelector('[data-app-pause]');
  var stage = sec.querySelector('[data-app-stage]');
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  function t(k) { try { var v = window.FullinI18n && window.FullinI18n.t(k); return typeof v === 'string' && v !== k ? v : ''; } catch (e) { return ''; } }
  function label() {
    if (!btn) return;
    var paused = btn.getAttribute('aria-pressed') === 'true';
    var s = t(paused ? 'app.play' : 'app.pause'); if (s) btn.setAttribute('aria-label', s);
  }
  if (btn && !reduce) {
    btn.hidden = false;
    btn.addEventListener('click', function () {
      var p = btn.getAttribute('aria-pressed') !== 'true';
      btn.setAttribute('aria-pressed', p ? 'true' : 'false');
      sec.classList.toggle('is-paused', p); label();
    });
    document.addEventListener('fullin:lang', label);
    setTimeout(label, 300);
  }
  if ('IntersectionObserver' in window && stage) {
    sec.classList.add('is-off');
    new IntersectionObserver(function (es) {
      es.forEach(function (e) { sec.classList.toggle('is-off', !e.isIntersecting); });
    }, { rootMargin: '80px' }).observe(stage);
  }
})();
