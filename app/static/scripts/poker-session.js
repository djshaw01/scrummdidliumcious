/**
 * SCRUM Poker — realtime client for vote count, reveal state, and leader actions.
 *
 * Connects to the session WebSocket and handles incoming broadcast events.
 * Vote, reveal, estimate, and complete actions are sent via fetch to the REST API.
 */

(function () {
  "use strict";

  /** @type {string|null} */
  const sessionEl = document.querySelector("[data-session-id]");
  if (!sessionEl) return;

  const SESSION_ID = sessionEl.dataset.sessionId;

  // ── WebSocket connection ──────────────────────────────────────────────────

  /**
   * Open a WebSocket connection to the session event stream.
   * Reconnects automatically on close with exponential back-off (capped at 30 s).
   *
   * @param {number} [delayMs=0] - Initial reconnect delay in milliseconds.
   */
  function connectWebSocket(delayMs) {
    delayMs = delayMs || 0;
    setTimeout(function () {
      const protocol = location.protocol === "https:" ? "wss:" : "ws:";
      const ws = new WebSocket(
        protocol + "//" + location.host + "/ws/poker/session/" + SESSION_ID
      );

      ws.onmessage = function (event) {
        let data;
        try {
          data = JSON.parse(event.data);
        } catch (_) {
          return;
        }
        handleEvent(data);
      };

      ws.onclose = function () {
        // Back-off: double the delay up to 30 s.
        const next = Math.min((delayMs || 1000) * 2, 30000);
        connectWebSocket(next);
      };
    }, delayMs);
  }

  connectWebSocket(0);

  // ── Event handlers ────────────────────────────────────────────────────────

  /**
   * Dispatch an incoming server broadcast event to the appropriate handler.
   *
   * @param {{ type: string, [key: string]: any }} event
   */
  function handleEvent(event) {
    switch (event.type) {
      case "vote_cast":
      case "vote_removed":
        updateVoteCount(event.issue_id, event.vote_count);
        break;
      case "votes_revealed":
        renderRevealedState(event);
        break;
      case "estimate_saved":
        updateEstimateDisplay(event.issue_id, event.final_estimate);
        break;
      case "issue_activated":
        highlightActiveNavItem(event.issue_id);
        break;
      case "session_completed":
        markSessionCompleted();
        break;
      case "leadership_transferred":
        // Reload page to reflect new leadership.
        window.location.reload();
        break;
    }
  }

  /**
   * Update the vote count display for an issue.
   *
   * @param {string} issueId
   * @param {number} count
   */
  function updateVoteCount(issueId, count) {
    document
      .querySelectorAll(".js-vote-count[data-issue-id='" + issueId + "']")
      .forEach(function (el) {
        el.textContent = String(count);
      });
  }

  /**
   * Render post-reveal vote summary: hide vote cards, show individual votes
   * and numeric average.
   *
   * @param {{ issue_id: string, votes: Array<{participant_id: string, card_value: string}>, average_numeric_vote: number|null }} event
   */
  function renderRevealedState(event) {
    const issueEl = document.querySelector(
      ".poker-issue[data-issue-id='" + event.issue_id + "']"
    );
    if (!issueEl) return;

    // Hide voting cards.
    const cardsEl = issueEl.querySelector(".js-vote-cards");
    if (cardsEl) cardsEl.style.display = "none";

    // Show revealed badge on vote strip.
    const strip = issueEl.querySelector(".poker-vote-strip");
    if (strip && !strip.querySelector(".poker-vote-strip__revealed-badge")) {
      const badge = document.createElement("span");
      badge.className = "poker-vote-strip__revealed-badge";
      badge.textContent = "Revealed";
      strip.appendChild(badge);
    }

    // Render per-vote pills.
    const votesContainer = issueEl.querySelector(".js-revealed-votes");
    if (votesContainer) {
      votesContainer.innerHTML = "";
      (event.votes || []).forEach(function (v) {
        const pill = document.createElement("span");
        pill.className = "poker-reveal-summary__pill";
        pill.textContent = v.card_value;
        pill.title = "Participant " + v.participant_id;
        votesContainer.appendChild(pill);
      });
    }

    // Show average.
    const avgEl = issueEl.querySelector(".js-vote-average");
    if (avgEl) {
      avgEl.textContent =
        event.average_numeric_vote != null
          ? event.average_numeric_vote.toFixed(1)
          : "—";
    }

    // Show estimate form if it was hidden.
    const estimateForm = issueEl.querySelector(".js-estimate-form");
    if (estimateForm) estimateForm.style.display = "";
  }

  /**
   * Update the saved estimate label for a nav card and the detail section.
   *
   * @param {string} issueId
   * @param {string|null} estimate
   */
  function updateEstimateDisplay(issueId, estimate) {
    // Nav card estimate badge.
    const navItem = document.querySelector(
      ".poker-nav__item[data-issue-id='" + issueId + "']"
    );
    if (navItem) {
      let badge = navItem.querySelector(".poker-nav__estimate");
      if (!badge) {
        badge = document.createElement("span");
        badge.className = "poker-nav__estimate";
        navItem.querySelector(".poker-nav__card").appendChild(badge);
      }
      badge.textContent = estimate || "";
    }
  }

  /**
   * Highlight the newly activated issue in the navigation list.
   *
   * @param {string} issueId
   */
  function highlightActiveNavItem(issueId) {
    document.querySelectorAll(".poker-nav__item").forEach(function (el) {
      const active = el.dataset.issueId === issueId;
      el.classList.toggle("poker-nav__item--active", active);
      const btn = el.querySelector(".poker-nav__card");
      if (btn) btn.setAttribute("aria-current", active ? "true" : "false");
    });
  }

  /**
   * Disable all vote and leader action buttons when session is completed.
   */
  function markSessionCompleted() {
    document.querySelectorAll(".js-cast-vote, .js-reveal-votes").forEach(function (el) {
      el.disabled = true;
      el.setAttribute("aria-disabled", "true");
    });
    const completeBtn = document.querySelector(".js-complete-session");
    if (completeBtn) completeBtn.style.display = "none";
    const badge = document.createElement("span");
    badge.className = "poker-status-row__badge poker-status-row__badge--completed";
    badge.textContent = "Completed";
    if (completeBtn && completeBtn.parentNode) {
      completeBtn.parentNode.replaceChild(badge, completeBtn);
    }
  }

  // ── REST action helpers ───────────────────────────────────────────────────

  /**
   * Derive the acting participant ID from sessionStorage or a visible
   * ``data-participant-id`` attribute on the page.
   *
   * @returns {string|null}
   */
  function currentParticipantId() {
    return (
      sessionStorage.getItem("participantId") ||
      (document.querySelector("[data-participant-id]") || {}).dataset
        ?.participantId ||
      null
    );
  }

  /**
   * Send a JSON fetch request and return the parsed response or null on error.
   *
   * @param {string} url
   * @param {{ method?: string, body?: object }} [opts]
   * @returns {Promise<object|null>}
   */
  async function apiFetch(url, opts) {
    opts = opts || {};
    try {
      const resp = await fetch(url, {
        method: opts.method || "GET",
        headers: { "Content-Type": "application/json" },
        body: opts.body ? JSON.stringify(opts.body) : undefined,
      });
      if (!resp.ok) return null;
      if (resp.status === 204) return {};
      return await resp.json();
    } catch (_) {
      return null;
    }
  }

  // ── DOM event listeners ───────────────────────────────────────────────────

  document.addEventListener("click", async function (e) {
    const target = /** @type {HTMLElement} */ (e.target);

    // Cast vote
    const castBtn = target.closest(".js-cast-vote");
    if (castBtn) {
      const cardsEl = castBtn.closest(".js-vote-cards");
      if (!cardsEl) return;
      const issueId = cardsEl.dataset.issueId;
      const cardValue = castBtn.dataset.cardValue;
      const participantId = currentParticipantId();
      if (!participantId || !issueId || !cardValue) return;

      // Toggle selected state.
      cardsEl
        .querySelectorAll(".poker-card")
        .forEach((c) => c.classList.remove("poker-card--selected"));
      castBtn.classList.add("poker-card--selected");

      await apiFetch(
        "/api/v1/sessions/" + SESSION_ID + "/issues/" + issueId + "/votes/me",
        {
          method: "PUT",
          body: { participant_id: participantId, card_value: cardValue },
        }
      );
      return;
    }

    // Reveal votes
    const revealBtn = target.closest(".js-reveal-votes");
    if (revealBtn) {
      const issueId = revealBtn.dataset.issueId;
      if (!issueId) return;
      const result = await apiFetch(
        "/api/v1/sessions/" + SESSION_ID + "/issues/" + issueId + "/reveal",
        { method: "POST" }
      );
      if (result) renderRevealedState({ ...result, issue_id: issueId });
      return;
    }

    // Save estimate
    const saveEstBtn = target.closest(".js-save-estimate");
    if (saveEstBtn) {
      const issueId = saveEstBtn.dataset.issueId;
      const form = saveEstBtn.closest(".js-estimate-form");
      if (!issueId || !form) return;
      const customInput = form.querySelector(".js-custom-estimate");
      const custom = customInput ? customInput.value.trim() : "";
      await apiFetch(
        "/api/v1/sessions/" + SESSION_ID + "/issues/" + issueId + "/estimate",
        { method: "POST", body: { custom_estimate: custom || null } }
      );
      return;
    }

    // Activate issue (nav card)
    const activateBtn = target.closest(".js-activate-issue");
    if (activateBtn) {
      const issueId = activateBtn.dataset.issueId;
      if (!issueId) return;
      await apiFetch(
        "/api/v1/sessions/" +
          SESSION_ID +
          "/issues/" +
          issueId +
          "/activate",
        { method: "POST" }
      );
      return;
    }

    // Complete session
    const completeBtn = target.closest(".js-complete-session");
    if (completeBtn) {
      if (!confirm("Complete this session? Voting will be locked.")) return;
      await apiFetch("/api/v1/sessions/" + SESSION_ID + "/complete", {
        method: "POST",
      });
      return;
    }

    // Rejoin
    const rejoinBtn = target.closest(".js-rejoin");
    if (rejoinBtn) {
      const participantId = currentParticipantId();
      if (!participantId) return;
      await apiFetch(
        "/api/v1/sessions/" +
          SESSION_ID +
          "/participants/" +
          participantId +
          "/rejoin",
        { method: "POST" }
      );
    }
  });
})();

// ── Entry Page: New Session Modal ──────────────────────────────────────────

(function () {
  "use strict";

  const modal = document.querySelector(".js-new-session-modal");
  if (!modal) return;

  const openBtn = document.querySelector(".js-open-new-session-modal");
  const cancelBtn = document.querySelector(".js-cancel-new-session");
  const form = document.querySelector(".js-new-session-form");
  const teamSelect = document.getElementById("teamSelect");
  const sessionNameInput = document.getElementById("sessionName");
  const submitBtn = document.querySelector(".js-submit-new-session");

  // Load teams on page load.
  loadTeams();

  // Open modal.
  if (openBtn) {
    openBtn.addEventListener("click", function () {
      modal.classList.add("is-active");
    });
  }

  // Close modal.
  if (cancelBtn) {
    cancelBtn.addEventListener("click", function () {
      modal.classList.remove("is-active");
      form.reset();
      clearErrors();
    });
  }

  // Close modal on background click.
  modal.addEventListener("click", function (e) {
    if (e.target === modal) {
      modal.classList.remove("is-active");
      form.reset();
      clearErrors();
    }
  });

  // Load team names for prefill.
  if (teamSelect) {
    teamSelect.addEventListener("change", async function () {
      const teamId = teamSelect.value;
      if (!teamId) return;

      // Fetch last session name for this team.
      try {
        const resp = await fetch("/api/v1/teams/" + teamId + "/last-session-name");
        if (resp.ok) {
          const data = await resp.json();
          if (data.last_session_name && sessionNameInput) {
            sessionNameInput.value = data.last_session_name;
          }
        }
      } catch (_) {
        // Ignore prefill errors.
      }
    });
  }

  // Submit form.
  if (form) {
    form.addEventListener("submit", async function (e) {
      e.preventDefault();
      clearErrors();

      const formData = new FormData(form);

      // Validate required fields.
      if (!formData.get("team_id")) {
        showError(".js-team-error", "Please select a team.");
        return;
      }
      if (!formData.get("session_name")) {
        showError(".js-session-name-error", "Please enter a session name.");
        return;
      }
      if (!formData.get("sprint_number")) {
        showError(".js-sprint-number-error", "Please enter a sprint number.");
        return;
      }
      if (!formData.get("user_identifier")) {
        showError(".js-user-identifier-error", "Please enter your email or username.");
        return;
      }
      if (!formData.get("issues_file")) {
        showError(".js-issues-file-error", "Please upload a CSV file.");
        return;
      }

      // Set card_set default if not set.
      if (!formData.get("card_set")) {
        formData.set("card_set", "fibonacci_plus_specials");
      }

      submitBtn.disabled = true;
      submitBtn.textContent = "Creating...";

      try {
        const resp = await fetch("/api/v1/sessions", {
          method: "POST",
          body: formData,
        });

        if (resp.ok) {
          const data = await resp.json();
          // Redirect to the new session page.
          window.location.href = "/poker/session/" + data.id;
        } else {
          const err = await resp.json();
          showError(".js-form-error", err.error || "Failed to create session.");
        }
      } catch (e) {
        showError(".js-form-error", "Network error. Please try again.");
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = "Create Session";
      }
    });
  }

  async function loadTeams() {
    if (!teamSelect) return;

    try {
      const resp = await fetch("/api/v1/teams");
      if (resp.ok) {
        const data = await resp.json();
        data.teams.forEach(function (team) {
          const option = document.createElement("option");
          option.value = team.id;
          option.textContent = team.name;
          teamSelect.appendChild(option);
        });
      }
    } catch (_) {
      // Ignore team loading errors.
    }
  }

  function showError(selector, message) {
    const el = document.querySelector(selector);
    if (el) {
      el.textContent = message;
      el.classList.add("is-visible");
    }
  }

  function clearErrors() {
    document.querySelectorAll(".error-message").forEach(function (el) {
      el.textContent = "";
      el.classList.remove("is-visible");
    });
  }
})();

// ── Entry Page: Session Listing ────────────────────────────────────────────

(function () {
  "use strict";

  const listContainer = document.querySelector(".js-sessions-list");
  if (!listContainer) return;

  loadSessions();

  async function loadSessions() {
    try {
      const resp = await fetch("/api/v1/sessions");
      if (resp.ok) {
        const data = await resp.json();
        renderSessions(data.sessions);
      } else {
        listContainer.innerHTML = "<p>Failed to load sessions.</p>";
      }
    } catch (_) {
      listContainer.innerHTML = "<p>Network error. Please refresh the page.</p>";
    }
  }

  function renderSessions(sessions) {
    if (sessions.length === 0) {
      listContainer.innerHTML = "<p>No sessions found. Create your first session!</p>";
      return;
    }

    listContainer.innerHTML = "";
    sessions.forEach(function (session) {
      const card = document.createElement("div");
      card.className = "session-card";

      const header = document.createElement("div");
      header.className = "session-card__header";

      const link = document.createElement("a");
      link.className = "session-card__name";
      link.href = "/poker/session/" + session.id;
      link.textContent = session.name;

      const status = document.createElement("span");
      status.className =
        "session-card__status session-card__status--" + session.status;
      status.textContent = session.status.charAt(0).toUpperCase() + session.status.slice(1);

      header.appendChild(link);
      header.appendChild(status);

      const meta = document.createElement("div");
      meta.className = "session-card__meta";
      meta.textContent =
        "Sprint " +
        session.sprint_number +
        " • " +
        session.participant_count +
        " participant(s)";

      card.appendChild(header);
      card.appendChild(meta);
      listContainer.appendChild(card);
    });
  }
})();

// ── Session Page: Leader Transfer Modal ────────────────────────────────────

(function () {
  "use strict";

  const modal = document.querySelector(".js-transfer-leader-modal");
  if (!modal) return;

  const openBtn = document.querySelector(".js-open-transfer-leader-modal");
  const cancelBtn = document.querySelector(".js-cancel-transfer-leader");
  const submitBtn = document.querySelector(".js-submit-transfer-leader");

  // Open modal.
  if (openBtn) {
    openBtn.addEventListener("click", function () {
      modal.classList.add("is-active");
    });
  }

  // Close modal.
  if (cancelBtn) {
    cancelBtn.addEventListener("click", function () {
      modal.classList.remove("is-active");
      clearSelection();
      clearErrors();
    });
  }

  // Close modal on background click.
  modal.addEventListener("click", function (e) {
    if (e.target === modal) {
      modal.classList.remove("is-active");
      clearSelection();
      clearErrors();
    }
  });

  // Submit transfer.
  if (submitBtn) {
    submitBtn.addEventListener("click", async function () {
      clearErrors();

      const selectedRadio = modal.querySelector('input[name="new_leader"]:checked');
      if (!selectedRadio) {
        showError(".js-transfer-error", "Please select a new leader.");
        return;
      }

      const newLeaderId = selectedRadio.value;
      const sessionId = openBtn ? openBtn.dataset.sessionId : null;
      if (!sessionId) return;

      // Get current leader ID (first participant with is_leader flag).
      const currentLeaderId = getCurrentLeaderId();
      if (!currentLeaderId) {
        showError(".js-transfer-error", "Could not determine current leader.");
        return;
      }

      submitBtn.disabled = true;
      const originalText = submitBtn.textContent;
      submitBtn.textContent = "Transferring...";

      try {
        const resp = await fetch("/api/v1/sessions/" + sessionId + "/leader", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            current_leader_participant_id: currentLeaderId,
            new_leader_participant_id: newLeaderId,
          }),
        });

        if (resp.ok) {
          // Reload page to reflect new leadership.
          window.location.reload();
        } else {
          const err = await resp.json();
          showError(".js-transfer-error", err.error || "Failed to transfer leadership.");
        }
      } catch (e) {
        showError(".js-transfer-error", "Network error. Please try again.");
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
      }
    });
  }

  function getCurrentLeaderId() {
    const leaderIcon = document.querySelector(
      '.participant-icon[data-is-leader="true"]'
    );
    if (!leaderIcon) return null;
    return leaderIcon.dataset.participantId || null;
  }

  function clearSelection() {
    const radios = modal.querySelectorAll('input[name="new_leader"]');
    radios.forEach(function (r) {
      r.checked = false;
    });
  }

  function showError(selector, message) {
    const el = modal.querySelector(selector);
    if (el) {
      el.textContent = message;
      el.classList.add("is-visible");
    }
  }

  function clearErrors() {
    modal.querySelectorAll(".error-message").forEach(function (el) {
      el.textContent = "";
      el.classList.remove("is-visible");
    });
  }
})();

