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
const mediaHelp = document.querySelector("[data-blog-media-help]");
const formKicker = document.querySelector("[data-blog-form-kicker]");
const formTitle = document.querySelector("[data-blog-form-title]");
const blogSubmit = document.querySelector("[data-blog-submit]");
let editingPost = null;
const maxImageBytes = 10 * 1024 * 1024;
const maxVideoBytes = 50 * 1024 * 1024;

function setStatus(message, isError = false) {
  if (!blogStatus) return;
  blogStatus.textContent = message;
  blogStatus.classList.toggle("is-error", isError);
}

function formatDate(value) {
  if (!value) return "Article";
  return new Intl.DateTimeFormat("en", { day: "numeric", month: "short", year: "numeric" }).format(new Date(value));
}

function excerpt(value) {
  const text = String(value || "").replace(/\s+/g, " ").trim();
  return text.length > 220 ? `${text.slice(0, 217).trimEnd()}...` : text;
}

function readingTime(value) {
  const words = String(value || "").trim().split(/\s+/).filter(Boolean).length;
  return `${Math.max(1, Math.ceil(words / 200))} min read`;
}

function appendMedia(container, post) {
  if (post.imageUrl) {
    const image = document.createElement("img");
    image.src = post.imageUrl;
    image.alt = post.header || "Blog image";
    image.loading = "lazy";
    image.addEventListener("error", () => container.classList.add("blog-card__media--empty"));
    container.appendChild(image);
  } else if (post.videoUrl) {
    const video = document.createElement("video");
    video.src = post.videoUrl;
    video.muted = true;
    video.preload = "metadata";
    video.playsInline = true;
    container.appendChild(video);
  } else {
    container.classList.add("blog-card__media--empty");
  }
}

function createPostCard(post, featured = false) {
  const article = document.createElement("article");
  article.className = `blog-card${featured ? " blog-card--featured" : ""}`;
  const link = document.createElement("a");
  link.className = "blog-card__surface";
  link.href = `/blogs/${post.id}/`;

  const body = document.createElement("div");
  body.className = "blog-card__body";
  const meta = document.createElement("p");
  meta.className = "blog-card__meta";
  meta.textContent = `Mani Gururam  ·  ${formatDate(post.createdAt)}  ·  ${readingTime(post.description)}`;
  const header = document.createElement("h2");
  header.textContent = post.header || "Untitled";
  const subheader = document.createElement("p");
  subheader.className = "blog-card__subheader";
  subheader.textContent = post.subheader || "";
  const description = document.createElement("p");
  description.className = "blog-card__description";
  description.textContent = excerpt(post.description);
  const readingCue = document.createElement("span");
  readingCue.className = "blog-card__link";
  readingCue.textContent = "Read story";
  body.append(meta, header, subheader, description, readingCue);

  const media = document.createElement("div");
  media.className = "blog-card__media";
  appendMedia(media, post);
  if (featured) {
    link.append(body, media);
  } else {
    link.append(body, media);
  }
  article.appendChild(link);
  if (adminMode) {
    const editButton = document.createElement("button");
    editButton.type = "button";
    editButton.className = "blog-card__edit";
    editButton.textContent = "Edit";
    editButton.addEventListener("click", () => openBlogForm(post));
    article.appendChild(editButton);
  }
  return article;
}

function renderPosts(items) {
  if (!blogGrid) return;
  blogGrid.innerHTML = "";

  const count = document.querySelector("[data-blog-count]");
  if (count) count.textContent = items.length ? `${items.length} ${items.length === 1 ? "story" : "stories"}` : "";

  if (!items.length) {
    blogGrid.innerHTML = '<p class="blog-empty">No posts yet.</p>';
    return;
  }

  blogGrid.appendChild(createPostCard(items[0], true));
  const stream = document.createElement("div");
  stream.className = "blog-stream";
  items.slice(1).forEach((post) => stream.appendChild(createPostCard(post)));
  if (stream.childElementCount) blogGrid.appendChild(stream);
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

function openBlogForm(post = null) {
  if (!blogForm || !blogDialog) return;
  editingPost = post;
  blogForm.reset();
  mediaInput.required = !post;
  if (post) {
    blogForm.elements.header.value = post.header || "";
    blogForm.elements.subheader.value = post.subheader || "";
    blogForm.elements.description.value = post.description || "";
    mediaTypeInput.value = post.videoUrl ? "video" : "image";
  }
  formKicker.textContent = post ? "Update post" : "New post";
  formTitle.textContent = post ? "Edit blog" : "Add blog";
  blogSubmit.textContent = post ? "Save changes" : "Publish";
  mediaHelp.textContent = post ? "Optional. Leave empty to keep the current media." : "Required for a new post.";
  updateMediaInput(false);
  blogDialog.showModal();
}

const addBlogButton = document.querySelector("[data-open-blog-form]");
if (adminMode && addBlogButton) addBlogButton.hidden = false;
addBlogButton?.addEventListener("click", () => openBlogForm());
document.querySelectorAll("[data-close-blog-form]").forEach((button) => button.addEventListener("click", closeDialog));

function updateMediaInput(clear = true) {
  if (!mediaInput || !mediaTypeInput) return;
  const isVideo = mediaTypeInput.value === "video";
  mediaInput.accept = isVideo ? "video/mp4,video/webm,video/quicktime" : "image/jpeg,image/png,image/webp,image/avif";
  if (clear) mediaInput.value = "";
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
    const hasNewMedia = media instanceof File && media.size;
    if (!hasNewMedia && !editingPost) throw new Error("Choose an image or video for the post.");
    let imageUrl = editingPost?.imageUrl || "";
    let videoUrl = editingPost?.videoUrl || "";

    if (hasNewMedia) {
      const maxFileBytes = mediaType === "video" ? maxVideoBytes : maxImageBytes;
      if (media.size > maxFileBytes) throw new Error(`${mediaType === "video" ? "Video" : "Image"} must be ${maxFileBytes / 1024 / 1024} MB or smaller.`);
      formStatus.textContent = "Preparing upload...";
      const signatureResponse = await fetch("/blog-upload/", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-Blog-Admin-Password": password },
        body: JSON.stringify({ contentType: media.type }),
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
      imageUrl = signatureData.resourceType === "image" ? uploadData.secure_url : "";
      videoUrl = signatureData.resourceType === "video" ? uploadData.secure_url : "";
    }

    formStatus.textContent = editingPost ? "Saving changes..." : "Publishing post...";
    const response = await fetch(editingPost ? `/blog-data/${editingPost.id}/` : "/blog-data/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Blog-Admin-Password": password,
      },
      body: JSON.stringify({
        imageUrl,
        videoUrl,
        header: formData.get("header"),
        subheader: formData.get("subheader"),
        description: formData.get("description"),
      }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Blog could not be saved.");
    blogForm.reset();
    editingPost = null;
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
