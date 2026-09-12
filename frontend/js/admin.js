const login = document.querySelector("[data-admin-login]");
const dashboard = document.querySelector("[data-admin-dashboard]");
const passwordInput = document.querySelector("[data-admin-password]");
const loginStatus = document.querySelector("[data-admin-login-status]");
const status = document.querySelector("[data-admin-status]");
let adminPassword = "";

const blankItems = {
  experience: { role: "", company: "", period: "", points: "", order: 0, is_visible: true },
  skills: { name: "", icon: "", order: 0, is_visible: true },
  projects: { name: "", description: "", brief: "", stack: "", live_url: "", show_live_url: true, github_url: "", show_github_url: true, image_url: "", image_alt: "", order: 0, is_visible: true },
  certifications: { title: "", issuer: "", issued_date: "", credential_url: "", description: "", image_url: "", image_alt: "", order: 0, is_visible: true },
};

function headers() { return { "Content-Type": "application/json", "X-Portfolio-Admin-Password": adminPassword }; }
function setMessage(element, message, error = false) { element.textContent = message; element.classList.toggle("is-error", error); }
function parseEditor(selector) { return JSON.parse(document.querySelector(selector).value); }
function editor(selector, value) { document.querySelector(selector).value = JSON.stringify(value, null, 2); }

async function loadAdmin() {
  const response = await fetch("/admin-data/", { headers: headers(), cache: "no-store" });
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || "Admin data could not be loaded.");
  editor("[data-admin-config]", data.config);
  Object.entries(data.collections).forEach(([name, items]) => editor(`[data-admin-collection="${name}"]`, items));
  document.querySelector("[data-admin-notification-emails]").value = data.notificationEmails || "";
}

document.querySelector("[data-admin-login-form]").addEventListener("submit", async (event) => {
  event.preventDefault(); adminPassword = passwordInput.value;
  try { await loadAdmin(); login.hidden = true; dashboard.hidden = false; setMessage(status, ""); }
  catch (error) { adminPassword = ""; setMessage(loginStatus, error.message, true); }
});

document.querySelectorAll("[data-admin-add]").forEach((button) => button.addEventListener("click", () => {
  const name = button.dataset.adminAdd;
  try { const items = parseEditor(`[data-admin-collection="${name}"]`); items.push({ ...blankItems[name], order: items.length + 1 }); editor(`[data-admin-collection="${name}"]`, items); }
  catch { setMessage(status, `Fix the ${name} JSON before adding another item.`, true); }
}));

document.querySelector("[data-admin-save]").addEventListener("click", async () => {
  try {
    const collections = Object.fromEntries(Object.keys(blankItems).map((name) => [name, parseEditor(`[data-admin-collection="${name}"]`)]));
    setMessage(status, "Saving...");
    const response = await fetch("/admin-data/", { method: "POST", headers: headers(), body: JSON.stringify({ config: parseEditor("[data-admin-config]"), collections, notificationEmails: document.querySelector("[data-admin-notification-emails]").value }) });
    const data = await response.json(); if (!response.ok) throw new Error(data.detail || "Changes could not be saved.");
    setMessage(status, "Saved. The portfolio is updated.");
    await loadAdmin();
  } catch (error) { setMessage(status, error.message || "Use valid JSON in every editor before saving.", true); }
});
