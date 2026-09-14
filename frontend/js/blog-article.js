const article = document.querySelector("[data-article]");
const postId = window.location.pathname.match(/\/blogs\/(\d+)\/?$/)?.[1];
const nav = document.querySelector(".top-nav");
const navToggle = document.querySelector("[data-nav-toggle]");
const navLinks = document.querySelector("[data-nav-links]");

function articleText(value) {
  return String(value || "").trim();
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
