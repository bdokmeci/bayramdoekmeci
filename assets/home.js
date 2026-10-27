(() => {
  'use strict';

  const root = document.documentElement;
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const hero = document.querySelector('.hero');
  const search = document.querySelector('#service-search');
  const filters = [...document.querySelectorAll('[data-filter]')];
  const groups = [...document.querySelectorAll('[data-group]')];
  const services = [...document.querySelectorAll('.service')];
  const status = document.querySelector('#filter-status');
  const noResults = document.querySelector('.no-results');
  let currentFilter = 'all';
  let scrollFrame = 0;
  let pointerFrame = 0;
  let searchTimer;

  // Links and descriptions are rendered in HTML; JS only adds optional controls.
  document.querySelector('.directory-tools').hidden = false;
  const normalize = value => value.toLocaleLowerCase('de').normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '').replace(/ß/g, 'ss').replace(/[^a-z0-9]+/g, ' ').trim();
  const searchIndex = new Map(services.map(service => [service, normalize(service.dataset.search)]));

  function filterServices() {
    const terms = normalize(search.value).split(/\s+/).filter(Boolean);
    let count = 0;
    groups.forEach(group => {
      const categoryMatches = currentFilter === 'all' || group.dataset.group === currentFilter;
      let groupCount = 0;
      group.querySelectorAll('.service').forEach(service => {
        const matches = categoryMatches && terms.every(term => searchIndex.get(service).includes(term));
        service.hidden = !matches;
        if (matches) groupCount++;
      });
      group.hidden = groupCount === 0;
      group.querySelector('.group-count').textContent = String(groupCount).padStart(2, '0');
      group.querySelector('.group-count').setAttribute('aria-label', `${groupCount} Leistungen`);
      count += groupCount;
    });
    noResults.hidden = count !== 0;
    status.textContent = `${count} von ${services.length} Leistungen${search.value.trim() ? ` für „${search.value.trim()}“` : ''}.`;
    status.classList.toggle('sr-only', !search.value.trim() && currentFilter === 'all');
    requestScrollUpdate();
  }

  filters.forEach(button => button.addEventListener('click', () => {
    currentFilter = button.dataset.filter;
    filters.forEach(filter => {
      const selected = filter === button;
      filter.classList.toggle('is-active', selected);
      filter.setAttribute('aria-pressed', String(selected));
    });
    filterServices();
  }));
  search.addEventListener('input', () => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(filterServices, 100);
  });
  document.querySelector('#reset-search').addEventListener('click', () => {
    clearTimeout(searchTimer);
    search.value = '';
    filters[0].click();
    search.focus({ preventScroll: true });
  });
  document.addEventListener('keydown', event => {
    const editing = event.target instanceof Element && event.target.closest('input, textarea, select, [contenteditable="true"]');
    if (event.key === '/' && !editing && !event.ctrlKey && !event.metaKey && !event.altKey) {
      event.preventDefault();
      search.focus();
    }
    if (event.key === 'Escape' && document.activeElement === search && search.value) {
      clearTimeout(searchTimer);
      search.value = '';
      filterServices();
    }
  });

  function updateScroll() {
    scrollFrame = 0;
    const scrollRange = root.scrollHeight - innerHeight;
    const progress = scrollRange > 0 ? Math.min(1, Math.max(0, scrollY / scrollRange)) : 0;
    root.style.setProperty('--scroll', progress.toFixed(4));
    const shift = reducedMotion.matches ? 0 : Math.min(scrollY, 650) * .12;
    hero.style.setProperty('--hero-shift', `${shift.toFixed(1)}px`);
  }
  function requestScrollUpdate() {
    if (!scrollFrame) scrollFrame = requestAnimationFrame(updateScroll);
  }
  addEventListener('scroll', requestScrollUpdate, { passive: true });
  addEventListener('resize', requestScrollUpdate, { passive: true });
  addEventListener('pageshow', requestScrollUpdate);
  if ('ResizeObserver' in window) new ResizeObserver(requestScrollUpdate).observe(document.body);
  reducedMotion.addEventListener('change', requestScrollUpdate);
  updateScroll();

  // Restore the directory after browser back/forward navigation and autofill.
  if (search.value) filterServices();
})();
