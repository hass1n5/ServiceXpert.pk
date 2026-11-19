/* ServiceXpert.pk — Mobile Child Theme v6 navigation */
(function () {
  "use strict";

  function init() {
    const burger = document.getElementById("burger");
    const nav = document.getElementById("mobileNav");
    const backdrop = document.getElementById("mobileNavBackdrop");
    const closeBtn = document.getElementById("mobileNavClose");
    if (!burger || !nav || !backdrop) return;

    const mq = window.matchMedia("(max-width: 860px)");
    let lastFocus = null;

    function mobile() { return mq.matches; }

    function close(restore) {
      nav.classList.remove("is-open");
      document.documentElement.classList.remove("mobile-nav-open");
      nav.setAttribute("aria-hidden", "true");
      burger.setAttribute("aria-expanded", "false");
      burger.setAttribute("aria-label", "Open menu");
      backdrop.hidden = true;
      document.body.classList.remove("mobile-menu-open");
      if (restore && lastFocus && typeof lastFocus.focus === "function") {
        try { lastFocus.focus({preventScroll:true}); } catch (_) { try { lastFocus.focus(); } catch (__) {} }
      }
    }

    function open() {
      if (!mobile()) return;
      lastFocus = document.activeElement;
      nav.classList.add("is-open");
      nav.setAttribute("aria-hidden", "false");
      burger.setAttribute("aria-expanded", "true");
      burger.setAttribute("aria-label", "Close menu");
      backdrop.hidden = false;
      document.documentElement.classList.add("mobile-nav-open");
      document.body.classList.add("mobile-menu-open");
      requestAnimationFrame(function () { closeBtn && closeBtn.focus(); });
    }

    function toggle(event) {
      event.preventDefault();
      event.stopPropagation();
      if (nav.classList.contains("is-open")) close(true);
      else open();
    }

    burger.addEventListener("click", toggle, {passive:false});
    closeBtn?.addEventListener("click", function (event) {
      event.preventDefault();
      event.stopPropagation();
      close(true);
    }, {passive:false});
    backdrop.addEventListener("click", function () { close(false); });

    nav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () { close(false); });
    });

    nav.querySelectorAll("details").forEach(function (details) {
      details.addEventListener("toggle", function () {
        if (!details.open) return;
        nav.querySelectorAll("details").forEach(function (other) {
          if (other !== details) other.removeAttribute("open");
        });
      });
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && nav.classList.contains("is-open")) {
        event.preventDefault();
        close(true);
      }
    });

    window.addEventListener("resize", function () {
      if (!mobile()) close(false);
    });

    close(false);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init, {once:true});
  else init();
})();

/* ServiceXpert Mobile Child Theme v6 — isolated home sliders */
(function () {
  "use strict";

  function initMobileHomeSliders() {
    if (!document.querySelector(".mobile-home")) return;
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    function heroSlider() {
      const root = document.querySelector(".mhero-slider");
      if (!root) return;
      const slides = [...root.querySelectorAll(".mhero-slide")];
      const dots = [...root.querySelectorAll(".mhero-dot")];
      const prev = root.querySelector("#mHeroPrev");
      const next = root.querySelector("#mHeroNext");
      if (!slides.length) return;
      let index = 0, timer = null, touchStartX = 0;

      function show(nextIndex) {
        index = (nextIndex + slides.length) % slides.length;
        slides.forEach((slide, i) => slide.classList.toggle("is-active", i === index));
        dots.forEach((dot, i) => {
          dot.classList.toggle("active", i === index);
          dot.setAttribute("aria-current", i === index ? "true" : "false");
        });
      }
      function restart() {
        if (reduce) return;
        clearInterval(timer);
        timer = setInterval(() => show(index + 1), 6200);
      }
      function go(delta) { show(index + delta); restart(); }

      prev?.addEventListener("click", () => go(-1));
      next?.addEventListener("click", () => go(1));
      dots.forEach(dot => dot.addEventListener("click", () => { show(Number(dot.dataset.mheroTo || 0)); restart(); }));
      root.addEventListener("touchstart", e => { touchStartX = e.touches[0].clientX; }, {passive:true});
      root.addEventListener("touchend", e => {
        const dx = e.changedTouches[0].clientX - touchStartX;
        if (Math.abs(dx) >= 45) go(dx < 0 ? 1 : -1);
      }, {passive:true});
      root.addEventListener("mouseenter", () => clearInterval(timer));
      root.addEventListener("mouseleave", restart);
      show(0);
      restart();
    }

    function trackSlider(trackId, prevId, nextId, progressId, interval) {
      const track = document.getElementById(trackId);
      if (!track) return;
      const items = [...track.children];
      if (!items.length) return;
      const prev = document.getElementById(prevId);
      const next = document.getElementById(nextId);
      const progress = document.querySelector(`#${progressId} span`);
      let index = 0, timer = null, touchStartX = 0;

      function step() {
        const item = items[0];
        if (!item) return 0;
        const gap = parseFloat(getComputedStyle(track).gap) || 0;
        return item.getBoundingClientRect().width + gap;
      }
      function maxScroll() { return Math.max(0, track.scrollWidth - track.clientWidth); }
      function update(behavior) {
        const max = maxScroll();
        const x = Math.min(max, index * step());
        track.scrollTo({left:x, behavior:behavior || (reduce ? "auto" : "smooth")});
        if (progress) {
          const pages = Math.max(1, items.length);
          const pct = Math.min(100, ((index + 1) / pages) * 100);
          progress.style.width = `${pct}%`;
        }
      }
      function go(delta) {
        index = (index + delta + items.length) % items.length;
        update();
        restart();
      }
      function restart() {
        if (reduce) return;
        clearInterval(timer);
        timer = setInterval(() => go(1), interval);
      }

      prev?.addEventListener("click", () => go(-1));
      next?.addEventListener("click", () => go(1));
      track.addEventListener("touchstart", e => { touchStartX = e.touches[0].clientX; }, {passive:true});
      track.addEventListener("touchend", e => {
        const dx = e.changedTouches[0].clientX - touchStartX;
        if (Math.abs(dx) >= 45) go(dx < 0 ? 1 : -1);
      }, {passive:true});
      track.addEventListener("scroll", () => {
        const s = step();
        if (!s) return;
        index = Math.max(0, Math.min(items.length - 1, Math.round(track.scrollLeft / s)));
        if (progress) progress.style.width = `${((index + 1) / Math.max(1, items.length)) * 100}%`;
      }, {passive:true});
      track.addEventListener("mouseenter", () => clearInterval(timer));
      track.addEventListener("mouseleave", restart);
      prev?.addEventListener("mouseenter", () => clearInterval(timer));
      next?.addEventListener("mouseenter", () => clearInterval(timer));
      prev?.addEventListener("mouseleave", restart);
      next?.addEventListener("mouseleave", restart);
      window.addEventListener("resize", () => { index = 0; update("auto"); });
      update("auto");
      restart();
    }

    heroSlider();
    trackSlider("mServiceTrack", "mServicePrev", "mServiceNext", "mServiceProgress", 5200);
    trackSlider("mReviewTrack", "mReviewPrev", "mReviewNext", "mReviewProgress", 5600);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initMobileHomeSliders, {once:true});
  } else {
    initMobileHomeSliders();
  }
})();
