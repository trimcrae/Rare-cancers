"""Render public bibliographic metadata only; never export the research workspace."""
from datetime import date
from html import escape
import json
from pathlib import Path
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent

def safe_url(url):
    parts = urlsplit(url)
    if parts.scheme not in ('https', 'http') or not parts.hostname or parts.username or parts.password:
        raise ValueError(f'Invalid public literature URL: {url!r}')
    return escape(url, quote=True)

def render():
    data = json.loads((HERE / 'literature.json').read_text(encoding='utf-8'))
    date.fromisoformat(data['updated_date'])
    records = data['records']
    if len({p['id'] for p in records}) != len(records):
        raise ValueError('Duplicate literature IDs')
    rows = []
    for p in records:
        if p['access'] not in ('free_link_indexed', 'unresolved'):
            raise ValueError('Unsupported access claim')
        if p['access'] == 'free_link_indexed' and not p['free_links']:
            raise ValueError('Free access requires source evidence')
        links = [f'<a href="{safe_url(p["record_url"])}">Source record</a>']
        for link in p['free_links'][:3]:
            if not link.get('evidence'):
                raise ValueError('Missing access provenance')
            links.append(f'<a href="{safe_url(link["url"])}">{escape(link["label"])}</a>')
        if p['publisher_url']:
            links.append(f'<a href="{safe_url(p["publisher_url"])}">Publisher / DOI</a>')
        for link in p.get('related_links', []):
            links.append(f'<a href="{safe_url(link["url"])}">{escape(link["label"])}</a>')
        types = ', '.join(p['publication_types']) or 'Type not supplied'
        scope = {'title': 'Title match', 'abstract': 'Abstract match', 'full_text_or_index': 'Full text / index match'}[p['discovery_scope']]
        access = 'Free link indexed' if p['free_links'] else 'Access unresolved'
        note = f'<p class="record-note">{escape(p["relation_note"])}</p>' if p.get('relation_note') else ''
        rows.append(f'''<article class="literature-record" data-year="{escape(str(p['year']), quote=True)}" data-scope="{p['discovery_scope']}" data-access="{p['access']}" data-types="{escape(types.lower(), quote=True)}">
<p class="record-meta">{escape(str(p['year']))} · {escape(p['journal'] or 'Venue not supplied')} · {escape(types)}</p>
<h3>{escape(p['title'])}</h3><p class="record-authors">{escape(p['authors'])}</p>
<p class="record-status">{scope} · {access} · {escape(p['screening_status'].replace('_', ' '))}</p>
<div class="record-links">{' '.join(links)}</div>{note}</article>''')
    counts = data['counts']
    focused = sum(p['discovery_scope'] != 'full_text_or_index' for p in records)
    queries = ''.join(f'<li><a href="{safe_url(q["url"])}">{escape(name.replace("_", " "))}</a>: {q["hit_count"]:,} search records. {escape(q.get("note", ""))}</li>' for name, q in data['queries'].items())
    html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>EMC literature | EMC Research</title><meta name="description" content="Searchable EMC literature discovery catalogue with source records, free full-text links and transparent coverage limits.">
<link rel="stylesheet" href="styles.css"><link rel="icon" href="favicon.svg"><script src="literature.js" defer></script></head>
<body><a class="skip-link" href="#records">Skip to literature</a><header class="site-header wrap"><a class="brand" href="./">EMC <strong>Research</strong></a><nav aria-label="Main navigation"><a href="./">Preprints</a><a href="#coverage">Coverage</a></nav></header>
<main class="wrap literature-page"><h1>EMC literature</h1><p class="intro">A shared index of research on extraskeletal myxoid chondrosarcoma, including routes to free full text and conference reports.</p>
<p><strong>{len(records):,} discovery records · {focused:,} title or abstract matches</strong><br>Search snapshot: {data['updated_date']}. Screening is in progress; the worldwide total of distinct EMC studies is not established.</p>
<div class="literature-filters" id="filters" hidden><label>Search titles, authors or venues<input id="literature-search" type="search" placeholder="e.g. NR4A3, sunitinib, Pauli"></label>
<label>Match location<select id="literature-scope"><option value="focused">Title or abstract</option><option value="all">All discovery records</option><option value="title">Title only</option><option value="full_text_or_index">Full text / index only</option></select></label>
<label>Access<select id="literature-access"><option value="all">Any access</option><option value="free_link_indexed">Free link indexed</option><option value="unresolved">Access unresolved</option></select></label>
<label>Report type<select id="literature-type"><option value="all">All types</option><option value="review">Reviews</option><option value="case reports">Case reports</option><option value="clinical trial">Clinical trials</option><option value="conference">Conference reports</option><option value="preprint">Preprints</option></select></label>
<label>Year<input id="literature-year" type="number" min="1900" max="2100" placeholder="Any year"></label>
<label>Order<select id="literature-order"><option value="newest">Newest first</option><option value="oldest">Oldest first</option></select></label><button id="literature-reset" type="button">Reset filters</button></div>
<p id="literature-count" role="status" aria-live="polite">{len(records):,} records. Enable JavaScript for search and filters.</p>
<noscript><p>All records appear below in newest-first order. Use your browser’s Find command to search.</p></noscript>
<div id="records">{''.join(rows)}</div><div class="literature-pagination" id="pagination" hidden><button id="literature-prev" type="button">Previous</button><span id="literature-page"></span><button id="literature-next" type="button">Next</button></div>
<section id="coverage" class="literature-coverage"><h2>Coverage and interpretation</h2>
<p>This is a discovery catalogue, not a claim that every listed record contains original EMC results. Title and abstract matches are automated screening aids. Broader matches may mention EMC only in background or references. Papers about other tumour types that resemble EMC also need exclusion after review.</p>
<p>Searches include the disease name, a hyphenated spelling, selected historical fusion names and model names such as H-EMC-SS. Model-name matches require molecular identity checks before their findings are treated as EMC evidence. The catalogue includes journal reports and preprints indexed by Europe PMC, with separately sourced conference records and other outputs where available. Society abstract books, posters, institutional repositories, trial results, non-English literature and EMC subgroup tables remain incompletely covered. Report types largely reflect source metadata; some meeting supplements are indexed as journal articles and will not yet appear under the conference filter.</p>
<p>“Free link indexed” means a public bibliographic source supplies a free-text link; it does not certify a working download, a complete supplement set or a completed reading. Conference abstracts are abstracts, even when their entire text is free. “Access unresolved” is not “paywall only”: use the publisher link while a repository copy is sought. Nothing here asserts that no free version exists.</p>
<p>Identical DOIs and database identifiers are deduplicated. Preprint versions, meeting reports and journal articles can describe the same study; patient cohorts can overlap. These records must not be summed as independent studies or patients. Inclusion does not endorse a result or establish clinical efficacy.</p>
<h3>Search sources</h3><ul>{queries}</ul><p><a href="literature.json">Download catalogue and search metadata (JSON)</a>. Bibliographic metadata and links only; article copyrights remain with their respective holders.</p></section></main>
<footer class="site-footer wrap"><span>EMC Research</span><p>Research information, not medical advice.</p><a href="./">Back to preprints</a></footer></body></html>'''
    return html, len(records), focused
