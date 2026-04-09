/**
 * My Theme — Plugin JavaScript
 * Runs in the browser. Has access to window.__GD__ for Vue, stores, API.
 * See docs/HOOKS.md for the full window.__GD__ API reference.
 */
(function () {
  'use strict';
  var THEME_ID = 'my-theme';
  var root = document.documentElement;

  function isActive() {
    return root.getAttribute('data-theme') === THEME_ID;
  }

  function apply() {
    if (!isActive()) return;
    // Your dynamic effects here
    // Example: read CSS var set by theme settings
    // var blur = getComputedStyle(root).getPropertyValue('--my-glass-blur').trim();
  }

  // React to theme changes
  root.addEventListener('gd-theme-updated', apply);
  var observer = new MutationObserver(function (mutations) {
    mutations.forEach(function (m) {
      if (m.attributeName === 'data-theme') apply();
    });
  });
  observer.observe(root, { attributes: true, attributeFilter: ['data-theme', 'style'] });
  apply();
})();
