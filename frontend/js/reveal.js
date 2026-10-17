(() => {
  const seen = new WeakSet();
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const selector = ".about-panel .section-copy, .about-image, .experience-card, .skill-item, .project-card, .certification-card, .contact-panel .section-copy, .contact-star-portrait, .blog-page .blog-card";

  function reveal(element) {
    element.classList.add("is-visible");
  }

  const observer = "IntersectionObserver" in window ? new IntersectionObserver((entries) => {
    entries.forEach(({ target, isIntersecting }) => {
      if (!isIntersecting) return;
      reveal(target);
      observer.unobserve(target);
    });
  }, { threshold: 0.08, rootMargin: "0px 0px -24px 0px" }) : null;

  window.revealContent = (root = document) => {
    root.querySelectorAll(selector).forEach((element) => {
      if (seen.has(element)) return;
      seen.add(element);
      if (reducedMotion.matches || !observer) {
        reveal(element);
        return;
      }
      const siblings = [...element.parentElement.children].filter((item) => item.matches(selector));
      const index = siblings.indexOf(element);
      const delay = element.classList.contains("skill-item") ? (index % 6) * 40 : (index % 3) * 80;
      element.style.setProperty("--reveal-delay", `${delay}ms`);
      element.classList.add("reveal-on-scroll");
      element.addEventListener("transitionend", (event) => {
        if (event.target === element && event.propertyName === "opacity") {
          element.style.setProperty("--reveal-delay", "0ms");
        }
      });
      observer.observe(element);
    });
  };

  reducedMotion.addEventListener("change", ({ matches }) => {
    if (!matches) return;
    document.querySelectorAll(".reveal-on-scroll").forEach((element) => {
      reveal(element);
      observer?.unobserve(element);
    });
  });

  document.querySelectorAll("[data-portrait-animation]").forEach((portrait) => {
    let svg;
    let started = false;
    let completed = false;
    let ratio = 0;
    const duration = 7;

    function updatePlayback() {
      if (!svg) return;
      if (reducedMotion.matches || completed || svg.getCurrentTime() >= duration) {
        completed = true;
        svg.setCurrentTime(duration);
        svg.pauseAnimations();
        portrait.dataset.playback = "complete";
        return;
      }
      if (!started && ratio >= 0.4) {
        started = true;
        svg.setCurrentTime(0);
      }
      if (started && ratio > 0 && !document.hidden) {
        svg.unpauseAnimations();
        portrait.dataset.playback = "playing";
      } else {
        svg.pauseAnimations();
        portrait.dataset.playback = started ? "paused" : "waiting";
      }
    }

    const portraitObserver = "IntersectionObserver" in window ? new IntersectionObserver((entries) => {
      ratio = entries[0].intersectionRatio;
      updatePlayback();
    }, { threshold: [0, 0.4] }) : null;

    function preparePortrait() {
      const root = portrait.contentDocument?.documentElement;
      if (!root || root.localName !== "svg") return;
      svg = root;
      svg.pauseAnimations();
      svg.setCurrentTime(0);
      started = false;
      completed = !portraitObserver;
      updatePlayback();
      portrait.dataset.ready = "true";
    }

    portrait.addEventListener("load", preparePortrait);
    preparePortrait();
    portraitObserver?.observe(portrait);
    reducedMotion.addEventListener("change", updatePlayback);
    document.addEventListener("visibilitychange", updatePlayback);
  });
})();
