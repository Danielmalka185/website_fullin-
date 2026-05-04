(function () {
  'use strict';

  var STORAGE_KEY = 'fullin_a11y';
  var MIN_FONT = 14;
  var MAX_FONT = 26;
  var FONT_STEP = 2;

  /* ---- Persist / restore ---- */
  function load() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {}; } catch (e) { return {}; }
  }
  function save(prefs) {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(prefs)); } catch (e) {}
  }

  /* ---- Apply preferences to <html> ---- */
  function apply(prefs) {
    var html = document.documentElement;
    /* font size */
    if (prefs.fontSize) {
      html.style.fontSize = prefs.fontSize + 'px';
    } else {
      html.style.fontSize = '';
    }
    /* high contrast */
    html.classList.toggle('a11y-high-contrast', !!prefs.contrast);
    /* highlight links */
    html.classList.toggle('a11y-highlight-links', !!prefs.links);
  }

  /* ---- Build widget HTML ---- */
  function buildWidget() {
    var widget = document.createElement('div');
    widget.className = 'a11y-widget';
    widget.setAttribute('id', 'a11y-widget');
    widget.setAttribute('role', 'region');
    widget.setAttribute('aria-label', 'כלי נגישות');
    widget.innerHTML = [
      '<button class="a11y-widget__toggle" id="a11y-toggle"',
      '  aria-expanded="false" aria-controls="a11y-panel"',
      '  aria-label="פתח תפריט נגישות">',
      '  <span class="a11y-widget__icon" aria-hidden="true">♿</span>',
      '  <span class="a11y-widget__label">נגישות</span>',
      '</button>',
      '<div class="a11y-widget__panel" id="a11y-panel" hidden',
      '  role="dialog" aria-label="אפשרויות נגישות">',
      '  <div class="a11y-widget__header">',
      '    <span>כלי נגישות</span>',
      '    <button class="a11y-widget__close" id="a11y-close" aria-label="סגור תפריט נגישות">✕</button>',
      '  </div>',
      '  <div class="a11y-widget__section">',
      '    <div class="a11y-widget__row-label">גודל טקסט</div>',
      '    <div class="a11y-widget__row">',
      '      <button class="a11y-widget__btn" id="a11y-font-dec" aria-label="הקטן טקסט">A<small>−</small></button>',
      '      <button class="a11y-widget__btn a11y-widget__btn--mid" id="a11y-font-reset" aria-label="אפס גודל טקסט">A</button>',
      '      <button class="a11y-widget__btn" id="a11y-font-inc" aria-label="הגדל טקסט">A<big>+</big></button>',
      '    </div>',
      '  </div>',
      '  <div class="a11y-widget__section">',
      '    <div class="a11y-widget__row-label">מצג</div>',
      '    <div class="a11y-widget__row">',
      '      <button class="a11y-widget__toggle-btn" id="a11y-contrast"',
      '        aria-pressed="false" aria-label="הפעל ניגודיות גבוהה">',
      '        <span class="a11y-widget__toggle-icon" aria-hidden="true">◑</span>',
      '        ניגודיות גבוהה',
      '      </button>',
      '    </div>',
      '    <div class="a11y-widget__row">',
      '      <button class="a11y-widget__toggle-btn" id="a11y-links"',
      '        aria-pressed="false" aria-label="הדגש קישורים">',
      '        <span class="a11y-widget__toggle-icon" aria-hidden="true">🔗</span>',
      '        הדגשת קישורים',
      '      </button>',
      '    </div>',
      '  </div>',
      '  <div class="a11y-widget__footer">',
      '    <button class="a11y-widget__reset" id="a11y-reset">איפוס הכל</button>',
      '    <a class="a11y-widget__stmt" href="accessibility.html">הצהרת נגישות ←</a>',
      '  </div>',
      '</div>'
    ].join('\n');
    return widget;
  }

  /* ---- Wire up events ---- */
  function init() {
    var prefs = load();
    apply(prefs);

    var widget = buildWidget();
    document.body.appendChild(widget);

    var toggle   = document.getElementById('a11y-toggle');
    var panel    = document.getElementById('a11y-panel');
    var closeBtn = document.getElementById('a11y-close');
    var fontDec  = document.getElementById('a11y-font-dec');
    var fontReset= document.getElementById('a11y-font-reset');
    var fontInc  = document.getElementById('a11y-font-inc');
    var contrast = document.getElementById('a11y-contrast');
    var links    = document.getElementById('a11y-links');
    var resetAll = document.getElementById('a11y-reset');

    /* sync button states */
    function syncUI() {
      var p = load();
      contrast.setAttribute('aria-pressed', !!p.contrast ? 'true' : 'false');
      contrast.classList.toggle('is-active', !!p.contrast);
      links.setAttribute('aria-pressed', !!p.links ? 'true' : 'false');
      links.classList.toggle('is-active', !!p.links);
    }
    syncUI();

    /* open / close panel */
    function openPanel() {
      panel.hidden = false;
      toggle.setAttribute('aria-expanded', 'true');
      closeBtn.focus();
    }
    function closePanel() {
      panel.hidden = true;
      toggle.setAttribute('aria-expanded', 'false');
      toggle.focus();
    }

    toggle.addEventListener('click', function () {
      panel.hidden ? openPanel() : closePanel();
    });
    closeBtn.addEventListener('click', closePanel);

    /* close on Escape */
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && !panel.hidden) closePanel();
    });

    /* close on outside click */
    document.addEventListener('click', function (e) {
      if (!panel.hidden && !widget.contains(e.target)) closePanel();
    });

    /* font size */
    fontDec.addEventListener('click', function () {
      var p = load();
      var cur = p.fontSize || 16;
      p.fontSize = Math.max(MIN_FONT, cur - FONT_STEP);
      save(p); apply(p);
    });
    fontReset.addEventListener('click', function () {
      var p = load();
      delete p.fontSize;
      save(p); apply(p);
    });
    fontInc.addEventListener('click', function () {
      var p = load();
      var cur = p.fontSize || 16;
      p.fontSize = Math.min(MAX_FONT, cur + FONT_STEP);
      save(p); apply(p);
    });

    /* contrast */
    contrast.addEventListener('click', function () {
      var p = load();
      p.contrast = !p.contrast;
      save(p); apply(p); syncUI();
    });

    /* links highlight */
    links.addEventListener('click', function () {
      var p = load();
      p.links = !p.links;
      save(p); apply(p); syncUI();
    });

    /* reset all */
    resetAll.addEventListener('click', function () {
      save({});
      apply({});
      syncUI();
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
