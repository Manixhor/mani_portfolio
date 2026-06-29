const LOCAL_API_BASE = "http://127.0.0.1:8000/api";
const API_BASE = window.PORTFOLIO_API_BASE || (
  ["localhost", "127.0.0.1", ""].includes(window.location.hostname)
    ? LOCAL_API_BASE
    : `${window.location.origin}/api`
);
const progressBar = document.getElementById("progress-bar");
const motionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");

function setText(selector, value) {
  const element = document.querySelector(selector);
  if (element) element.textContent = value || "";
}

function plainText(value) {
  const template = document.createElement("template");
  template.innerHTML = String(value || "");
  return (template.content.textContent || "").trim();
}

function cleanProjectUrl(value) {
  const url = plainText(value);
  if (!url || url === "#" || url.toLowerCase() === "null" || url.toLowerCase() === "none") {
    return "";
  }

  if (url.startsWith("/") || url.startsWith("http://") || url.startsWith("https://")) {
    return url;
  }

  return "";
}

function setHtml(selector, value) {
  const element = document.querySelector(selector);
  if (element) element.innerHTML = value || "";
}

function setMeta(selector, value) {
  const element = document.querySelector(selector);
  if (element && value) element.setAttribute("content", value);
}

function hasHtml(value) {
  return /<\/?[a-z][\s\S]*>/i.test(value || "");
}

function richTextHtml(value) {
  if (!value) return "";
  return hasHtml(value) ? value : `<p>${value}</p>`;
}

function renderRichText(container, items = []) {
  container.innerHTML = "";
  items.forEach((item) => {
    if (!item) return;
    container.insertAdjacentHTML("beforeend", richTextHtml(item));
  });
}

function updateProgress() {
  if (!progressBar) return;

  const scrollTop = window.scrollY;
  const docHeight = document.documentElement.scrollHeight - window.innerHeight;
  const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
  progressBar.style.width = `${progress}%`;
}

function normalizeStack(project) {
  if (Array.isArray(project.tags)) return project.tags.join(" | ");
  return project.stack || "";
}

function skillLogo(skillName, icon) {
  if (icon) return icon;

  const normalized = (skillName || "").toLowerCase().replace(/\s+/g, "");
  const logos = {
    python: "devicon-python-plain",
    django: "devicon-django-plain",
    drf: "text:DRF",
    djangorestframework: "text:DRF",
    mysql: "devicon-mysql-plain",
    postgresql: "devicon-postgresql-plain",
    postgres: "devicon-postgresql-plain",
    sql: "devicon-mysql-plain",
    git: "devicon-git-plain",
    html: "devicon-html5-plain",
    html5: "devicon-html5-plain",
    css: "devicon-css3-plain",
    css3: "devicon-css3-plain",
    javascript: "devicon-javascript-plain",
    js: "devicon-javascript-plain",
    react: "devicon-react-original",
    fastapi: "devicon-fastapi-plain",
  };

  return logos[normalized] || "devicon-code-plain";
}

async function loadPortfolioConfig() {
  const response = await fetch(`${API_BASE}/portfolio/config/`, {
    headers: { Accept: "application/json" },
  });

  if (!response.ok) {
    throw new Error("Portfolio config could not be loaded.");
  }

  return response.json();
}

function renderHero(hero = {}) {
  setText('[data-content="hero-title"]', hero.title);
  setText('[data-content="hero-name"]', hero.name);
  setText('[data-content="hero-tagline"]', hero.tagline);
  setText('[data-content="hero-year"]', hero.year);

  if (hero.name) {
    document.title = `${hero.name} | Portfolio`;
    setMeta('meta[property="og:title"]', `${hero.name} | Portfolio`);
  }

  if (hero.tagline) {
    setMeta('meta[name="description"]', hero.tagline);
    setMeta('meta[property="og:description"]', hero.tagline);
  }

  const resumeLink = document.querySelector('[data-content="resume-link"]');
  if (resumeLink) {
    resumeLink.textContent = hero.resumeLabel;
    resumeLink.href = hero.resumeUrl || "#";
  }
}

function renderAbout(about = {}) {
  setText('[data-content="about-label"]', about.sectionLabel);
  setText('[data-content="about-heading"]', about.heading);

  const paragraphs = document.querySelector('[data-render="about-paragraphs"]');
  if (paragraphs) {
    renderRichText(paragraphs, about.paragraphs || []);
  }

  const image = document.querySelector('[data-content="about-image"]');
  if (image) {
    image.src = about.imageUrl || "";
    image.alt = about.imageAlt || "Developer workspace";
  }
}

function renderExperience(experience = {}) {
  setText('[data-content="experience-label"]', experience.sectionLabel);
  setText('[data-content="experience-heading"]', experience.heading);

  const container = document.querySelector('[data-render="experience"]');
  if (!container) return;

  container.innerHTML = "";
  (experience.items || []).forEach((item) => {
    const article = document.createElement("article");
    article.className = "experience-card";
    article.innerHTML = `
      <div>
        <p class="experience-period"></p>
        <h3></h3>
        <span></span>
      </div>
      <ul></ul>
    `;

    article.querySelector(".experience-period").textContent = item.period || "";
    article.querySelector("h3").textContent = item.role || "";
    article.querySelector("span").textContent = item.company || "";

    const list = article.querySelector("ul");
    (item.points || []).forEach((point) => {
      const li = document.createElement("li");
      li.textContent = point;
      list.appendChild(li);
    });

    container.appendChild(article);
  });
}

function renderSkills(skills = {}) {
  setText('[data-content="skills-label"]', skills.sectionLabel);
  setText('[data-content="skills-heading"]', skills.heading);

  const grid = document.querySelector('[data-render="skills"]');
  if (!grid) return;

  grid.innerHTML = "";
  (skills.items || []).forEach((skill) => {
    const logo = skillLogo(skill.name, skill.icon);
    const item = document.createElement("div");
    item.className = "skill-item";

    if (logo.startsWith("text:")) {
      item.innerHTML = `<strong class="skill-logo-text"></strong><span></span>`;
      item.querySelector("strong").textContent = logo.replace("text:", "");
    } else {
      item.innerHTML = `<i></i><span></span>`;
      item.querySelector("i").className = logo;
    }

    item.querySelector("span").textContent = skill.name || "";
    grid.appendChild(item);
  });
}

function renderCertifications(certifications = {}) {
  setText('[data-content="certifications-label"]', certifications.sectionLabel || "Certifications");
  setText('[data-content="certifications-heading"]', certifications.heading || "Certifications");

  const grid = document.querySelector('[data-render="certifications"]');
  if (!grid) return;

  const items = certifications.items || [];
  grid.innerHTML = "";

  if (!items.length) {
    const empty = document.createElement("article");
    empty.className = "certification-card certification-card--empty";
    empty.innerHTML = `
      <img loading="lazy" referrerpolicy="no-referrer" />
      <h3></h3>
      <p></p>
    `;
    empty.querySelector("img").src = "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?auto=format&fit=crop&w=900&q=80";
    empty.querySelector("img").alt = "Certification preview";
    empty.querySelector("h3").textContent = "Certifications coming soon";
    empty.querySelector("p").textContent = "New credentials will appear here as they are added.";
    grid.appendChild(empty);
    return;
  }

  items.forEach((item) => {
    const article = document.createElement("article");
    article.className = "certification-card";
    article.innerHTML = `
      <img loading="lazy" referrerpolicy="no-referrer" />
      <div>
        <p class="certification-date"></p>
        <h3></h3>
        <span></span>
        <p class="certification-description"></p>
        <a class="certification-link" target="_blank" rel="noopener noreferrer">View Credential</a>
      </div>
    `;

    const image = article.querySelector("img");
    image.src = item.imageUrl || "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?auto=format&fit=crop&w=900&q=80";
    image.alt = plainText(item.imageAlt) || `${plainText(item.title) || "Certification"} preview`;
    article.querySelector(".certification-date").textContent = plainText(item.issuedDate);
    article.querySelector("h3").textContent = plainText(item.title);
    article.querySelector("span").textContent = plainText(item.issuer);
    article.querySelector(".certification-description").textContent = plainText(item.description);

    const link = article.querySelector(".certification-link");
    const credentialUrl = cleanProjectUrl(item.credentialUrl);
    if (credentialUrl) {
      link.href = credentialUrl;
    } else {
      link.hidden = true;
    }

    grid.appendChild(article);
  });
}

function renderProjects(projects = {}) {
  setText('[data-content="projects-label"]', projects.sectionLabel);
  setText('[data-content="projects-heading"]', projects.heading);

  const grid = document.querySelector('[data-render="projects"]');
  if (!grid) return;

  grid.innerHTML = "";
  (projects.items || []).forEach((project) => {
    const stack = normalizeStack(project);
    const article = document.createElement("article");
    article.className = "project-card";
    article.innerHTML = `
      <img loading="lazy" referrerpolicy="no-referrer" />
      <div>
        <h3></h3>
        <p></p>
        <span></span>
        <button class="project-trigger" type="button">View Project <b aria-hidden="true">-&gt;</b></button>
      </div>
    `;

    const image = article.querySelector("img");
    image.src = project.imageUrl || "";
    image.alt = project.imageAlt || `${project.name || "Project"} preview`;
    article.querySelector("h3").textContent = project.name || "";
    article.querySelector("p").textContent = project.description || "";
    article.querySelector("span").textContent = stack;

    const trigger = article.querySelector(".project-trigger");
    trigger.dataset.title = project.name || "";
    trigger.dataset.stack = stack;
    trigger.dataset.brief = project.brief || project.description || "";
    trigger.dataset.live = cleanProjectUrl(project.liveUrl);
    trigger.dataset.github = cleanProjectUrl(project.githubUrl);
    trigger.addEventListener("click", () => openProjectModal(trigger));

    grid.appendChild(article);
  });
}

function renderContact(contact = {}, hero = {}) {
  setText('[data-content="contact-label"]', contact.sectionLabel);
  setText('[data-content="contact-heading"]', contact.heading);
  setHtml('[data-render="contact-copy"]', richTextHtml(contact.subtitle));

  const list = document.querySelector('[data-render="contact-list"]');
  if (list) {
    list.innerHTML = "";
    [
      ["&#9993;", contact.email],
      ["&#9742;", contact.phone],
      ["&#8982;", contact.location],
    ].forEach(([icon, value]) => {
      if (!value) return;
      const li = document.createElement("li");
      li.innerHTML = `<span aria-hidden="true">${icon}</span> `;
      li.append(document.createTextNode(value));
      list.appendChild(li);
    });
  }

  const social = hero.social || {};
  const socialLinks = document.querySelector('[data-render="social-links"]');
  if (socialLinks) {
    socialLinks.innerHTML = "";
    [
      ["github", '<i class="devicon-github-original"></i>'],
      ["linkedin", "in"],
      ["email", "&#9993;"],
    ].forEach(([key, label]) => {
      const item = social[key];
      if (!item?.url || item.url === "#") return;
      const link = document.createElement("a");
      link.href = item.url;
      link.setAttribute("aria-label", item.label || key);
      link.rel = "noopener noreferrer";
      link.innerHTML = label;
      socialLinks.appendChild(link);
    });
  }

  const image = document.querySelector('[data-content="contact-image"]');
  if (image) {
    image.src = contact.imageUrl || "";
    image.alt = contact.imageAlt || "Developer workspace";
  }

  setText('[data-content="contact-quote"]', contact.quote || "");
}

function renderPortfolio(config) {
  renderHero(config.hero || {});
  renderAbout(config.about || {});
  renderExperience(config.experience || {});
  renderSkills(config.skills || {});
  renderCertifications(config.certifications || {});
  renderProjects(config.projects || {});
  renderContact(config.contact || {}, config.hero || {});
}

function setupRevealAnimations() {
  if (motionQuery.matches) return;

  const revealItems = document.querySelectorAll(
    ".split-panel, .experience-card, .skills-grid, .certification-card, .project-card, .contact-panel"
  );

  revealItems.forEach((item) => item.classList.add("reveal-on-scroll"));

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    },
    { threshold: 0.15 }
  );

  revealItems.forEach((item) => observer.observe(item));
}

const projectModal = document.getElementById("project-modal");
const modalDialog = projectModal?.querySelector(".project-modal__dialog");
const modalTitle = document.getElementById("modal-title");
const modalBrief = document.getElementById("modal-brief");
const modalStack = document.getElementById("modal-stack");
const modalLive = document.getElementById("modal-live");
const modalGithub = document.getElementById("modal-github");
const modalLinks = projectModal?.querySelector(".project-modal__links");

function setProjectLink(link, url) {
  if (!link) return false;

  const cleanUrl = cleanProjectUrl(url);
  const isPlaceholder = !cleanUrl;
  link.hidden = isPlaceholder;
  link.classList.toggle("is-placeholder", isPlaceholder);

  if (isPlaceholder) {
    link.href = "#";
    link.removeAttribute("target");
    link.setAttribute("aria-disabled", "true");
    return false;
  }

  link.href = cleanUrl;
  link.target = "_blank";
  link.rel = "noopener noreferrer";
  link.removeAttribute("aria-disabled");
  return true;
}

function openProjectModal(trigger) {
  if (!projectModal || !modalDialog) return;

  modalTitle.textContent = trigger.dataset.title || "Project";
  modalBrief.textContent = trigger.dataset.brief || "";
  modalStack.textContent = trigger.dataset.stack || "";
  const hasLiveLink = setProjectLink(modalLive, trigger.dataset.live);
  const hasGithubLink = setProjectLink(modalGithub, trigger.dataset.github);
  if (modalLinks) {
    modalLinks.hidden = !hasLiveLink && !hasGithubLink;
  }

  projectModal.classList.add("is-open");
  projectModal.setAttribute("aria-hidden", "false");
  modalDialog.focus();
}

function closeProjectModal() {
  if (!projectModal) return;

  projectModal.classList.remove("is-open");
  projectModal.setAttribute("aria-hidden", "true");
}

function setContactStatus(message, type = "") {
  const status = document.querySelector("[data-contact-status]");
  if (!status) return;

  status.textContent = message;
  status.classList.toggle("is-success", type === "success");
  status.classList.toggle("is-error", type === "error");
}

function setupContactForm() {
  const form = document.querySelector("[data-contact-form]");
  if (!form) return;

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const submitButton = form.querySelector('button[type="submit"]');
    const formData = new FormData(form);
    const payload = Object.fromEntries(formData.entries());

    submitButton.disabled = true;
    setContactStatus("Sending...");

    try {
      const response = await fetch(`${API_BASE}/contact/submit/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error("Message could not be sent.");
      }

      form.reset();
      setContactStatus("Message sent. I will get back to you soon.", "success");
    } catch (error) {
      console.error(error);
      setContactStatus("Message failed. Please email me directly.", "error");
    } finally {
      submitButton.disabled = false;
    }
  });
}

document.querySelectorAll("[data-close-modal]").forEach((control) => {
  control.addEventListener("click", closeProjectModal);
});

document.querySelectorAll(".project-modal__links a").forEach((link) => {
  link.addEventListener("click", (event) => {
    if (link.classList.contains("is-placeholder")) {
      event.preventDefault();
    }
  });
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") closeProjectModal();
});

document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", (event) => {
    const targetId = anchor.getAttribute("href");
    if (!targetId || targetId === "#") return;

    const target = document.querySelector(targetId);
    if (!target) return;

    event.preventDefault();
    target.scrollIntoView({ behavior: "smooth", block: "start" });
  });
});

window.addEventListener("scroll", updateProgress, { passive: true });
window.addEventListener("load", updateProgress);

window.addEventListener("DOMContentLoaded", async () => {
  setupContactForm();

  try {
    const config = await loadPortfolioConfig();
    renderPortfolio(config);
    setupRevealAnimations();
  } catch (error) {
    document.body.classList.add("config-error");
    console.error(error);
  }
});
