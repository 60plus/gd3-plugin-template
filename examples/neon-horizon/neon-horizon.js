/**
 * NEON HORIZON — Theme JavaScript
 * Handles all dynamic theme effects via DOM manipulation:
 * - Gradient text on headings
 * - Glass blur on all nh-navbar, nh-user-menu, .glass elements
 * - Neon glow size recalculation
 * All read CSS vars set by theme store on :root
 */
(function () {
  'use strict';

  var THEME_ID = 'neon-horizon';
  var root = document.documentElement;
  var style = root.style;

  function isActive() {
    return root.getAttribute('data-theme') === THEME_ID;
  }

  function getCssVar(name, fallback) {
    var v = getComputedStyle(root).getPropertyValue(name).trim();
    return v || fallback;
  }

  function getCssVarNum(name, fallback) {
    var v = parseFloat(getComputedStyle(root).getPropertyValue(name));
    return isNaN(v) ? fallback : v;
  }

  // ── Gradient text ──────────────────────────────────────────────────
  var GRADIENT_SELECTORS = [
    '.gd-title', '.home-section-title', '.emu-platform-name-text',
    '.title-text', '.nh-hero-title',
  ];

  function applyGradientText() {
    if (!isActive()) return;
    GRADIENT_SELECTORS.forEach(function (sel) {
      document.querySelectorAll(sel).forEach(function (el) {
        if (!el.classList.contains('nh-gradient-text')) {
          el.classList.add('nh-gradient-text');
        }
      });
    });
  }

  function cleanupGradientText() {
    document.querySelectorAll('.nh-gradient-text').forEach(function (el) {
      el.classList.remove('nh-gradient-text');
    });
  }

  // ── Glass blur + opacity — apply to all glass elements ──────────────
  var GLASS_SELECTORS = '.nh-navbar, .nh-user-menu, .glass, .glass-panel, .glass-card, .v-overlay__content > .v-card, .v-dialog .v-card, .sync-dialog, .gd-confirm-box, .gl-modal, .ts-option, .ts-theme-card, .settings-content, .pv-section';
  var _lastBlur = -1;
  var _lastOpacity = -1;

  function updateGlassBlur() {
    if (!isActive()) return;
    var blur = getCssVarNum('--glass-blur-px', 20);
    var opacity = getCssVarNum('--nh-glass-opacity', 0.35);
    if (blur === _lastBlur && opacity === _lastOpacity) return;
    _lastBlur = blur;
    _lastOpacity = opacity;
    var blurVal = 'blur(' + blur + 'px) saturate(180%)';
    document.querySelectorAll(GLASS_SELECTORS).forEach(function (el) {
      el.style.backdropFilter = blurVal;
      el.style.webkitBackdropFilter = blurVal;
      // Update background opacity — parse current bg color and replace alpha
      var cs = getComputedStyle(el);
      var bg = cs.backgroundColor;
      if (bg && bg.startsWith('rgb')) {
        var m = bg.match(/[\d.]+/g);
        if (m && m.length >= 3) {
          el.style.backgroundColor = 'rgba(' + m[0] + ',' + m[1] + ',' + m[2] + ',' + opacity + ')';
        }
      }
    });
  }

  // ── Master update ──────────────────────────────────────────────────
  function update() {
    if (!isActive()) { cleanupGradientText(); return; }
    applyGradientText();
    updateGlassBlur();
  }

  // Observe root attribute/style changes (theme switch, settings changes)
  var observer = new MutationObserver(function () { update(); });

  // Observe body for new elements — debounced to avoid storms during route changes
  var _bodyDebounce;
  var bodyObserver = new MutationObserver(function () {
    if (!isActive()) return;
    clearTimeout(_bodyDebounce);
    _bodyDebounce = setTimeout(function () {
      applyGradientText();
      _lastBlur = -1; _lastOpacity = -1; updateGlassBlur();
    }, 150);
  });

  // Listen for custom event from theme store (no polling needed)
  function onThemeUpdated() { update(); }

  function init() {
    observer.observe(root, { attributes: true, attributeFilter: ['data-theme', 'data-skin', 'style'] });
    bodyObserver.observe(document.body, { childList: true, subtree: true });
    root.addEventListener('gd-theme-updated', onThemeUpdated);
    update();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
