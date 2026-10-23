const $ = (id) => document.getElementById(id);
const status = $("status");
const canvas = $("pdf");
let pdf, pdfBytes, resumeUrl, page = 1, zoom = 1, fitScale = 1;
let rendering = false, pending = false;

async function render() {
  if (rendering) { pending = true; return; }
  rendering = true;
  $("pdf-links").replaceChildren();
  try {
    const current = await pdf.getPage(page);
    const base = current.getViewport({ scale: 1 });
    const viewportElement = $("viewport");
    const styles = getComputedStyle(viewportElement);
    const width = viewportElement.clientWidth - parseFloat(styles.paddingLeft) - parseFloat(styles.paddingRight);
    fitScale = Math.min(width / base.width, 1.6);
    const scale = fitScale * zoom;
    const ratio = Math.min(window.devicePixelRatio || 1, 2);
    const viewport = current.getViewport({ scale: scale * ratio });
    canvas.width = Math.ceil(viewport.width);
    canvas.height = Math.ceil(viewport.height);
    canvas.style.width = `${viewport.width / ratio}px`;
    canvas.style.height = `${viewport.height / ratio}px`;
    await current.render({ canvasContext: canvas.getContext("2d"), viewport }).promise;
    const linkViewport = current.getViewport({ scale });
    const annotations = await current.getAnnotations({ intent: "display" });
    for (const annotation of annotations) {
      if (annotation.subtype !== "Link" || !annotation.url || !annotation.rect) continue;
      let url;
      try { url = new URL(annotation.url); } catch { continue; }
      if (!["https:", "http:", "mailto:", "tel:"].includes(url.protocol)) continue;
      const rect = linkViewport.convertToViewportRectangle(annotation.rect);
      const link = document.createElement("a");
      link.href = url.href;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.title = url.href;
      link.setAttribute("aria-label", annotation.titleObj?.str || url.href);
      link.style.left = `${Math.min(rect[0], rect[2])}px`;
      link.style.top = `${Math.min(rect[1], rect[3])}px`;
      link.style.width = `${Math.abs(rect[2] - rect[0])}px`;
      link.style.height = `${Math.abs(rect[3] - rect[1])}px`;
      $("pdf-links").appendChild(link);
    }
    canvas.hidden = false;
    canvas.setAttribute("aria-label", `Resume page ${page} of ${pdf.numPages}`);
    $("page-count").textContent = `${page} / ${pdf.numPages}`;
    $("zoom-level").textContent = `${Math.round(zoom * 100)}%`;
    $("previous").disabled = page <= 1;
    $("next").disabled = page >= pdf.numPages;
    $("zoom-out").disabled = zoom <= 0.5;
    $("zoom-in").disabled = zoom >= 3;
    status.hidden = true;
  } catch {
    status.hidden = false;
    status.textContent = "The preview could not be displayed. You can still open or download the PDF.";
  } finally {
    rendering = false;
    if (pending) { pending = false; render(); }
  }
}

$("previous").onclick = () => { if (page > 1) { page--; render(); } };
$("next").onclick = () => { if (page < pdf.numPages) { page++; render(); } };
$("zoom-in").onclick = () => { zoom = Math.min(3, zoom + 0.25); render(); };
$("zoom-out").onclick = () => { zoom = Math.max(0.5, zoom - 0.25); render(); };
$("fit").onclick = () => { zoom = 1; render(); };
$("download").onclick = () => {
  if (!pdfBytes) { window.open(resumeUrl, "_blank", "noopener"); return; }
  const url = URL.createObjectURL(new Blob([pdfBytes], { type: "application/pdf" }));
  const link = document.createElement("a");
  link.href = url;
  link.download = "Mani-Resume.pdf";
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 60000);
};
let resizeTimer;
window.addEventListener("resize", () => {
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => { if (pdf) render(); }, 150);
});

try {
  const response = await fetch(`/portfolio-data/?_=${Date.now()}`, { cache: "no-store" });
  if (!response.ok) throw new Error();
  const config = await response.json();
  const url = new URL(config.hero?.resumeUrl || "");
  if (!["https:", "http:"].includes(url.protocol)) throw new Error();
  resumeUrl = url.href;
  $("open").href = resumeUrl;
  $("open").hidden = false;
  $("download").disabled = false;
  const pdfjs = await import("https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.10.38/pdf.min.mjs");
  pdfjs.GlobalWorkerOptions.workerSrc = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.10.38/pdf.worker.min.mjs";
  const file = await fetch(resumeUrl);
  if (!file.ok) throw new Error();
  pdfBytes = await file.arrayBuffer();
  pdf = await pdfjs.getDocument({ data: pdfBytes.slice(0) }).promise;
  $("fit").disabled = false;
  await render();
} catch {
  status.textContent = resumeUrl
    ? "The preview is unavailable. Please use Open PDF or Download to view the resume."
    : "The resume is not available right now. Please try again shortly.";
}
