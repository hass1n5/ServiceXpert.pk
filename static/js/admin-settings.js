/* Settings page: theme swatches and live font preview.

   The catalogue has 130+ families, so nothing is loaded up front — the
   stylesheet for a family is injected only when it gets picked. */

(function () {
  "use strict";

  /* ------------------------------------------------------------- themes */

  document.querySelectorAll(".theme-card input[name='theme']").forEach((radio) => {
    radio.addEventListener("change", () => {
      document.querySelectorAll(".theme-card").forEach((card) => card.classList.remove("on"));
      if (radio.checked) radio.closest(".theme-card").classList.add("on");
    });
  });

  /* -------------------------------------------------------------- fonts */

  const catalogue = (() => {
    const tag = document.getElementById("fontCatalogue");
    try {
      return JSON.parse(tag?.textContent || "[]");
    } catch (_) {
      return [];
    }
  })();

  const byName = new Map(catalogue.map((font) => [font.name, font]));
  const loaded = new Set();

  const FALLBACKS = {
    sans: "ui-sans-serif, system-ui, sans-serif",
    display: '"Trebuchet MS", ui-sans-serif, sans-serif',
    serif: "ui-serif, Georgia, serif",
    hand: '"Segoe Script", cursive',
    mono: 'ui-monospace, Menlo, monospace',
    urdu: '"Noto Naskh Arabic", serif',
  };

  function load(name) {
    const font = byName.get(name);
    if (!font || loaded.has(name)) return;
    loaded.add(name);

    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href =
      "https://fonts.googleapis.com/css2?family=" +
      encodeURIComponent(font.name).replace(/%20/g, "+") +
      ":wght@" +
      font.weights +
      "&display=swap";
    document.head.appendChild(link);
  }

  function stack(name) {
    const font = byName.get(name);
    if (!font) return FALLBACKS.sans;
    return `"${font.name}", ${FALLBACKS[font.group] || FALLBACKS.sans}`;
  }

  function apply(select) {
    const target = document.getElementById(select.dataset.preview);
    if (!target) return;
    load(select.value);
    target.style.fontFamily = stack(select.value);
  }

  document.querySelectorAll("[data-font-select]").forEach((select) => {
    apply(select);
    select.addEventListener("change", () => apply(select));
  });
})();
