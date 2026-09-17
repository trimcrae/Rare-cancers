"""Render the reviewed cross-paper evidence matrix from explicit public data."""
from datetime import date
from html import escape
import json
from pathlib import Path
from literature_page import safe_url

HERE = Path(__file__).resolve().parent


def validate(data):
    date.fromisoformat(data['updated_date'])
    ids = [s['id'] for s in data['sources']]
    if len(set(ids)) != len(ids):
        raise ValueError('Duplicate source IDs')
    hypotheses = data['hypotheses']
    if len({h['id'] for h in hypotheses}) != len(hypotheses):
        raise ValueError('Duplicate hypothesis IDs')
    if sorted(h['rank'] for h in hypotheses) != list(range(1, len(hypotheses) + 1)):
        raise ValueError('Research priorities must be unique and contiguous')
    for source in data['sources']:
        safe_url(source['url'])
        for key in ('label', 'location', 'denominator', 'observation', 'limitation', 'reading'):
            if not source.get(key):
                raise ValueError('Missing source evidence field: ' + key)
    for item in hypotheses + data['rejected_shortcuts']:
        if not item['source_ids'] or not set(item['source_ids']).issubset(ids):
            raise ValueError('Unresolved evidence reference')
    for h in hypotheses:
        if len(set(h['source_ids'])) < 2:
            raise ValueError('Cross-paper inference needs at least two source records')
        for key in ('inference', 'against', 'available_test', 'missing_test', 'falsifier', 'novelty', 'decision'):
            if not h.get(key):
                raise ValueError('Missing hypothesis limit/test: ' + key)


def render():
    data = json.loads((HERE / 'synthesis.json').read_text(encoding='utf-8'))
    check = json.loads((HERE / 'synthesis-check.json').read_text(encoding='utf-8'))
    validate(data)
    e = escape
    sources = {s['id']: s for s in data['sources']}

    def refs(ids):
        return ' · '.join(f'<a href="#source-{e(i)}">{e(sources[i]["label"])}</a>' for i in ids)

    summary_rows, cards = [], []
    for h in sorted(data['hypotheses'], key=lambda h: h['rank']):
        summary_rows.append(f'<tr><td>{h["rank"]}</td><th scope="row"><a href="#{e(h["id"])}">{e(h["title"])}</a></th><td>{e(h["status"])}</td></tr>')
        fields = [('inference', 'Connection across studies'), ('against', 'What could explain it instead?'),
                  ('available_test', 'What the available data can test'), ('missing_test', 'Missing evidence and discriminating test'),
                  ('falsifier', 'What would weaken this hypothesis?'), ('novelty', 'Was this already proposed?'),
                  ('decision', 'Research decision')]
        body = ''.join(f'<dt>{label}</dt><dd>{e(h[key])}</dd>' for key, label in fields)
        cards.append(f'<section class="hypothesis" id="{e(h["id"])}"><p class="eyebrow">Research priority {h["rank"]}</p><h2>{e(h["title"])}</h2><p class="status-chip">{e(h["status"])}</p><p class="source-links">{refs(h["source_ids"])}</p><dl>{body}</dl></section>')
    evidence = []
    for s in data['sources']:
        evidence.append(f'<details id="source-{e(s["id"])}"><summary>{e(s["label"])}</summary><p><a href="{safe_url(s["url"])}">Open primary source ↗</a></p><dl>'+''.join(f'<dt>{label}</dt><dd>{e(s[key])}</dd>' for key,label in [('location','Source location'),('denominator','Patients / models'),('observation','Reported observation'),('limitation','Limits'),('reading','Reading coverage')])+'</dl></details>')
    rejected = ''.join(f'<li><strong>{e(r["title"])}</strong><p>{e(r["reason"])}</p><p>{refs(r["source_ids"])}</p></li>' for r in data['rejected_shortcuts'])
    drug_rows = ''.join(f'<tr><th scope="row">{e(r["drug"])}</th><td>{r["viability_percent"]:.1f}</td><td>{r["sd_percentage_points"]:.1f}</td><td>{r["source_row"]}</td></tr>' for r in check['rows_sorted_by_mean_viability'])
    html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cross-paper evidence matrix | EMC Research</title><meta name="description" content="Connections across EMC studies, conflicting evidence, prior proposals and specific tests. A bounded research synthesis with source-level provenance."><link rel="stylesheet" href="styles.css"><link rel="icon" href="favicon.svg"></head>
<body><a class="skip-link" href="#matrix">Skip to evidence matrix</a><header class="site-header wrap"><a class="brand" href="./">EMC <strong>Research</strong></a><nav aria-label="Main navigation"><a href="./">Preprints</a><a href="literature.html">Literature</a></nav></header>
<main class="wrap synthesis-page"><p class="eyebrow">Cross-paper synthesis · {data['updated_date']}</p><h1>{e(data['title'])}</h1><p class="synthesis-conclusion">{e(data['conclusion'])}</p><p>{e(data['scope'])}</p>
<p class="source-links"><a href="synthesis.json">Download evidence matrix (JSON)</a> · <a href="synthesis-check.json">Download reproducible screen comparison</a> · <a href="#evidence">Source evidence and reading limits</a></p>
<div class="table-scroll" tabindex="0" role="region" aria-label="Research priorities"><table id="matrix"><caption>Priority reflects the value of answering a research question, not the efficacy of a treatment.</caption><thead><tr><th scope="col">Priority</th><th scope="col">Question</th><th scope="col">Current assessment</th></tr></thead><tbody>{''.join(summary_rows)}</tbody></table></div>
<section class="screen-check" id="screen-check"><h2>A comparison actually run on the available data</h2><p>{e(check['result'])}</p><div class="table-scroll" tabindex="0" role="region" aria-label="Independent drug screen"><table><caption>NCC-EMC1-C1 · Iwata supplementary Table 3. One donor model. Lower values indicate a lower reported viability-assay readout.</caption><thead><tr><th scope="col">Drug</th><th scope="col">Mean viability (%)</th><th scope="col">Reported SD (percentage points)</th><th scope="col">Source row</th></tr></thead><tbody>{drug_rows}</tbody></table></div><p>{e(check['scope'])}</p><p>{e(check['methodological_warning'])}</p><p>Exposure duration and screen concentration remain unresolved. This table does not compare clinical doses or establish selective toxicity.</p></section>
{''.join(cards)}<section class="hypothesis"><h2>Connections rejected or withheld</h2><ul>{rejected}</ul></section><section id="evidence" class="hypothesis"><h2>Source evidence and reading limits</h2><p>Expand a source to inspect its denominator, exact location, observation and limitations. Multiple reports may reuse patients; no pooled patient total is calculated here.</p>{''.join(evidence)}</section>
<section class="hypothesis"><h2>Novelty check</h2><p>{e(data['novelty_search']['method'])} Searches checked {data['novelty_search']['date']}.</p><ul>{''.join('<li>'+e(q)+'</li>' for q in data['novelty_search']['queries'])}</ul></section></main><footer class="site-footer wrap"><span>EMC Research</span><p>Research hypotheses require experimental and clinical validation.</p><a href="literature.html">Back to literature</a></footer></body></html>'''
    return html
