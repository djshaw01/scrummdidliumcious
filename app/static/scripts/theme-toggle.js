/**
 * Theme Toggle Script
 *
 * Handles client-side theme switching and persistence for light/dark modes.
 * Syncs with server-side preference and stores in localStorage for fast initial render.
 *
 * Phase 5, User Story 5 (US5 / T041)
 */

(function () {
  'use strict';

  const THEME_KEY = 'scrumm-theme-preference';
  const THEME_LIGHT = 'light';
  const THEME_DARK = 'dark';

  /**
   * Get current theme from document root element.
   * @returns {string} Current theme ('light' or 'dark').
   */
  function getCurrentTheme() {
    const htmlElement = document.documentElement;
    return htmlElement.getAttribute('data-theme') || THEME_LIGHT;
  }

  /**
   * Set theme on document root element.
   * @param {string} theme - Theme to set ('light' or 'dark').
   */
  function setTheme(theme) {
    if (theme !== THEME_LIGHT && theme !== THEME_DARK) {
      theme = THEME_LIGHT;
    }
    document.documentElement.setAttribute('data-theme', theme);
  }

  /**
   * Toggle between light and dark themes.
   * @returns {string} New theme after toggle.
   */
  function toggleTheme() {
    const current = getCurrentTheme();
    const newTheme = current === THEME_LIGHT ? THEME_DARK : THEME_LIGHT;
    setTheme(newTheme);
    return newTheme;
  }

  /**
   * Save theme preference to localStorage.
   * @param {string} theme - Theme to save.
   */
  function saveThemeToLocalStorage(theme) {
    try {
      localStorage.setItem(THEME_KEY, theme);
    } catch (e) {
      console.warn('Failed to save theme to localStorage:', e);
    }
  }

  /**
   * Load theme preference from localStorage.
   * @returns {string|null} Saved theme or null if not found.
   */
  function loadThemeFromLocalStorage() {
    try {
      return localStorage.getItem(THEME_KEY);
    } catch (e) {
      console.warn('Failed to load theme from localStorage:', e);
      return null;
    }
  }

  /**
   * Send theme preference to server.
   * @param {string} theme - Theme to save on server.
   */
  function saveThemeToServer(theme) {
    // Note: This will be implemented when theme API endpoint is added
    // For now, this is a placeholder for future server sync
    fetch('/api/theme', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ theme: theme }),
    }).catch((error) => {
      console.warn('Failed to save theme to server:', error);
    });
  }

  /**
   * Initialize theme from localStorage on page load.
   * This ensures fast theme application before server response.
   */
  function initializeTheme() {
    const savedTheme = loadThemeFromLocalStorage();
    if (savedTheme) {
      setTheme(savedTheme);
    }
  }

  /**
   * Set up theme toggle button event listener.
   */
  function setupThemeToggle() {
    const toggleButton = document.getElementById('theme-toggle');
    if (!toggleButton) {
      return;
    }

    toggleButton.addEventListener('click', function () {
      const newTheme = toggleTheme();
      saveThemeToLocalStorage(newTheme);
      saveThemeToServer(newTheme);
    });
  }

  /**
   * Sync localStorage theme with server-rendered theme on page load.
   * This ensures localStorage matches the authoritative server preference.
   */
  function syncThemeOnLoad() {
    const currentTheme = getCurrentTheme();
    saveThemeToLocalStorage(currentTheme);
  }

  // Initialize theme as early as possible to prevent flash
  initializeTheme();

  // Set up event listeners when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      setupThemeToggle();
      syncThemeOnLoad();
    });
  } else {
    // DOM already loaded
    setupThemeToggle();
    syncThemeOnLoad();
  }

  // Expose theme utilities globally for debugging and programmatic access
  window.ThemeUtils = {
    getCurrentTheme: getCurrentTheme,
    setTheme: setTheme,
    toggleTheme: toggleTheme,
    saveTheme: function (theme) {
      setTheme(theme);
      saveThemeToLocalStorage(theme);
      saveThemeToServer(theme);
    },
  };
})();
