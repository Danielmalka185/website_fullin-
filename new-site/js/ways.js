/* FULLIN #ways: card CTAs preselect the contact-form interest. Also supports #contact?way=rental in the URL. */
(function () {
  'use strict';
  var doc = document;
  var MAP = { hosting: '0', host: '0', rental: '1', rent: '1', event: '2', events: '2', unsure: '3' };
  function preselect(way) {
    var sel = doc.getElementById('lf-interest');
    if (!sel || MAP[way] == null) return;
    sel.value = MAP[way];
    sel.dispatchEvent(new Event('change', { bubbles: true }));
  }
  function fromHash() {
    var m = /^#contact\?(?:.*&)?way=(\w+)/.exec(location.hash || '');
    if (!m) return;
    preselect(m[1]);
    var c = doc.getElementById('contact');
    if (c && c.scrollIntoView) c.scrollIntoView();
  }
  function init() {
    Array.prototype.forEach.call(doc.querySelectorAll('[data-way]'), function (a) {
      a.addEventListener('click', function () { preselect(a.getAttribute('data-way')); });
    });
    fromHash();
  }
  window.addEventListener('hashchange', fromHash);
  window.addEventListener('fullin:way', function (e) { preselect(e.detail); });
  if (doc.readyState === 'loading') doc.addEventListener('DOMContentLoaded', init); else init();
})();
