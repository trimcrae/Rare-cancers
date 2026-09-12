'use strict';
(() => {
  const byId = id => document.getElementById(id);
  const entries = Array.from(document.querySelectorAll('.literature-record')).map((node, index) => ({node, index, text: node.textContent.toLocaleLowerCase()}));
  const keys = ['search', 'scope', 'access', 'type', 'year', 'order'];
  const fields = Object.fromEntries(keys.map(k => [k, byId('literature-' + k)]));
  const pageSize = 30;
  let page = 0;
  function update() {
    const term = fields.search.value.trim().toLocaleLowerCase();
    const matches = entries.filter(({node, text}) => {
      const d = node.dataset;
      return (!term || text.includes(term)) &&
        (fields.scope.value === 'all' || (fields.scope.value === 'focused' ? d.scope !== 'full_text_or_index' : d.scope === fields.scope.value)) &&
        (fields.access.value === 'all' || d.access === fields.access.value) &&
        (fields.type.value === 'all' || d.types.includes(fields.type.value)) &&
        (!fields.year.value || d.year === fields.year.value);
    });
    if (fields.order.value === 'oldest') matches.reverse();
    const pages = Math.max(1, Math.ceil(matches.length / pageSize));
    page = Math.min(page, pages - 1);
    entries.forEach(({node}) => { node.hidden = true; });
    matches.slice(page * pageSize, (page + 1) * pageSize).forEach(({node}) => { node.hidden = false; byId('records').append(node); });
    byId('literature-count').textContent = `${matches.length.toLocaleString()} matching records${matches.length ? ` · showing ${page * pageSize + 1}–${Math.min((page + 1) * pageSize, matches.length)}` : ' · Try fewer filters.'}`;
    byId('literature-page').textContent = `Page ${page + 1} of ${pages}`;
    byId('literature-prev').disabled = page === 0;
    byId('literature-next').disabled = page + 1 >= pages;
  }
  Object.values(fields).forEach(field => field.addEventListener('input', () => { page = 0; update(); }));
  byId('literature-reset').addEventListener('click', () => {
    fields.search.value = ''; fields.scope.value = 'focused'; fields.access.value = 'all'; fields.type.value = 'all'; fields.year.value = ''; fields.order.value = 'newest'; page = 0; update();
  });
  byId('literature-prev').addEventListener('click', () => { page--; update(); byId('literature-count').scrollIntoView(); });
  byId('literature-next').addEventListener('click', () => { page++; update(); byId('literature-count').scrollIntoView(); });
  byId('filters').hidden = false; byId('pagination').hidden = false; update();
})();
