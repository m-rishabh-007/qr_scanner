(() => {
  "use strict";
  const config = JSON.parse(document.getElementById("bootstrap").textContent);
  const ratings = new Map();
  let sessionToken = sessionStorage.getItem(`reviewflow:${config.qrToken}:session`) || null;
  let selectedDraftId = null;
  let edited = false;
  const feedbackKeyName = `reviewflow:${config.qrToken}:feedbackKey`;
  const feedbackKey = sessionStorage.getItem(feedbackKeyName) || uuid();
  sessionStorage.setItem(feedbackKeyName, feedbackKey);

  const qRoot = document.getElementById("questions");
  const form = document.getElementById("feedback-form");
  const comment = document.getElementById("comment");
  const formError = document.getElementById("form-error");
  const suggestions = document.getElementById("suggestions");
  const questionnaire = document.getElementById("questionnaire");
  const draftCards = document.getElementById("draft-cards");
  const finalText = document.getElementById("final-text");
  const copyButton = document.getElementById("copy-open-button");
  const retryButton = document.getElementById("retry-copy-button");
  const actionError = document.getElementById("action-error");
  const manualCopy = document.getElementById("manual-copy");
  const manualGoogleLink = document.getElementById("manual-google-link");
  manualGoogleLink.href = config.googleReviewUrl;

  function uuid() {
    return crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random()}`;
  }

  async function api(path, options = {}) {
    const response = await fetch(`${config.apiBase}${path}`, {
      ...options,
      headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    });
    const data = response.status === 204 ? null : await response.json().catch(() => ({}));
    if (!response.ok) {
      const error = new Error(data?.detail || "Request failed. Please try again.");
      error.status = response.status;
      error.data = data;
      throw error;
    }
    return data;
  }

  async function ensureSession() {
    if (sessionToken) return sessionToken;
    const data = await api(`/qr/${config.qrToken}/sessions/`, {
      method: "POST",
      body: JSON.stringify({ language: config.language }),
    });
    sessionToken = data.session_token;
    sessionStorage.setItem(`reviewflow:${config.qrToken}:session`, sessionToken);
    return sessionToken;
  }

  function renderQuestions() {
    config.questions.forEach((question) => {
      const wrapper = document.createElement("fieldset");
      wrapper.className = "question";
      wrapper.innerHTML = `<legend class="question-title"><span>${question.label}</span>${question.required ? '<span aria-label="required">*</span>' : ""}</legend><div class="stars" role="radiogroup" aria-label="${question.label}"></div>`;
      const stars = wrapper.querySelector(".stars");
      for (let value = question.min; value <= question.max; value += 1) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "star";
        button.textContent = String(value);
        button.setAttribute("aria-label", `${value} out of ${question.max}`);
        button.setAttribute("aria-pressed", "false");
        button.addEventListener("click", () => {
          ratings.set(question.id, value);
          [...stars.children].forEach((item, index) => item.setAttribute("aria-pressed", String(index + question.min === value)));
        });
        stars.appendChild(button);
      }
      qRoot.appendChild(wrapper);
    });
  }

  function validateRatings() {
    const missing = config.questions.filter((q) => q.required && !ratings.has(q.id));
    if (missing.length) throw new Error(`Please rate: ${missing.map((q) => q.label).join(", ")}.`);
  }

  function showManualFallback(message) {
    questionnaire.hidden = true;
    suggestions.hidden = false;
    draftCards.innerHTML = "";
    actionError.textContent = message;
    finalText.placeholder = "Write or paste your own review based on your experience";
    finalText.focus();
  }

  function renderDrafts(drafts) {
    draftCards.innerHTML = "";
    drafts.forEach((draft) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "draft-card";
      button.innerHTML = `<strong class="draft-label">${draft.style}</strong><span>${draft.text}</span>`;
      button.addEventListener("click", () => {
        if (edited && finalText.value.trim() && !confirm("Replace your edits with this suggestion?")) return;
        selectedDraftId = draft.id;
        edited = false;
        finalText.value = draft.text;
        copyButton.disabled = false;
        [...draftCards.children].forEach((card) => card.classList.remove("selected"));
        button.classList.add("selected");
      });
      draftCards.appendChild(button);
    });
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    formError.textContent = "";
    const generateButton = document.getElementById("generate-button");
    try {
      validateRatings();
      generateButton.disabled = true;
      generateButton.textContent = "Generating…";
      await ensureSession();
      await api(`/sessions/${sessionToken}/feedback/`, {
        method: "POST",
        body: JSON.stringify({
          answers: [...ratings].map(([question_id, rating]) => ({ question_id, rating })),
          optional_comment: comment.value.trim(),
          idempotency_key: feedbackKey,
        }),
      });
      const result = await api(`/sessions/${sessionToken}/generate/`, { method: "POST", body: "{}" });
      questionnaire.hidden = true;
      suggestions.hidden = false;
      renderDrafts(result.drafts);
      suggestions.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (error) {
      if (error.status === 503 || error.status === 429) showManualFallback(error.message);
      else formError.textContent = error.message;
    } finally {
      generateButton.disabled = false;
      generateButton.textContent = "Generate review suggestions";
    }
  });

  finalText.addEventListener("input", () => {
    edited = true;
    copyButton.disabled = !finalText.value.trim();
  });

  async function recordEvent(eventType) {
    await api(`/sessions/${sessionToken}/events/`, {
      method: "POST",
      body: JSON.stringify({ event_type: eventType, idempotency_key: uuid() }),
    });
  }

  async function copyAndOpen() {
    actionError.textContent = "";
    manualCopy.hidden = true;
    const text = finalText.value.trim();
    if (!text) return;
    copyButton.disabled = true;
    try {
      await api(`/sessions/${sessionToken}/select/`, {
        method: "POST",
        body: JSON.stringify({ draft_id: selectedDraftId, final_text: text }),
      });
      if (edited) await recordEvent("draft_edited").catch(() => undefined);
    } catch (error) {
      actionError.textContent = "Unable to save the final text. Check your connection and try again.";
      copyButton.disabled = false;
      return;
    }

    try {
      await navigator.clipboard.writeText(text);
    } catch (error) {
      await recordEvent("copy_failed").catch(() => undefined);
      actionError.textContent = "The review was not copied. Use retry or copy it manually.";
      retryButton.hidden = false;
      manualCopy.hidden = false;
      copyButton.disabled = false;
      return;
    }

    sessionStorage.setItem(`reviewflow:${config.qrToken}:finalText`, text);
    await recordEvent("copy_succeeded").catch(() => undefined);
    await recordEvent("google_open_clicked").catch(() => undefined);
    window.location.assign(config.googleReviewUrl);
  }

  copyButton.addEventListener("click", copyAndOpen);
  retryButton.addEventListener("click", copyAndOpen);

  const restored = sessionStorage.getItem(`reviewflow:${config.qrToken}:finalText`);
  if (restored) finalText.value = restored;
  renderQuestions();
  ensureSession().catch(() => { formError.textContent = "Unable to start the feedback session. Check your connection."; });
})();
