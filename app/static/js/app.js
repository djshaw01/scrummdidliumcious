const THEME_KEY = "scrum-poker-theme";

function setTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  window.localStorage.setItem(THEME_KEY, theme);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute("data-theme") || "light";
  const next = current === "light" ? "dark" : "light";
  setTheme(next);
}

function initializeTheme() {
  const saved = window.localStorage.getItem(THEME_KEY);
  if (saved === "light" || saved === "dark") {
    setTheme(saved);
  }
}

function initializeThemeToggle() {
  const button = document.getElementById("theme-toggle");
  if (!button) {
    return;
  }
  button.addEventListener("click", toggleTheme);
}

function subscribeToEvent(socket, eventName, callback) {
  if (!socket || typeof socket.on !== "function") {
    return;
  }
  socket.on(eventName, callback);
}

async function apiRequest(url, options = {}) {
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.message || `Request failed with status ${response.status}`);
  }

  return response.status === 204 ? null : response.json();
}

initializeTheme();
initializeThemeToggle();

window.scrumPoker = {
  apiRequest,
  subscribeToEvent,
  setTheme,
};
