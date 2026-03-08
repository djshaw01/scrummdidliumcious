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

