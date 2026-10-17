const host = document.querySelector('.portrait');
const status = document.querySelector('#status');
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
let svg;
let visible = false;
let loading;

function updatePlayback() {
  if (!svg) return;
  if (reducedMotion.matches) {
    svg.pauseAnimations();
    svg.setCurrentTime(5.5);
    status.textContent = 'Portrait shown with reduced motion.';
  } else if (visible && !document.hidden) {
    svg.unpauseAnimations();
    status.textContent = 'Playing · 7-second loop';
  } else {
    svg.pauseAnimations();
    status.textContent = 'Paused while the portrait is out of view.';
  }
}

async function loadPortrait() {
  if (loading) return loading;
  loading = (async () => {
    const response = await fetch('profile-ascii.svg');
    if (!response.ok) throw new Error('Portrait could not be loaded.');
    const doc = new DOMParser().parseFromString(await response.text(), 'image/svg+xml');
    if (doc.querySelector('parsererror') || doc.documentElement.localName !== 'svg') {
      throw new Error('Portrait format is invalid.');
    }
    svg = document.importNode(doc.documentElement, true);
    host.replaceChildren(svg);
    // Pause and reset in the same task as insertion, before the first paint.
    svg.pauseAnimations();
    svg.setCurrentTime(0);
    host.setAttribute('aria-busy', 'false');
    updatePlayback();
  })().catch(error => {
    loading = undefined;
    host.setAttribute('aria-busy', 'false');
    status.textContent = error.message;
  });
  return loading;
}

const observer = new IntersectionObserver(entries => {
  visible = entries[0].isIntersecting && entries[0].intersectionRatio >= 0.4;
  if (visible) loadPortrait();
  updatePlayback();
}, { threshold: [0, 0.4] });
observer.observe(host);
reducedMotion.addEventListener('change', updatePlayback);
document.addEventListener('visibilitychange', () => {
  if (document.hidden) svg?.pauseAnimations();
  else updatePlayback();
});
document.querySelector('#replay').addEventListener('click', async () => {
  // Replaying outside the viewport must not start an unseen animation.
  if (visible) await loadPortrait();
  if (svg) svg.setCurrentTime(0);
  updatePlayback();
});
