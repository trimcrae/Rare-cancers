// Exercise filter/pagination state without launching a browser (morning-safe).
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
function element(value = '') {
  return {value, hidden: false, disabled: false, textContent: '', events: {},
    addEventListener(name, fn) { this.events[name] = fn; }, scrollIntoView() {}};
}
const controls = Object.fromEntries(['filters', 'pagination', 'records', 'literature-count', 'literature-page', 'literature-prev', 'literature-next', 'literature-reset'].map(k => [k, element()]));
for (const [key, value] of Object.entries({search: '', scope: 'focused', access: 'all', type: 'all', year: '', order: 'newest'})) controls['literature-' + key] = element(value);
const nodes = Array.from({length: 65}, (_, i) => Object.assign(element(), {
  textContent: i === 40 ? 'Unique sunitinib report' : `Record ${i}`,
  dataset: {year: String(2026 - i), scope: i === 64 ? 'full_text_or_index' : 'title',
    access: i % 2 ? 'unresolved' : 'free_link_indexed', types: i === 40 ? 'conference abstract' : 'journal article'}
}));
let order = [...nodes];
controls.records.append = node => { order = order.filter(x => x !== node); order.push(node); };
vm.runInNewContext(fs.readFileSync(path.join(__dirname, 'literature.js'), 'utf8'), {
  document: {getElementById: id => controls[id], querySelectorAll: () => nodes}
});
const visible = () => order.filter(x => !x.hidden);
const set = (field, value) => { const el = controls['literature-' + field]; el.value = value; el.events.input(); };
const click = field => controls['literature-' + field].events.click();
assert.equal(visible().length, 30);
assert.equal(controls['literature-count'].textContent.startsWith('64 matching records'), true);
click('next'); assert.equal(visible().length, 30);
click('next'); assert.equal(visible().length, 4); assert.equal(controls['literature-next'].disabled, true);
set('search', 'SUNITINIB'); assert.deepEqual(visible().map(x => x.textContent), ['Unique sunitinib report']);
set('access', 'unresolved'); assert.equal(visible().length, 0);
click('reset'); assert.equal(visible().length, 30);
set('type', 'conference'); assert.equal(visible().length, 1);
click('reset'); set('year', '2026'); assert.equal(visible().length, 1);
click('reset'); set('scope', 'all'); set('order', 'oldest'); assert.equal(visible()[0], nodes[64]);
console.log('Filter, empty-result, reset, pagination, year, type, case-insensitive search and sort checks passed (no browser).');
