const blogGrid = document.querySelector("[data-blog-grid]");
const blogStatus = document.querySelector("[data-blog-status]");
const blogDialog = document.querySelector("[data-blog-dialog]");
const blogForm = document.querySelector("[data-blog-form]");
const nav = document.querySelector(".top-nav");
const navToggle = document.querySelector("[data-nav-toggle]");
const navLinks = document.querySelector("[data-nav-links]");

function setStatus(message, isError = false) {
  if (!blogStatus) return;
  blogStatus.textContent = message;
  blogStatus.classList.toggle("is-error", isError);
}

function renderPosts(items) {
  if (!blogGrid) return;
  blogGrid.innerHTML = "";

  if (!items.length) {
    blogGrid.innerHTML = '<p class="blog-empty">No posts yet.</p>';
    return;
  }

  items.forEach((post) => {
    const article = document.createElement("article");
    article.className = "blog-card";

    if (post.imageUrl) {
      const image = document.createElement("img");
      image.src = post.imageUrl;
      image.alt = post.header || "Blog image";
      image.loading = "lazy";
      image.addEventListener("error", () => image.remove());
      article.appendChild(image);
    }

    const body = document.createElement("div");
    const header = document.createElement("h2");
    const subheader = document.createElement("p");
    const description = document.createElement("p");
    header.textContent = post.header || "Untitled";
    subheader.className = "blog-card__subheader";
    subheader.textContent = post.subheader || "";
    description.className = "blog-card__description";
    description.textContent = post.description || "";
    body.append(header, subheader, description);
    article.appendChild(body);
    blogGrid.appendChild(article);
  });
}

async function loadPosts() {
  setStatus("Loading posts...");
  const response = await fetch(`/blog-data/?_=${Date.now()}`, { cache: "no-store" });
  if (!response.ok) throw new Error("Blogs could not be loaded.");
  const data = await response.json();
  renderPosts(data.items || []);
  setStatus("");
}

function closeDialog() {
  if (blogDialog?.open) blogDialog.close();
}

document.querySelector("[data-open-blog-form]")?.addEventListener("click", () => blogDialog?.showModal());
document.querySelectorAll("[data-close-blog-form]").forEach((button) => button.addEventListener("click", closeDialog));

blogForm?.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(blogForm);
  const publishButton = blogForm.querySelector('button[type="submit"]');
  const formStatus = document.querySelector("[data-blog-form-status]");
  publishButton.disabled = true;
  formStatus.textContent = "Publishing...";

  try {
    const response = await fetch("/blog-data/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Blog-Admin-Password": formData.get("password"),
      },
      body: JSON.stringify({
        imageUrl: formData.get("imageUrl"),
        header: formData.get("header"),
        subheader: formData.get("subheader"),
        description: formData.get("description"),
      }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Blog could not be published.");
    blogForm.reset();
    closeDialog();
    await loadPosts();
  } catch (error) {
    formStatus.textContent = error.message || "Blog could not be published.";
  } finally {
    publishButton.disabled = false;
  }
});

navToggle?.addEventListener("click", () => {
  const isOpen = nav.classList.toggle("is-open");
  navToggle.setAttribute("aria-expanded", String(isOpen));
});
navLinks?.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => {
  nav.classList.remove("is-open");
  navToggle?.setAttribute("aria-expanded", "false");
}));

loadPosts().catch((error) => setStatus(error.message, true));
