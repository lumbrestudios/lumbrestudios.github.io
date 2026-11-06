(() => {
  const controls = document.querySelector('.gallery-controls');
  const buttons = [...document.querySelectorAll('[data-gallery-filter]')];
  const groups = [...document.querySelectorAll('[data-gallery-group]')];
  if (controls && groups.length) {
    controls.hidden = false;
    const select = button => {
      buttons.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
      groups.forEach(group => { group.hidden = group.dataset.galleryGroup !== button.dataset.galleryFilter; });
    };
    buttons.forEach(button => button.addEventListener('click', () => select(button)));
    select(buttons[0]);
  }
  const dialog = document.querySelector('#image-viewer');
  if (!dialog || typeof dialog.showModal !== 'function') return;
  const preview = dialog.querySelector('img');
  const title = dialog.querySelector('#viewer-title');
  const original = dialog.querySelector('.viewer-original');
  let trigger;
  document.querySelectorAll('a[data-full-image]').forEach(link => {
    link.addEventListener('click', event => {
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      trigger = link;
      const thumbnail = link.querySelector('img');
      preview.src = link.href;
      preview.alt = thumbnail.alt;
      title.textContent = link.dataset.caption || thumbnail.alt;
      original.href = link.href;
      dialog.showModal();
      document.body.style.overflow = 'hidden';
    });
  });
  dialog.addEventListener('keydown', event => {
    if (event.key !== 'Tab') return;
    const focusable = [...dialog.querySelectorAll('button, a[href]')];
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  });
  dialog.querySelector('button').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => { if (event.target === dialog) { const rect = dialog.getBoundingClientRect(); if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close(); } });
  dialog.addEventListener('close', () => { document.body.style.overflow = ''; preview.removeAttribute('src'); trigger?.focus(); });
})();
