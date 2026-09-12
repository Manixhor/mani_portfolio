const login = document.querySelector("[data-admin-login]");
const dashboard = document.querySelector("[data-admin-dashboard]");
const passwordInput = document.querySelector("[data-admin-password]");
const loginStatus = document.querySelector("[data-admin-login-status]");
const status = document.querySelector("[data-admin-status]");
let adminPassword = "";
let portfolioConfig = {};

const fields = {
  experience: [["role", "Role"], ["company", "Company"], ["period", "Period"], ["points", "Highlights", "textarea"], ["order", "Order", "number"], ["is_visible", "Visible", "checkbox"]],
  skills: [["name", "Skill name"], ["icon", "Icon class or text:LABEL"], ["order", "Order", "number"], ["is_visible", "Visible", "checkbox"]],
  projects: [["name", "Project name"], ["description", "Description", "textarea"], ["brief", "Project brief", "textarea"], ["stack", "Tech stack"], ["live_url", "Live link", "url"], ["show_live_url", "Show live link", "checkbox"], ["github_url", "GitHub link", "url"], ["show_github_url", "Show GitHub link", "checkbox"], ["blog_url", "Blog link", "url"], ["image_url", "Image URL", "url"], ["image_alt", "Image alt text"], ["order", "Order", "number"], ["is_visible", "Visible", "checkbox"]],
  certifications: [["title", "Title"], ["issuer", "Issuer"], ["issued_date", "Issued date"], ["credential_url", "Credential link", "url"], ["description", "Description", "textarea"], ["image_url", "Image URL", "url"], ["image_alt", "Image alt text"], ["order", "Order", "number"], ["is_visible", "Visible", "checkbox"]],
};
const blankItems = Object.fromEntries(Object.entries(fields).map(([name, definitions]) => [name, Object.fromEntries(definitions.map(([key, , type]) => [key, type === "checkbox" ? true : type === "number" ? 0 : ""]))]));
const siteFields = [
  ["hero.name", "Name"], ["hero.title", "Hero title"], ["hero.tagline", "Role tagline"], ["hero.year", "Year"], ["hero.resumeUrl", "Resume download link", "url"], ["hero.resumeLabel", "Resume button label"],
  ["about.sectionLabel", "About section label"], ["about.heading", "About heading"], ["about.paragraphs.0", "About text", "textarea"], ["about.imageUrl", "About image URL", "url"], ["about.imageAlt", "About image alt text"],
  ["experience.sectionLabel", "Experience section label"], ["experience.heading", "Experience heading"], ["skills.sectionLabel", "Technical Skills label"], ["skills.heading", "Technical Skills heading"], ["projects.sectionLabel", "Projects section label"], ["projects.heading", "Projects heading"],
  ["contact.sectionLabel", "Contact section label"], ["contact.heading", "Contact heading"], ["contact.subtitle", "Contact text", "textarea"], ["contact.email", "Contact email", "email"], ["contact.phone", "Phone"], ["contact.location", "Location"], ["contact.quote", "Quote", "textarea"], ["contact.imageUrl", "Contact image URL", "url"], ["contact.imageAlt", "Contact image alt text"], ["footer.copyright", "Footer copyright"], ["notificationEmails", "Contact notification emails"],
];

function headers() { return { "Content-Type": "application/json", "X-Portfolio-Admin-Password": adminPassword }; }
function setMessage(element, message, error = false) { element.textContent = message; element.classList.toggle("is-error", error); }
function getPath(object, path) { return path.split(".").reduce((value, key) => value?.[key], object) ?? ""; }
function setPath(object, path, value) { const keys = path.split("."); const last = keys.pop(); const target = keys.reduce((current, key) => current[key] ??= /^\d+$/.test(key) ? [] : {}, object); target[last] = value; }

function renderSite() {
  const container = document.querySelector("[data-admin-site-fields]"); container.innerHTML = "";
  siteFields.forEach(([path, label, type = "text"]) => {
    const field = document.createElement("label"); field.textContent = label;
    const control = type === "textarea" ? document.createElement("textarea") : document.createElement("input");
    if (type !== "textarea") control.type = type; control.dataset.adminSite = path; control.value = getPath({ ...portfolioConfig, notificationEmails: portfolioConfig.notificationEmails }, path); field.appendChild(control); container.appendChild(field);
  });
}

function renderCollection(name, items) {
  const container = document.querySelector(`[data-admin-collection="${name}"]`); container.innerHTML = "";
  items.forEach((item) => {
    const card = document.createElement("article"); card.className = "admin-item"; card.dataset.adminItem = name; card.dataset.id = item.id || "";
    const remove = document.createElement("button"); remove.type = "button"; remove.className = "admin-remove"; remove.textContent = "Remove"; remove.addEventListener("click", () => card.remove()); card.appendChild(remove);
    fields[name].forEach(([key, label, type = "text"]) => {
      const field = document.createElement("label"); field.textContent = label;
      const control = type === "textarea" ? document.createElement("textarea") : document.createElement("input");
      control.dataset.field = key; if (type === "checkbox") { control.type = "checkbox"; control.checked = item[key] === true || item[key] === "t"; } else { control.type = type; control.value = item[key] ?? ""; } field.appendChild(control); card.appendChild(field);
    });
    container.appendChild(card);
  });
}

function collectionValues(name) {
  return [...document.querySelectorAll(`[data-admin-item="${name}"]`)].map((card) => {
    const item = {}; if (card.dataset.id) item.id = Number(card.dataset.id);
    fields[name].forEach(([key, , type = "text"]) => { const control = card.querySelector(`[data-field="${key}"]`); item[key] = type === "checkbox" ? control.checked : type === "number" ? Number(control.value || 0) : control.value.trim(); }); return item;
  });
}

async function loadAdmin() {
  const response = await fetch("/admin-data/", { headers: headers(), cache: "no-store" }); const data = await response.json(); if (!response.ok) throw new Error(data.detail || "Admin data could not be loaded.");
  portfolioConfig = { ...data.config, notificationEmails: data.notificationEmails || "" }; renderSite(); Object.entries(data.collections).forEach(([name, items]) => renderCollection(name, items));
}

document.querySelector("[data-admin-login-form]").addEventListener("submit", async (event) => { event.preventDefault(); adminPassword = passwordInput.value; try { await loadAdmin(); login.hidden = true; dashboard.hidden = false; } catch (error) { adminPassword = ""; setMessage(loginStatus, error.message, true); } });
document.querySelectorAll("[data-admin-add]").forEach((button) => button.addEventListener("click", () => { const name = button.dataset.adminAdd; renderCollection(name, [...collectionValues(name), { ...blankItems[name], order: collectionValues(name).length + 1 }]); }));
document.querySelector("[data-admin-save]").addEventListener("click", async () => {
  try { const draft = structuredClone(portfolioConfig); document.querySelectorAll("[data-admin-site]").forEach((control) => setPath(draft, control.dataset.adminSite, control.value.trim())); const notificationEmails = draft.notificationEmails; delete draft.notificationEmails; setMessage(status, "Saving..."); const response = await fetch("/admin-data/", { method: "POST", headers: headers(), body: JSON.stringify({ config: draft, collections: Object.fromEntries(Object.keys(fields).map((name) => [name, collectionValues(name)])), notificationEmails }) }); const data = await response.json(); if (!response.ok) throw new Error(data.detail || "Changes could not be saved."); setMessage(status, "Saved. The portfolio is updated."); await loadAdmin(); } catch (error) { setMessage(status, error.message || "Changes could not be saved.", true); }
});
