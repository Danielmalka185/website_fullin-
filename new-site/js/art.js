/* FULLIN art.js: scroll parallax/zoom for .ph imagery (writes --p only; transform-driven in CSS). Reduced-motion safe. */
(function () {
  'use strict';
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce || !('IntersectionObserver' in window)) return;
  var vis = new Set(), ticking = false;
  function update() {
    ticking = false;
    var vh = window.innerHeight || 800;
    vis.forEach(function (el) {
      var r = el.getBoundingClientRect();
      var p = ((r.top + r.height / 2) - vh / 2) / (vh / 2 + r.height / 2);
      el.style.setProperty('--p', Math.max(-1, Math.min(1, p)).toFixed(3));
    });
  }
  function req() { if (!ticking) { ticking = true; requestAnimationFrame(update); } }
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (e) { e.isIntersecting ? vis.add(e.target) : vis.delete(e.target); });
    req();
  }, { rootMargin: '10% 0px' });
  Array.prototype.forEach.call(document.querySelectorAll('.ph'), function (el) { io.observe(el); });
  window.addEventListener('scroll', req, { passive: true });
  window.addEventListener('resize', req);
})();
