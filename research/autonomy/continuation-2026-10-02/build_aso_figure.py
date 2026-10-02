#!/usr/bin/env python3
"""Frozen ASO source-corpus sensitivity; run on cloud with matplotlib, not locally.
Usage: python build_aso_figure.py --source results/aso-transcriptome.json --out figures
Produces SVG, PNG, plot-value TSV and provenance/caption manifest. No inference tests.
"""
import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

REF = 'd39296bdf4114e7bf366c8a9ffeefc22e6cfb71f'
SOURCE_PATH = 'research/autonomy/continuation-2026-10-02/results/aso-transcriptome.json'
SHA = 'ffec759ac33c734d8aa28aa2f71f9f2b5e8296c8ece0e21f8a744606ba1d37ec'
BINS = [0] + list(range(6, 17))
PANELS = [
    ('Deposited sequence matches', ['deposited_sequence_match'], 25),
    ('Other reference reconstructions', ['coordinate_based_reference_reconstruction',
                                         'construct_description_reference_reconstruction'], 10),
    ('Hypothetical reference joins', ['hypothetical_exact_reference_join'], 180),
]
CAPTION = (
    'Reference-corpus sensitivity of the maximum contiguous exact match containing the '
    'complete six-nucleotide DNA core of each 16-nucleotide target (positions 6–11, one-based). '
    'Gray: 85 archived normal-parent transcript records; blue: their union with 670,670 '
    'GENCODE v50 annotated mature transcript records, including haplotypes. All 215 target '
    'designs are included: 25 deposited-sequence matches, 10 other reference reconstructions '
    '(5 coordinate-based and 5 construct-description-based), and 180 hypothetical joins. '
    'The 5 annotation-error control designs are excluded. The none (0) bin denotes no '
    'perfect complete-core match; it does not denote absence of complementarity. Horizontal '
    'units are nucleotides; vertical units are design counts, with a common scale. Each '
    'design contributes once to each corpus histogram; panels do not show paired trajectories. '
    'Longer matches occurred in 23/25, 10/10 and 179/180 designs, respectively. Designs '
    'overlap within junctions and are not independent patients. No error bars or confidence '
    'intervals are intended. These are sequence descriptors, not validated selectivity, '
    'cleavage, expression, accessibility, safety or efficacy measurements.'
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    raw = args.source.read_bytes()
    require(len(raw) == 435970 and hashlib.sha256(raw).hexdigest() == SHA, 'Source pin mismatch')
    source = json.loads(raw)
    require(source['schema'] == 'aso-transcriptome-extension/1', 'Unexpected source schema')
    designs = source['designs']
    require(len(designs) == 220 and len({d['design_id'] for d in designs}) == 220, 'Design IDs')
    controls = [d for d in designs if d['control']]
    targets = [d for d in designs if not d['control']]
    require(len(controls) == 5 and len(targets) == 215, 'Target/control counts')
    require(all(d['evidence_class'] == 'annotation_error_control' for d in controls), 'Controls')
    classes = {c for _, cs, _ in PANELS for c in cs}
    require({d['evidence_class'] for d in targets} == classes, 'Evidence classes')
    require(all(d['archive_gap'] in BINS and d['union_gap'] in BINS and
                d['union_gap'] >= d['archive_gap'] for d in targets), 'Invalid core-run values')
    rows, panels = [], []
    for title, classes, expected in PANELS:
        group = [d for d in targets if d['evidence_class'] in classes]
        require(len(group) == expected, 'Panel denominator')
        counts = [Counter(d[key] for d in group) for key in ('archive_gap', 'union_gap')]
        panels.append((title, expected, counts))
        for corpus, count in zip(('archived_parent', 'archive_plus_gencode_v50'), counts):
            rows.extend((title, corpus, value, count[value], expected) for value in BINS)
    require([sum(d['union_gap'] > d['archive_gap'] for d in targets if d['evidence_class'] in cs)
             for _, cs, _ in PANELS] == [23, 10, 179], 'Caption change counts')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'svg.hashsalt': SHA})
    args.out.mkdir(parents=True, exist_ok=True)
    stem = args.out / 'aso-corpus-gap-sensitivity'
    fig, axes = plt.subplots(1, 3, figsize=(13.8, 5), sharey=True, layout='constrained')
    for ax, (title, n, counts) in zip(axes, panels):
        for offset, count, color, label in zip((-.2, .2), counts, ('#737373', '#0072B2'),
                                              ('Archived parents', 'Expanded union')):
            ax.bar([x + offset for x in range(len(BINS))], [count[b] for b in BINS],
                   width=.38, color=color, label=label)
        ax.set_xticks(range(len(BINS)), ['none\n(0)'] + [str(b) for b in BINS[1:]])
        ax.set_title(f'{title}\n{n} designs', fontsize=11)
        ax.set_xlabel('Maximum complete-core match (nt)', labelpad=8)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_axisbelow(True)
        ax.grid(axis='y', color='#dddddd', linewidth=.6)
        ax.spines[['top', 'right']].set_visible(False)
    axes[0].set_ylabel('Number of designs')
    axes[0].legend(loc='upper left', frameon=False, fontsize=9)
    fig.suptitle('Sequence descriptor sensitivity to the reference corpus', fontsize=14)
    fig.savefig(stem.with_suffix('.svg'), metadata={'Date': None, 'Description': CAPTION})
    fig.savefig(stem.with_suffix('.png'), dpi=180, metadata={'Description': CAPTION})
    plt.close(fig)
    with stem.with_suffix('.tsv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t', lineterminator='\n')
        writer.writerow(['panel', 'corpus', 'complete_core_match_nt', 'design_count', 'panel_n'])
        writer.writerows(rows)
    artifacts = {ext: hashlib.sha256(stem.with_suffix(ext).read_bytes()).hexdigest()
                 for ext in ('.svg', '.png', '.tsv')}
    manifest = dict(source_revision=REF, source_path=SOURCE_PATH, source_sha256=SHA,
                    source_bytes=len(raw), targets=215, excluded_annotation_controls=5,
                    matplotlib_version=matplotlib.__version__, caption=CAPTION,
                    artifact_sha256=artifacts, visual_inspection='pending; generation is not visual QA')
    stem.with_suffix('.manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(manifest, sort_keys=True))


if __name__ == '__main__':
    main()
