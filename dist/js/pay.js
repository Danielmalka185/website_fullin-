/* FULLIN scan & pay: step line draws on scroll (desktop), step highlight, carousel hint. Vanilla, transform/opacity only. */
(function () {
  'use strict';
  var sec = document.getElementById('pay'); if (!sec) return;
  var steps = sec.querySelector('[data-pay-steps]');
  var demo = sec.querySelector('[data-pay-demo]');
  var items = steps ? [].slice.call(steps.querySelectorAll('.pay-step')) : [];
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var phones = sec.querySelector('.pay-phones');
  if (phones && demo) phones.addEventListener('scroll', function () { demo.classList.add('is-scrolled'); }, { passive: true });
  if (!steps) return;
  if (reduce) { steps.style.setProperty('--p', '1'); items.forEach(function (i) { i.classList.add('is-on'); }); return; }
  var ticking = false;
  function upd() {
    ticking = false;
    var r = steps.getBoundingClientRect(), vh = window.innerHeight || 800;
    var p = Math.max(0, Math.min(1, (vh * .85 - r.top) / (r.height + vh * .2)));
    steps.style.setProperty('--p', p.toFixed(3));
    items.forEach(function (it, i) { it.classList.toggle('is-on', p * 1.1 >= (i + .35) / items.length); });
  }
  function on() { if (!ticking) { ticking = true; requestAnimationFrame(upd); } }
  window.addEventListener('scroll', on, { passive: true });
  window.addEventListener('resize', on);
  upd();
})();
