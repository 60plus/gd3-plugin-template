/**
 * NEON HORIZON — Theme JavaScript
 * Applies gradient text effect to dynamically loaded content.
 * Particles and gradient bg are handled by NeonHorizonLayout.vue.
 */
(function () {
  'use strict';

  var THEME_ID = 'neon-horizon';

  function isActive() {
    return document.documentElement.getAttribute('data-theme') === THEME_ID;
  }

  // Apply gradient text to key headings
  function applyGradientText() {
    if (!isActive()) return;
    var selectors = [
      '.gd-title',
      '.home-section-title',
      '.emu-platform-name-text',
      '.title-text',
      '.nh-hero-title',
    ];
    selectors.forEach(function (sel) {
      document.querySelectorAll(sel).forEach(function (el) {
        if (!el.classList.contains('nh-gradient-text')) {
          el.classList.add('nh-gradient-text');
        }
      });
    });
  }

  function cleanup() {
    document.querySelectorAll('.nh-gradient-text').forEach(function (el) {
      el.classList.remove('nh-gradient-text');
    });
  }

  function apply() {
    if (isActive()) { applyGradientText(); } else { cleanup(); }
  }

  // Observe theme changes
  var observer = new MutationObserver(function (mutations) {
    mutations.forEach(function (m) {
      if (m.attributeName === 'data-theme') apply();
    });
  });

  // Observe DOM changes for new content
  var bodyObserver = new MutationObserver(function () {
    if (isActive()) applyGradientText();
  });

  function init() {
    observer.observe(document.documentElement, { attributes: true });
    bodyObserver.observe(document.body, { childList: true, subtree: true });
    apply();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
