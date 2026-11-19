/* Shared admin panel helpers. Loaded on every admin page. */

window.Admin = (function () {
  "use strict";

  const csrf = document.querySelector('meta[name="csrf-token"]')?.content || "";

  function toast(text, isError) {
    const host = document.getElementById("toasts");
    if (!host) return;
    const el = document.createElement("div");
    el.className = "toast" + (isError ? " error" : "");
    el.textContent = text;
    host.appendChild(el);
    setTimeout(() => el.remove(), 5000);
  }

  document.querySelectorAll("#toasts .toast").forEach((el) => {
    setTimeout(() => el.remove(), 5000);
  });

  /** fetch wrapper that adds the CSRF header and unwraps API errors. */
  async function api(url, options = {}) {
    const response = await fetch(url, {
      headers: { "Content-Type": "application/json", "X-CSRF-Token": csrf },
      ...options,
    });

    let payload = {};
    try {
      payload = await response.json();
    } catch (_) {
      payload = {};
    }

    if (!response.ok) {
      throw new Error(payload.error || `Request fail ho gayi (${response.status}).`);
    }
    return payload;
  }

  /** Runs an action, shows the result as a toast, optionally reloads. */
  async function run(fn, { reload = false } = {}) {
    try {
      const payload = await fn();
      if (payload?.message) toast(payload.message);
      if (reload) setTimeout(() => window.location.reload(), 350);
      return payload;
    } catch (error) {
      toast(error.message, true);
      throw error;
    }
  }

  function openModal(dialog) {
    if (dialog && !dialog.open) dialog.showModal();
  }

  function closeModal(dialog) {
    if (dialog?.open) dialog.close();
  }

  function showError(dialog, text) {
    const box = dialog?.querySelector("[data-error]");
    if (!box) return;
    box.textContent = text || "";
    box.hidden = !text;
  }

  /* Sidebar on small screens */
  document.querySelectorAll("[data-toggle-nav]").forEach((button) => {
    button.addEventListener("click", () => document.body.classList.toggle("nav-open"));
  });
  document.querySelectorAll("[data-close-nav]").forEach((el) => {
    el.addEventListener("click", () => document.body.classList.remove("nav-open"));
  });

  /* Any button marked data-close-modal closes its own dialog */
  document.addEventListener("click", (event) => {
    const button = event.target.closest("[data-close-modal]");
    if (button) closeModal(button.closest("dialog"));
  });

  return { api, run, toast, openModal, closeModal, showError, csrf };
})();
