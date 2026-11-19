/**
 * Sparkle Bot — a free, no-API-key "smart bot" for the WhatsApp chat widget.
 *
 * It reads the service catalogue rendered into #waBotData and answers common
 * questions (price, hours, address, a named service) directly in the widget.
 * Anything it can't confidently answer gets a "forward to WhatsApp" button so
 * a human can take over — the bot never leaves a customer stuck.
 *
 * Exposed as `window.SparkleBot`. Also exported via module.exports when run
 * under Node (no `window`), so the matching logic can be unit-tested without
 * a browser/DOM.
 */
(function (root) {
  "use strict";

  /* ---------------------------------------------------------- utilities */

  function escapeRegExp(str) {
    return String(str).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  /**
   * True if `phrase` appears in `text` as a whole word/phrase — not as a
   * substring of a larger word. This is what the old version got wrong:
   * a plain `text.includes("hi")` also matched inside "bhi" (Urdu for
   * "also"), "yahi", "sahi", etc. Boundaries are defined as "start/end of
   * string" or "any character that isn't a-z/0-9", so "hi" only matches a
   * standalone word, never a chunk of a longer one.
   */
  function hasWord(text, phrase) {
    const escaped = escapeRegExp(phrase).replace(/\s+/g, "\\s+");
    const re = new RegExp(`(^|[^a-z0-9])${escaped}([^a-z0-9]|$)`, "i");
    return re.test(text);
  }

  function hasAnyWord(text, phrases) {
    return phrases.some((p) => hasWord(text, p));
  }

  function formatPKR(amount) {
    const n = Number(amount) || 0;
    return `Rs ${n.toLocaleString("en-PK")}`;
  }

  /* --------------------------------------------------------- keyword sets */

  const GREETINGS = [
    "hi", "hii", "hiii", "hello", "hey", "salam", "salaam", "slm",
    "asalam", "assalam", "asalamalaikum", "assalamualaikum",
    "assalamoalaikum", "aoa", "good morning", "good evening", "good afternoon",
  ];

  const THANKS = ["thanks", "thank you", "thankyou", "shukriya", "shukria", "mehrbani"];

  const PRICE_WORDS = [
    "price", "prices", "pricing", "rate", "rates", "cost", "costs",
    "charge", "charges", "fee", "fees", "kitna", "kitne", "kitni", "kya rate",
  ];

  const HOURS_WORDS = [
    "hours", "hour", "timing", "timings", "time", "kab", "khulte", "khulty",
    "band", "open", "close",
  ];

  const LOCATION_WORDS = [
    "address", "location", "kahan", "kaha", "office", "branch", "shop", "area",
  ];

  const BOOKING_WORDS = [
    "book", "booking", "appointment", "order", "schedule", "confirm",
  ];

  const LIST_WORDS = [
    "services", "service", "list", "menu", "options", "kya kya", "which services",
  ];

  const HUMAN_WORDS = ["human", "agent", "team", "banda", "insan", "call me", "call"];

  /* ------------------------------------------------------------- catalog */

  function loadCatalog() {
    if (typeof document === "undefined") return { services: [], brand: "", whatsapp: "" };
    const el = document.getElementById("waBotData");
    if (!el) return { services: [], brand: "", whatsapp: "" };
    try {
      const data = JSON.parse(el.textContent || "{}");
      return {
        brand: data.brand || "",
        whatsapp: data.whatsapp || "",
        phone: data.phone || "",
        address: data.address || "",
        city: data.city || "",
        hours: data.hours || "",
        services: Array.isArray(data.services) ? data.services : [],
      };
    } catch (err) {
      return { services: [], brand: "", whatsapp: "" };
    }
  }

  /** Find the service the customer is most likely asking about, if any. */
  function findService(text, services) {
    let best = null;
    for (const svc of services) {
      if (!svc.name) continue;
      if (hasWord(text, svc.name)) {
        // Prefer the longest/most specific name match (e.g. "Sofa Deep
        // Cleaning" over a shorter category-ish word that also matched).
        if (!best || svc.name.length > best.name.length) best = svc;
      }
    }
    return best;
  }

  function findCategory(text, services) {
    const seen = new Map();
    for (const svc of services) {
      if (!svc.category || seen.has(svc.category)) continue;
      seen.set(svc.category, true);
      if (hasWord(text, svc.category)) return svc.category;
    }
    return null;
  }

  /* --------------------------------------------------------------- reply */

  /**
   * Build a reply for one incoming message.
   * Returns { lines: string[], offerHuman: boolean, matched: boolean }.
   *   lines       — one or more sentences to show as separate bot bubbles.
   *   offerHuman  — whether to show the "forward to WhatsApp" CTA.
   *   matched     — false only for the pure fallback (bot didn't understand).
   */
  function reply(rawText, catalog) {
    const text = String(rawText || "").trim();
    const data = catalog || loadCatalog();
    const services = data.services || [];

    if (!text) {
      return { lines: ["Which service would you like to know about?"], offerHuman: false, matched: false };
    }

    // 1. A specific named service — the most useful answer we can give.
    const service = findService(text, services);
    if (service) {
      const lines = [];
      const priceLine = service.price_from
        ? `${service.name}: starting from ${formatPKR(service.price_from)}${service.duration ? `, estimated duration ${service.duration}` : ""}.`
        : `${service.name} is available. Our team will confirm the exact price.`;
      lines.push(priceLine);
      if (service.summary) lines.push(service.summary);
      return { lines, offerHuman: true, matched: true, service };
    }

    // 2. A category name ("pest control", "deep cleaning" etc).
    const category = findCategory(text, services);
    if (category) {
      const inCat = services.filter((s) => s.category === category).slice(0, 4);
      const names = inCat.map((s) => `${s.name} (${formatPKR(s.price_from)} se)`).join(", ");
      return {
        lines: [`${category} mein ye services hain: ${names}.`],
        offerHuman: true,
        matched: true,
      };
    }

    // 3. General price question with no specific service named.
    if (hasAnyWord(text, PRICE_WORDS)) {
      const cheapest = services.filter((s) => s.price_from).sort((a, b) => a.price_from - b.price_from)[0];
      const lines = cheapest
        ? [`Rates vary by service — starting from ${formatPKR(cheapest.price_from)}. Which service would you like pricing for?`]
        : ["Pricing depends on the service. Which service would you like to know about?"];
      return { lines, offerHuman: true, matched: true };
    }

    // 4. Business hours.
    if (hasAnyWord(text, HOURS_WORDS)) {
      return {
        lines: [data.hours ? `Our business hours are: ${data.hours}.` : "Our team can confirm the business hours."],
        offerHuman: false,
        matched: true,
      };
    }

    // 5. Address / location.
    if (hasAnyWord(text, LOCATION_WORDS)) {
      const where = [data.address, data.city].filter(Boolean).join(", ");
      return {
        lines: [where ? `Our location is: ${where}.` : "Our team can share the location on WhatsApp."],
        offerHuman: !where,
        matched: true,
      };
    }

    // 6. Wants to book.
    if (hasAnyWord(text, BOOKING_WORDS)) {
      return {
        lines: ["Absolutely — you can confirm a booking using the 'Get a free quote' form below or via WhatsApp."],
        offerHuman: true,
        matched: true,
      };
    }

    // 7. Wants the full service list.
    if (hasAnyWord(text, LIST_WORDS)) {
      const names = services.slice(0, 6).map((s) => s.name).join(", ");
      return {
        lines: [names ? `Our services: ${names}.` : "Service details are available on the website."],
        offerHuman: true,
        matched: true,
      };
    }

    // 8. Explicitly wants a human.
    if (hasAnyWord(text, HUMAN_WORDS)) {
      return { lines: ["Sure — I will connect you with our team on WhatsApp."], offerHuman: true, matched: true };
    }

    // 9. Thanks.
    if (hasAnyWord(text, THANKS)) {
      return { lines: ["You’re welcome! Let me know if you have another question."], offerHuman: false, matched: true };
    }

    // 10. Greeting — but only when the message is *just* a greeting, so
    // "hi, pest control ka rate?" still falls through to the price match
    // above instead of getting stuck on a plain hello.
    if (hasAnyWord(text, GREETINGS) && text.split(/\s+/).length <= 3) {
      const greetName = data.brand ? ` ${data.brand} ` : " ";
      return {
        lines: [`Hello! How can we help you? Enter a service name or ask a question.`],
        offerHuman: false,
        matched: true,
      };
    }

    // 11. Fallback — bot genuinely doesn't know; hand off to a human.
    return {
      lines: ["I’m not sure I understood that. I can connect you with our team on WhatsApp for help."],
      offerHuman: true,
      matched: false,
    };
  }

  const SparkleBot = { reply, loadCatalog, hasWord, hasAnyWord, findService, findCategory, formatPKR };

  if (typeof module !== "undefined" && module.exports) {
    module.exports = SparkleBot;
  }
  if (root) {
    root.SparkleBot = SparkleBot;
  }
})(typeof window !== "undefined" ? window : null);
