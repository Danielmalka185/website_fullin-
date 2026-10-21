/* FULLIN page battery: decorative scroll-charge indicator. Stalls at 99% until #contact is in view. */
(function () {
  'use strict';
  var d = document, root = d.documentElement, c = d.getElementById('contact');
  if (!c || !d.body) return;
  var el = d.createElement('div');
  el.className = 'pbat'; el.setAttribute('aria-hidden', 'true');
  el.innerHTML = '<span class="pbat__b"><svg viewBox="0 0 24 24"><path d="M13.5 2 5 13.5h6L10 22l9-12.5h-6z"/></svg></span><b class="pbat__n">1</b>';
  d.body.appendChild(el);
  var num = el.lastChild, cur = 1, tgt = 1, raf = 0, full = false, shown = false, shownN = 1, cls = '', last = 0, ready = false;
  function inView() {
    var r = c.getBoundingClientRect(); return r.top < innerHeight * .6;
  }
  function goal() {
    var y = pageYOffset, top = c.getBoundingClientRect().top + y, span = Math.max(1, top - innerHeight);
    full = ready ? full : inView();
    return full ? 100 : 1 + 98 * Math.min(1, Math.max(0, y / span));
  }
  function paint() {
    var n = Math.max(1, Math.round(cur));
    if (!full && n > 99) n = 99;
    if (n !== shownN) { shownN = n; num.textContent = n; }
    el.style.setProperty('--p', (cur / 100).toFixed(3));
    var k = n >= 100 ? 'f' : n >= 50 ? 'g' : n >= 20 ? 'a' : 'r';
    if (k !== cls) {
      if (k === 'f') { el.classList.remove('is-pulse'); void el.offsetWidth; el.classList.add('is-pulse'); }
      cls = k; el.setAttribute('data-c', k);
    }
  }
  function tick(t) {
    raf = 0; var dt = Math.min(100, t - last || 16); last = t; tgt = goal();
    var diff = tgt - cur;
    if (Math.abs(diff) < .05) { cur = tgt; paint(); el.classList.remove('is-active'); last = 0; return; }
    cur += diff * (1 - Math.exp(-dt / 120)); paint(); raf = requestAnimationFrame(tick);
  }
  function go() {
    var s = pageYOffset > 40;
    if (s !== shown) { shown = s; el.classList.toggle('is-on', s); }
    el.classList.add('is-active');
    if (!raf) raf = requestAnimationFrame(tick);
  }
  addEventListener('scroll', go, { passive: true });
  addEventListener('resize', go, { passive: true });
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (es) {
      var e = es[es.length - 1]; ready = true;
      full = e.isIntersecting || e.boundingClientRect.top < 0; go();
    }, { rootMargin: '0px 0px -40% 0px' }).observe(c);
  }
  addEventListener('load', go);
  paint(); go();
})();
