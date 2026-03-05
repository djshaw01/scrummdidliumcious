/**
 * app.js — Global theme management and SocketIO bootstrap.
 * Loaded on every page via base.html.
 */
(function () {
  "use strict";

  var THEME_KEY = "scrum-poker-theme";

  /**
   * Apply a theme by setting the data-theme attribute on <html>.
   * @param {string} theme - "light" or "dark"
   */
  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    try {
      localStorage.setItem(THEME_KEY, theme);
    } catch (_e) {
      // localStorage unavailable — continue without persistence
    }
  }

  /**
   * Initialise the theme from localStorage or the OS colour-scheme preference.
   */
  function initTheme() {
    var saved = null;
    try {
      saved = localStorage.getItem(THEME_KEY);
    } catch (_e) {
      // ignore
    }
    if (saved === "light" || saved === "dark") {
      applyTheme(saved);
    } else {
      var prefersDark =
        window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
      applyTheme(prefersDark ? "dark" : "light");
    }
  }

  /**
   * Toggle between light and dark theme.
   * Exposed globally so onclick="window.toggleTheme()" in base.html works.
   */
  window.toggleTheme = function () {
    var current = document.documentElement.getAttribute("data-theme") || "light";
    applyTheme(current === "dark" ? "light" : "dark");
  };

  // Initialise on every page load
  initTheme();

  // SocketIO is initialised lazily by page-specific scripts (e.g. session-detail.js).
  window.PokerApp = {
    socketio: null,
    sessionId: null,
  };
})();
