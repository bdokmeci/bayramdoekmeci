// Execute the actual homepage script against a small DOM fixture for each locale.
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const assert = require('assert/strict');
const code = fs.readFileSync(path.join(__dirname, '../assets/home.js'), 'utf8');
for (const lang of ['de', 'en']) {
  const node = (extra = {}) => ({ hidden: false, textContent: '', attrs: {}, handlers: {},
    classList: { toggle() {} }, setAttribute(k, v) { this.attrs[k] = v; },
    addEventListener(k, fn) { this.handlers[k] = fn; }, focus() {}, ...extra });
  const web = node({ dataset: { search: lang === 'en' ? 'Web development websites' : 'Webentwicklung Websites' } });
  const ai = node({ dataset: { search: lang === 'en' ? 'AI automation workflows' : 'KI-Automatisierung Workflows' } });
  const counts = [node(), node()];
  const groups = [web, ai].map((service, i) => node({ dataset: { group: ['entwicklung', 'automation'][i] }, querySelectorAll: () => [service], querySelector: () => counts[i] }));
  const filters = ['all', 'entwicklung', 'automation'].map(filter => node({ dataset: { filter }, click() { this.handlers.click(); } }));
  const search = node({ value: '' }), status = node(), empty = node({ hidden: true }), reset = node();
  const root = { lang, scrollHeight: 2000, style: { setProperty() {} } };
  const nodes = { '.hero': { style: { setProperty() {} } }, '#service-search': search, '#filter-status': status, '.no-results': empty, '#reset-search': reset, '.directory-tools': node() };
  const doc = { documentElement: root, querySelector: s => nodes[s], querySelectorAll: s => ({ '[data-filter]': filters, '[data-group]': groups, '.service': [web, ai] })[s], addEventListener() {} };
  vm.runInNewContext(code, { document: doc, window: {}, matchMedia: () => ({ matches: true, addEventListener() {} }), addEventListener() {}, requestAnimationFrame: () => 1, setTimeout: fn => { fn(); return 1; }, clearTimeout() {}, scrollY: 0, innerHeight: 800 });
  search.value = lang === 'en' ? 'web development' : 'Webentwicklung';
  search.handlers.input();
  assert.equal(web.hidden, false); assert.equal(ai.hidden, true);
  assert.equal(counts[0].attrs['aria-label'], lang === 'en' ? '1 service' : '1 Leistung');
  assert.equal(status.textContent, lang === 'en' ? '1 of 2 services for “web development”.' : '1 von 2 Leistungen für „Webentwicklung“.');
  search.value = 'zzzz-no-match'; search.handlers.input();
  assert.equal(empty.hidden, false);
  reset.handlers.click();
  assert.equal(search.value, ''); assert.equal(web.hidden, false); assert.equal(ai.hidden, false); assert.equal(empty.hidden, true);
  filters[2].click();
  assert.equal(web.hidden, true); assert.equal(ai.hidden, false);
  assert.equal(filters[2].attrs['aria-pressed'], 'true');
}
console.log('Homepage locale regression: English/German search, singular counts, no results, reset and category filters passed.');
