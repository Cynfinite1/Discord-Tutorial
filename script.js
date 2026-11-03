// Table of Contents toggle on small screens
const toggle = document.querySelector('.toc-toggle');
const sidebar = document.getElementById('sidebar');
if (toggle && sidebar) {
  const set = (open) => { sidebar.classList.toggle('open', open); toggle.setAttribute('aria-expanded', String(open)); };
  toggle.addEventListener('click', (e) => { e.stopPropagation(); set(!sidebar.classList.contains('open')); });
  document.addEventListener('click', (e) => { if (sidebar.classList.contains('open') && !sidebar.contains(e.target)) set(false); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') set(false); });
}

// Keep the current page visible in the sidebar
const current = document.querySelector('.toc-list a[aria-current="page"]');
if (current && sidebar) {
  const r = current.getBoundingClientRect();
  if (r.bottom > window.innerHeight - 40) sidebar.scrollTop = current.offsetTop - 120;
}

// New words: show the definition on hover, keyboard focus, or tap
const tip = document.getElementById('term-tip');
let active = null;
function show(el) {
  active = el;
  tip.innerHTML = '';
  const b = document.createElement('b'); b.textContent = el.textContent;
  tip.append(b, document.createTextNode(el.dataset.def));
  tip.hidden = false;
  el.setAttribute('aria-describedby', 'term-tip');
  const r = el.getBoundingClientRect();
  const w = tip.offsetWidth, h = tip.offsetHeight;
  let left = Math.min(Math.max(8, r.left + r.width / 2 - w / 2), window.innerWidth - w - 8);
  let top = r.top - h - 8;
  if (top < 8) top = r.bottom + 8;
  tip.style.left = left + 'px'; tip.style.top = top + 'px';
}
function hide() { if (active) active.removeAttribute('aria-describedby'); active = null; tip.hidden = true; }
document.querySelectorAll('.term').forEach((el) => {
  el.addEventListener('mouseenter', () => show(el));
  el.addEventListener('mouseleave', hide);
  el.addEventListener('focus', () => show(el));
  el.addEventListener('blur', hide);
  el.addEventListener('click', (e) => { e.stopPropagation(); show(el); });
});
document.addEventListener('click', hide);
window.addEventListener('scroll', hide, { passive: true });
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') hide(); });
