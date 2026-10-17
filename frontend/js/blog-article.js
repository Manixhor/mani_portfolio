const article = document.querySelector("[data-article]");
const postId = window.location.pathname.match(/\/blogs\/(\d+)\/?$/)?.[1];
const nav = document.querySelector(".top-nav");
const navToggle = document.querySelector("[data-nav-toggle]");
const navLinks = document.querySelector("[data-nav-links]");
const audioButton = document.querySelector("[data-article-audio]");
const audioIcon = document.querySelector("[data-article-audio-icon]");
const audioLabel = document.querySelector("[data-article-audio-label]");
let speechUtterance = null;

function articleText(value) {
  return String(value || "").trim();
}

function readingTime(value) {
  const words = articleText(value).split(/\s+/).filter(Boolean).length;
  return `${Math.max(1, Math.ceil(words / 200))} min read`;
}

function updateAudioButton(isPlaying) {
  if (!audioButton || !audioIcon || !audioLabel) return;
  audioButton.setAttribute("aria-pressed", String(isPlaying));
  audioIcon.textContent = isPlaying ? "■" : "▶";
  audioLabel.textContent = isPlaying ? "Stop listening" : "Listen to article";
}

function setupArticleAudio(post, title) {
  if (!audioButton) return;
  if (!("speechSynthesis" in window)) {
    audioButton.disabled = true;
    audioLabel.textContent = "Voice unavailable";
    return;
  }

  audioButton.addEventListener("click", () => {
    if (speechSynthesis.speaking || speechSynthesis.pending) {
      speechSynthesis.cancel();
      updateAudioButton(false);
      return;
    }

    const content = [title, articleText(post.subheader), articleText(post.description)].filter(Boolean).join(". ");
    speechUtterance = new SpeechSynthesisUtterance(content);
    speechUtterance.lang = navigator.language || "en-US";
    speechUtterance.rate = 0.94;
    speechUtterance.onend = () => updateAudioButton(false);
    speechUtterance.onerror = () => updateAudioButton(false);
    speechSynthesis.cancel();
    speechSynthesis.speak(speechUtterance);
    updateAudioButton(true);
  });
}

navToggle?.addEventListener("click", () => {
  const isOpen = nav?.classList.toggle("is-open");
  navToggle.setAttribute("aria-expanded", String(isOpen));
});

navLinks?.addEventListener("click", () => {
  nav?.classList.remove("is-open");
  navToggle?.setAttribute("aria-expanded", "false");
});

async function loadArticle() {
  if (!postId) throw new Error("Article not found.");

  const response = await fetch(`/blog-data/${postId}/`, { cache: "no-store" });
  const post = await response.json();
  if (!response.ok) throw new Error(post.detail || "Article not found.");

  const title = articleText(post.header) || "Untitled";
  document.title = `${title} | Mani`;
  document.querySelector("[data-article-title]").textContent = title;
  document.querySelector("[data-article-subtitle]").textContent = articleText(post.subheader);
  document.querySelector("[data-article-date]").textContent = post.createdAt
    ? new Intl.DateTimeFormat("en", { day: "numeric", month: "long", year: "numeric" }).format(new Date(post.createdAt))
    : "";
  document.querySelector("[data-article-reading-time]").textContent = readingTime(post.description);
  setupArticleAudio(post, title);

  const media = document.querySelector("[data-article-media]");
  if (post.imageUrl) {
    const image = document.createElement("img");
    image.src = post.imageUrl;
    image.alt = title;
    media.appendChild(image);
  }
  if (post.videoUrl) {
    const video = document.createElement("video");
    video.src = post.videoUrl;
    video.controls = true;
    video.preload = "metadata";
    video.playsInline = true;
    media.appendChild(video);
  }
  media.hidden = !media.childElementCount;

  const body = document.querySelector("[data-article-body]");
  const lines = articleText(post.description).split(/\n+/).map((line) => line.trim()).filter(Boolean);
  lines.forEach((line, index) => {
    const nextLine = lines[index + 1] || "";
    const isSectionHeading = line.length < 80 && !/[.:!?]$/.test(line) && nextLine.length > line.length + 25;
    const element = document.createElement(isSectionHeading ? "h2" : "p");
    element.textContent = line;
    body.appendChild(element);
  });
}

loadArticle().catch((error) => {
  article.querySelector("[data-article-title]").textContent = error.message;
});

window.addEventListener("pagehide", () => {
  if (speechUtterance && "speechSynthesis" in window) speechSynthesis.cancel();
});
