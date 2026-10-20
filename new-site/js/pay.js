/* FULLIN payment section: three iPhone screenshots (scroll-snap carousel on mobile, a row on desktop). JS only hides the swipe hint after the first scroll. Vanilla. */
(function () {
  'use strict';
  var sec = document.getElementById('pay'); if (!sec) return;
  var track = sec.querySelector('[data-pay-track]');
  var stage = sec.querySelector('.pay-demo__stage');
  if (!track || !stage) return;
  track.addEventListener('scroll', function () { stage.classList.add('is-scrolled'); }, { passive: true });
})();
