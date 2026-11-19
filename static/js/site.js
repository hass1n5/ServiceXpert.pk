/* Sparkle Care — public site behaviour */

(function () {
  "use strict";

  const csrf = document.querySelector('meta[name="csrf-token"]')?.content || "";

  /* ------------------------------------------------------------ toasts */

  function toast(text, isError) {
    const host = document.getElementById("toasts");
    if (!host) return;
    const el = document.createElement("div");
    el.className = "toast" + (isError ? " error" : "");
    el.textContent = text;
    host.appendChild(el);
    setTimeout(() => el.remove(), 5200);
  }

  document.querySelectorAll("#toasts .toast").forEach((el) => {
    setTimeout(() => el.remove(), 5200);
  });

  /* --------------------------------------------------------- mobile nav */

  const burger = document.getElementById("burger");
  const hasMobileChildNav = !!document.getElementById("mobileNav");

  // The mobile child theme owns the mobile drawer completely. The legacy
  // body.menu-open drawer is disabled whenever #mobileNav exists.
  function closeLegacyMobileMenu() {
    if (hasMobileChildNav) return;
    document.body.classList.remove("menu-open");
    burger?.setAttribute("aria-expanded", "false");
  }

  if (burger && !hasMobileChildNav) {
    burger.addEventListener("click", () => {
      const open = document.body.classList.toggle("menu-open");
      burger.setAttribute("aria-expanded", String(open));
    });

    document.addEventListener("click", (event) => {
      if (
        document.body.classList.contains("menu-open") &&
        !event.target.closest(".main-nav") &&
        !event.target.closest("#burger")
      ) {
        closeLegacyMobileMenu();
      }
    });

    document.querySelectorAll(".main-nav > a, .dropdown-menu a").forEach((link) => {
      link.addEventListener("click", closeLegacyMobileMenu);
    });
  }

  /* ---------------------------------------------------------- dropdowns */

  document.querySelectorAll("[data-dropdown]").forEach((drop) => {
    const button = drop.querySelector("button");
    button.addEventListener("click", (event) => {
      event.stopPropagation();
      const open = drop.classList.toggle("open");
      button.setAttribute("aria-expanded", String(open));
    });
  });

  document.addEventListener("click", (event) => {
    document.querySelectorAll("[data-dropdown].open").forEach((drop) => {
      if (!drop.contains(event.target)) {
        drop.classList.remove("open");
        drop.querySelector("button")?.setAttribute("aria-expanded", "false");
      }
    });
  });

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    document.querySelectorAll("[data-dropdown].open").forEach((d) => d.classList.remove("open"));
    closeLegacyMobileMenu();
  });

  /* -------------------------------------------------- service tab filter */

  const tabs = document.querySelectorAll(".tab[data-filter]");
  const grid = document.getElementById("serviceGrid");

  if (tabs.length && grid) {
    tabs.forEach((tab) => {
      tab.addEventListener("click", () => {
        tabs.forEach((t) => {
          t.classList.remove("on");
          t.setAttribute("aria-selected", "false");
        });
        tab.classList.add("on");
        tab.setAttribute("aria-selected", "true");

        const want = tab.dataset.filter;
        grid.querySelectorAll(".service-card").forEach((card) => {
          const show = want === "all" || card.dataset.category === want;
          card.style.display = show ? "" : "none";
        });
      });
    });
  }

  /* ------------------------------------------------------- booking form */

  function readForm(form) {
    const data = {};
    form.querySelectorAll("input, select, textarea").forEach((el) => {
      if (el.name) data[el.name] = el.value.trim();
    });
    data.source = form.dataset.source || "website";
    return data;
  }

  document.querySelectorAll("[data-booking-form]").forEach((form) => {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();

      const button = form.querySelector('button[type="submit"]');
      const label = button?.querySelector("[data-label]");
      const msg = form.querySelector("[data-msg]");
      const original = label ? label.textContent : "";

      if (button) button.disabled = true;
      if (label) label.textContent = "Bheja ja raha hai...";
      if (msg) msg.hidden = true;

      try {
        const response = await fetch("/book", {
          method: "POST",
          headers: { "Content-Type": "application/json", "X-CSRF-Token": csrf },
          body: JSON.stringify(readForm(form)),
        });

        const payload = await response.json();

        if (!response.ok) {
          throw new Error(payload.error || "There was a problem submitting your request.");
        }

        if (msg) {
          msg.className = "form-msg ok";
          msg.textContent = payload.message;
          msg.hidden = false;
        }
        toast(payload.message);
        form.reset();

        // Hand the enquiry to WhatsApp. Opened after the save, so the record
        // survives even if the customer closes the WhatsApp tab.
        if (payload.whatsapp_url) {
          window.open(payload.whatsapp_url, "_blank", "noopener");
        }
      } catch (error) {
        if (msg) {
          msg.className = "form-msg bad";
          msg.textContent = error.message;
          msg.hidden = false;
        }
        toast(error.message, true);
      } finally {
        if (button) button.disabled = false;
        if (label) label.textContent = original;
      }
    });
  });
})();

/* Sparkle Care — motion: scroll reveals and counting stats */

(function () {
  "use strict";

  document.documentElement.classList.remove("no-js");

  const still = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ------------------------------------------------------------ reveals */

  const targets = document.querySelectorAll("[data-reveal]");

  if (still || !("IntersectionObserver" in window)) {
    targets.forEach((el) => el.classList.add("revealed"));
  } else {
    // Children of the same parent come in one after another, not all at once.
    const seen = new Map();
    targets.forEach((el) => {
      const parent = el.parentElement;
      const index = seen.get(parent) || 0;
      seen.set(parent, index + 1);
      el.style.setProperty("--reveal-delay", `${Math.min(index, 6) * 70}ms`);
    });

    const watcher = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("revealed");
          watcher.unobserve(entry.target);
        });
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.12 }
    );

    targets.forEach((el) => watcher.observe(el));
  }

  /* ----------------------------------------------------------- counters */

  function format(value, decimals) {
    return decimals
      ? value.toFixed(decimals)
      : Math.round(value).toLocaleString("en-US");
  }

  function countUp(el) {
    const target = parseFloat(el.dataset.count);
    if (!isFinite(target)) return;

    const decimals = parseInt(el.dataset.decimals || "0", 10);
    const prefix = el.dataset.prefix || "";
    const suffix = el.dataset.suffix || "";

    if (still) {
      el.textContent = prefix + format(target, decimals) + suffix;
      return;
    }

    const duration = 1100;
    const start = performance.now();

    function frame(now) {
      const progress = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = prefix + format(target * eased, decimals) + suffix;
      if (progress < 1) requestAnimationFrame(frame);
    }

    requestAnimationFrame(frame);
  }

  const counters = document.querySelectorAll("[data-count]");

  if (!("IntersectionObserver" in window)) {
    counters.forEach(countUp);
  } else {
    const watcher = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          countUp(entry.target);
          watcher.unobserve(entry.target);
        });
      },
      { threshold: 0.4 }
    );
    counters.forEach((el) => watcher.observe(el));
  }
})();


/* Sparkle Care — WhatsApp chat widget */

(function () {
  "use strict";

  const chat = document.getElementById("waChat");
  if (!chat) return;

  const panel = document.getElementById("waPanel");
  const launch = document.getElementById("waLaunch");
  const badge = document.getElementById("waBadge");
  const typing = document.getElementById("waTyping");
  const greeting = document.getElementById("waGreeting");
  const chips = document.getElementById("waChips");
  const thread = document.getElementById("waThread");
  const form = document.getElementById("waForm");
  const nameField = document.getElementById("waName");
  const textField = document.getElementById("waText");

  const number = chat.dataset.number || "";
  let greeted = false;

  function clock() {
    return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }

  function greet() {
    if (greeted) return;
    greeted = true;

    const delay = window.matchMedia("(prefers-reduced-motion: reduce)").matches ? 0 : 750;

    setTimeout(() => {
      if (typing) typing.hidden = true;
      if (greeting) {
        const stamp = greeting.querySelector("[data-wa-clock]");
        if (stamp) stamp.textContent = clock();
        greeting.hidden = false;
      }
      if (chips) chips.hidden = false;
      if (thread) thread.scrollTop = thread.scrollHeight;
    }, delay);
  }

  function open() {
    chat.classList.add("open");
    panel.hidden = false;
    launch.setAttribute("aria-expanded", "true");
    if (badge) badge.hidden = true;
    greet();
    setTimeout(() => textField?.focus(), 260);
  }

  function shut() {
    chat.classList.remove("open");
    panel.hidden = true;
    launch.setAttribute("aria-expanded", "false");
  }

  launch.addEventListener("click", () => (panel.hidden ? open() : shut()));

  document.querySelectorAll("[data-wa-close]").forEach((button) => {
    button.addEventListener("click", shut);
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !panel.hidden) {
      shut();
      launch.focus();
    }
  });

  /* Quick replies drop straight into the box so nothing is sent blind. */
  chips?.querySelectorAll("[data-wa-chip]").forEach((chip) => {
    chip.addEventListener("click", () => {
      const service = chip.dataset.waChip;
      textField.value = `I would like information about ${service}.`;
      textField.focus();
      textField.dispatchEvent(new Event("input"));
    });
  });

  /* Textarea grows with the message, up to the CSS max-height. */
  textField?.addEventListener("input", () => {
    textField.style.height = "auto";
    textField.style.height = `${textField.scrollHeight}px`;
  });

  textField?.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      form.requestSubmit();
    }
  });

  /* ---------------------------------------------- Sparkle Bot integration */

  const catalog = window.SparkleBot ? window.SparkleBot.loadCatalog() : { services: [] };

  function appendBubble(text, outgoing) {
    if (!thread) return;
    const wrap = document.createElement("div");
    wrap.className = outgoing ? "wa-bubble-out" : "wa-bubble";

    const p = document.createElement("p");
    p.textContent = text;
    wrap.appendChild(p);

    const time = document.createElement("time");
    time.textContent = clock();
    wrap.appendChild(time);

    thread.appendChild(wrap);
    thread.scrollTop = thread.scrollHeight;
    return wrap;
  }

  function appendHandoffCta(promptText) {
    if (!thread) return;
    const holder = document.createElement("div");
    holder.className = "wa-bubble";

    const p = document.createElement("p");
    p.textContent = promptText;
    holder.appendChild(p);

    const cta = document.createElement("button");
    cta.type = "button";
    cta.className = "wa-bubble-cta";
    cta.textContent = "Send to our team on WhatsApp";
    cta.addEventListener("click", () => {
      sendToWhatsApp(lastCustomerMessage);
      cta.disabled = true;
      cta.textContent = "WhatsApp opened \u2713";
    });
    holder.appendChild(cta);

    thread.appendChild(holder);
    thread.scrollTop = thread.scrollHeight;
  }

  let lastCustomerMessage = "";

  function sendToWhatsApp(message) {
    if (!number) return;
    const who = (nameField.value || "").trim();
    const lines = ["Hello!", "", message];
    if (who) lines.push("", `Naam: ${who}`);
    lines.push("", `(${window.location.href})`);

    window.open(
      `https://wa.me/${number}?text=${encodeURIComponent(lines.join("\n"))}`,
      "_blank",
      "noopener"
    );
  }

  form?.addEventListener("submit", (event) => {
    event.preventDefault();

    const message = (textField.value || "").trim();
    if (!message) {
      textField.focus();
      return;
    }

    lastCustomerMessage = message;
    appendBubble(message, true);
    textField.value = "";
    textField.style.height = "auto";

    if (!window.SparkleBot) {
      // Bot script failed to load — fall back to the old direct-forward
      // behaviour so a message is never silently lost.
      sendToWhatsApp(message);
      return;
    }

    if (typing) typing.hidden = false;
    if (chips) chips.hidden = true;
    thread.scrollTop = thread.scrollHeight;

    const delay = window.matchMedia("(prefers-reduced-motion: reduce)").matches ? 0 : 550;
    setTimeout(() => {
      if (typing) typing.hidden = true;

      const result = window.SparkleBot.reply(message, catalog);
      result.lines.forEach((line) => appendBubble(line, false));

      if (result.offerHuman) {
        appendHandoffCta(
          result.matched
            ? "Agar chahein to yehi baat direct team se WhatsApp par bhi kar sakte hain:"
            : "Chahein to WhatsApp par team se seedha baat kar sakte hain:"
        );
      }
    }, delay);
  });
})();


/* ServiceXpert premium sliders */
(function(){
  "use strict";
  const reduce=window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  function slider(trackId, prevSel, nextSel, progressId, autoplay){
    const track=document.getElementById(trackId); if(!track) return;
    const prev=document.querySelector(prevSel), next=document.querySelector(nextSel), prog=document.querySelector('#'+progressId+' span');
    const items=[...track.children]; if(!items.length) return;
    let index=0, timer;
    const step=()=>{const first=items[0]; const gap=parseFloat(getComputedStyle(track).gap)||0; return first.getBoundingClientRect().width+gap};
    function update(){
      const max=Math.max(0,track.scrollWidth-track.clientWidth); const x=Math.min(max,index*step()); track.scrollTo({left:x,behavior:reduce?'auto':'smooth'}); if(prog){const pct=max?Math.min(100,((x+track.clientWidth)/track.scrollWidth)*100):100;prog.style.width=pct+'%';}
    }

    // Native-feeling swipe on phones/tablets.
    let touchStartX = 0;
    track.addEventListener('touchstart', e => { touchStartX = e.touches[0].clientX; }, {passive:true});
    track.addEventListener('touchend', e => {
      const dx = e.changedTouches[0].clientX - touchStartX;
      if (Math.abs(dx) < 45) return;
      dx < 0 ? nextFn() : prevFn();
    }, {passive:true});
    function nextFn(){index++; const max=Math.max(0,track.scrollWidth-track.clientWidth); if(index*step()>max+8) index=0; update();}
    function prevFn(){index=Math.max(0,index-1); update();}
    next?.addEventListener('click',nextFn); prev?.addEventListener('click',prevFn);
    window.addEventListener('resize',()=>{index=0;update()});
    if(autoplay&&!reduce){timer=setInterval(nextFn,5200); [track,prev,next].forEach(el=>el?.addEventListener('mouseenter',()=>clearInterval(timer))); [track,prev,next].forEach(el=>el?.addEventListener('mouseleave',()=>{clearInterval(timer);timer=setInterval(nextFn,5200)}));}
    update();
  }
  slider('serviceTrack','.service-prev','.service-next','serviceProgress',true);
  slider('reviewTrack','.review-prev','.review-next','reviewProgress',true);

  const slides=[...document.querySelectorAll('.hero-slide')], dots=[...document.querySelectorAll('.hero-dot')];
  if(slides.length){let i=0,timer; const show=n=>{i=(n+slides.length)%slides.length;slides.forEach((s,k)=>s.classList.toggle('is-active',k===i));dots.forEach((d,k)=>d.classList.toggle('active',k===i));}; const go=n=>{show(n);restart()}; const restart=()=>{if(reduce)return;clearInterval(timer);timer=setInterval(()=>show(i+1),6500)}; document.getElementById('heroPrev')?.addEventListener('click',()=>go(i-1));document.getElementById('heroNext')?.addEventListener('click',()=>go(i+1));dots.forEach(d=>d.addEventListener('click',()=>go(Number(d.dataset.slideTo))));show(0);restart(); const hero=document.querySelector('.hero-slider'); hero?.addEventListener('mouseenter',()=>clearInterval(timer));hero?.addEventListener('mouseleave',restart);}
})();
