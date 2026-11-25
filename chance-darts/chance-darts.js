'use strict';
// Progressive enhancement: all navigation and help remain available without JS.
const menuButton = document.querySelector('.menu-toggle');
const menu = document.querySelector('#product-menu');
function closeMenu(restoreFocus = false) {
  menu.hidden = true;
  menuButton.setAttribute('aria-expanded', 'false');
  menuButton.querySelector('span').textContent = '＋';
  if (restoreFocus) menuButton.focus();
}
if (menuButton && menu) {
  closeMenu();
  menuButton.hidden = false;
  menuButton.addEventListener('click', () => {
    const opening = menu.hidden;
    menu.hidden = !opening;
    menuButton.setAttribute('aria-expanded', String(opening));
    menuButton.querySelector('span').textContent = opening ? '−' : '＋';
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && !menu.hidden) closeMenu(true);
  });
  document.addEventListener('click', event => {
    if (!menu.hidden && !event.target.closest('.product-header')) closeMenu();
  });
}
const dialog = document.querySelector('#image-viewer');
if (dialog && typeof dialog.showModal === 'function') {
  const image = dialog.querySelector('img');
  const caption = dialog.querySelector('p');
  document.querySelectorAll('[data-viewer]').forEach(link => {
    link.addEventListener('click', event => {
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      image.src = link.href;
      image.alt = link.querySelector('img').alt;
      caption.textContent = image.alt;
      dialog.showModal();
    });
  });
  dialog.querySelector('button').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => {
    if (event.target === dialog) {
      const box = dialog.getBoundingClientRect();
      if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) dialog.close();
    }
  });
}
const search = document.querySelector('#help-search');
if (search) {
  search.closest('.help-search').hidden = false;
  const articles = [...document.querySelectorAll('.help-article')];
  const groups = [...document.querySelectorAll('.help-group')];
  const status = document.querySelector('#search-status');
  const normalize = value => value.toLowerCase().normalize('NFKD').replace(/[^a-z0-9]+/g, ' ').trim();
  function filterHelp() {
    const words = normalize(search.value).split(' ').filter(Boolean);
    let count = 0;
    for (const article of articles) {
      const matches = words.every(word => normalize(article.textContent).includes(word));
      article.hidden = !matches;
      article.open = matches && words.length > 0;
      if (matches) count++;
    }
    for (const group of groups) group.hidden = ![...group.querySelectorAll('.help-article')].some(article => !article.hidden);
    status.textContent = words.length ? (count ? `${count} ${count === 1 ? 'guide' : 'guides'} found.` : 'No guides found. Try “code”, “camera” or “Pro”, or contact support below.') : `${articles.length} guides. Choose a topic or search.`;
  }
  search.addEventListener('input', filterHelp);
  document.querySelectorAll('.help-topics a').forEach(link => link.addEventListener('click', () => {search.value = ''; filterHelp();}));
  filterHelp();
}
// Carry explicit campaign tags through product navigation without cookies, storage,
// pixels or network calls. Apple campaign tokens remain exactly as supplied.
const sourceParams = new URLSearchParams(location.search);
const campaignKeys = ['utm_source','utm_medium','utm_campaign','utm_content','utm_term','ct','pt','mt'];
const campaign = campaignKeys.filter(key => sourceParams.has(key));
if (campaign.length) {
  document.querySelectorAll('a[href]').forEach(link => {
    const url = new URL(link.href, location.href);
    const internal = url.origin === location.origin && url.pathname.startsWith('/chance-darts/');
    const appStore = link.hasAttribute('data-store') && url.hostname === 'apps.apple.com';
    if (!internal && !appStore) return;
    for (const key of campaign) {
      if (!url.searchParams.has(key)) url.searchParams.set(key, sourceParams.get(key));
    }
    link.href = url.toString();
  });
}
