/* FULLIN app section: screenshot carousel (scroll-snap on mobile) + gentle parallax on desktop. Vanilla. */
(function () {
  'use strict';
  var sec = document.getElementById('app'); if (!sec) return;
  var track = sec.querySelector('[data-app-track]');
  var show = sec.querySelector('[data-app-showcase]');
  if (!track || !show) return;
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var wide = window.matchMedia && matchMedia('(min-width: 960px)');
  // mobile: start with the first screen in view (works for RTL and LTR)
  function reset() { try { if (!wide.matches) track.scrollTo({ left: 0 }); } catch (e) {} }
  // hide the swipe hint once the user scrolls the carousel
  track.addEventListener('scroll', function () { show.classList.add('is-scrolled'); }, { passive: true });
  // desktop parallax: side phones drift slightly with scroll (transform only)
  if (reduce || !('IntersectionObserver' in window)) return;
  var on = false, ticking = false;
  function upd() {
    ticking = false;
    var r = show.getBoundingClientRect(), vh = window.innerHeight || 800;
    var p = Math.max(-1, Math.min(1, (r.top + r.height / 2 - vh / 2) / vh));
    show.style.setProperty('--par', p.toFixed(3));
  }
  function onScroll() { if (on && wide.matches && !ticking) { ticking = true; requestAnimationFrame(upd); } }
  new IntersectionObserver(function (es) { on = es[0].isIntersecting; if (on) onScroll(); }, { rootMargin: '100px' }).observe(show);
  window.addEventListener('scroll', onScroll, { passive: true });
  reset();
})();
