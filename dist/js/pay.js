/* FULLIN scan & pay: one big phone with a slow scripted auto-scroll (pure CSS keyframes on the image, steps and progress line share one clock).
   JS only toggles state classes on #pay: .is-paused (button), .is-hold (hover / focus on the phone), .is-off (section off-screen). Vanilla. */
(function () {
  'use strict';
  var sec = document.getElementById('pay'); if (!sec) return;
  var view = sec.querySelector('[data-pay-view]');
  var btn = sec.querySelector('[data-pay-toggle]');
  var phone = sec.querySelector('.pay-phone');
  if (btn) btn.addEventListener('click', function () {
    var p = btn.getAttribute('aria-pressed') !== 'true';
    btn.setAttribute('aria-pressed', p ? 'true' : 'false');
    sec.classList.toggle('is-paused', p);
  });
  if (view && phone) {
    var hold = function (on) { sec.classList.toggle('is-hold', on); };
    phone.addEventListener('mouseenter', function () { hold(true); });
    phone.addEventListener('mouseleave', function () { hold(view === document.activeElement); });
    view.addEventListener('focus', function () { hold(true); });
    view.addEventListener('blur', function () { hold(false); });
  }
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (es) { sec.classList.toggle('is-off', !es[0].isIntersecting); }, { threshold: .1 }).observe(phone || sec);
  }
})();
