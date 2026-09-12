const blogGrid = document.querySelector("[data-blog-grid]");
const blogStatus = document.querySelector("[data-blog-status]");
const blogDialog = document.querySelector("[data-blog-dialog]");
const blogForm = document.querySelector("[data-blog-form]");
const nav = document.querySelector(".top-nav");
const navToggle = document.querySelector("[data-nav-toggle]");
const navLinks = document.querySelector("[data-nav-links]");
const adminMode = window.location.pathname.replace(/\/$/, "") === "/blogs/admin";
const mediaTypeInput = document.querySelector("[data-blog-media-type]");
const mediaInput = document.querySelector("[data-blog-media-input]");
const maxImageBytes = 10 * 1024 * 1024;
const maxVideoBytes = 50 * 1024 * 1024;

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
    } else if (post.videoUrl) {
      const video = document.createElement("video");
      video.src = post.videoUrl;
      video.controls = true;
      video.preload = "metadata";
      video.playsInline = true;
      article.appendChild(video);
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

const addBlogButton = document.querySelector("[data-open-blog-form]");
if (adminMode && addBlogButton) addBlogButton.hidden = false;
addBlogButton?.addEventListener("click", () => blogDialog?.showModal());
document.querySelectorAll("[data-close-blog-form]").forEach((button) => button.addEventListener("click", closeDialog));

function updateMediaInput() {
  if (!mediaInput || !mediaTypeInput) return;
  const isVideo = mediaTypeInput.value === "video";
  mediaInput.accept = isVideo ? "video/mp4,video/webm,video/quicktime" : "image/jpeg,image/png,image/webp,image/avif";
  mediaInput.value = "";
}

mediaTypeInput?.addEventListener("change", updateMediaInput);

blogForm?.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(blogForm);
  const publishButton = blogForm.querySelector('button[type="submit"]');
  const formStatus = document.querySelector("[data-blog-form-status]");
  const media = formData.get("media");
  const mediaType = formData.get("mediaType");
  const password = formData.get("password");
  publishButton.disabled = true;
  formStatus.textContent = "";

  try {
    if (!(media instanceof File) || !media.size) throw new Error("Choose an image or video for the post.");
    const maxFileBytes = mediaType === "video" ? maxVideoBytes : maxImageBytes;
    if (media.size > maxFileBytes) throw new Error(`${mediaType === "video" ? "Video" : "Image"} must be ${maxFileBytes / 1024 / 1024} MB or smaller.`);

    formStatus.textContent = "Preparing upload...";
    const signatureResponse = await fetch("/blog-upload/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Blog-Admin-Password": password,
      },
      body: JSON.stringify({
        contentType: media.type,
      }),
    });
    const signatureData = await signatureResponse.json();
    if (!signatureResponse.ok) throw new Error(signatureData.detail || "Upload could not be prepared.");

    formStatus.textContent = "Uploading media...";
    const uploadForm = new FormData();
    uploadForm.append("file", media);
    uploadForm.append("public_id", signatureData.publicId);
    uploadForm.append("timestamp", signatureData.timestamp);
    uploadForm.append("api_key", signatureData.apiKey);
    uploadForm.append("signature", signatureData.signature);
    uploadForm.append("allowed_formats", signatureData.allowedFormats);
    const uploadResponse = await fetch(signatureData.uploadUrl, { method: "POST", body: uploadForm });
    const uploadData = await uploadResponse.json();
    if (!uploadResponse.ok) throw new Error(uploadData.error?.message || "Media could not be uploaded.");

    formStatus.textContent = "Publishing post...";
    const response = await fetch("/blog-data/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Blog-Admin-Password": password,
      },
      body: JSON.stringify({
        imageUrl: signatureData.resourceType === "image" ? uploadData.secure_url : "",
        videoUrl: signatureData.resourceType === "video" ? uploadData.secure_url : "",
        header: formData.get("header"),
        subheader: formData.get("subheader"),
        description: formData.get("description"),
      }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Blog could not be published.");
    blogForm.reset();
    updateMediaInput();
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
