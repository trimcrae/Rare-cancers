"""Independent coordinate, outcome arithmetic and rank-statistic verification.

Usage: python coordinator_verify.py WORKER_OUTPUT OUTPUT_JSON
Requires Pillow and scipy. Does not modify worker outputs.
Visual source checks are recorded separately; arithmetic is not semantic validation.
"""
import hashlib
import json
import math
import sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, 'C:/Projects/EMC-Research/.cache/python-deps')
from PIL import Image
from scipy.stats import spearmanr

root = Path(sys.argv[1]).resolve()
dest = Path(sys.argv[2]).resolve()
read = lambda name: json.loads((root / name).read_text(encoding='utf-8'))
dataset = read('dataset.json')
coordinates = read('extraction-coordinates.json')
analysis = read('analysis.json')
designs = {d['design_id']: d for d in dataset['designs']}
outcomes = {(d['design_id'], d['endpoint']): d for d in dataset['outcomes']}
assert len(designs) == 31 and len(outcomes) == 93
pixel_checks = []
for screen in coordinates['screens']:
    im = Image.open(root / 'inspections' / screen['image']).convert('RGB')
    low, high = screen['axis_ticks']
    slope = (high['value'] - low['value']) / (high['y'] - low['y'])
    for bar in screen['bars']:
        key = (f"{screen['target']}_{bar['design_number']:02d}", bar['endpoint'])
        outcome = outcomes[key]
        if bar['y_mean'] is None:
            assert key == ('SS_04', 'measured_parent')
            assert outcome['relative_expression_mean'] is None
            assert outcome['reading_high'] is None
            continue
        value = low['value'] + slope * (bar['y_mean'] - low['y'])
        assert math.isclose(value, outcome['relative_expression_mean'], abs_tol=1e-12)
        assert outcome['reading_low'] <= value <= outcome['reading_high']
        assert math.isclose(outcome['plotted_SD'], abs(slope) * (bar['y_mean'] - bar['y_sd_upper']), abs_tol=1e-12)
        # Independently locate a colored bar edge near the supplied coordinate.
        # Use multiple interior pixels away from the neutral error-bar line.
        hits = []
        for y in range(max(int(high['y']), int(bar['y_mean']) - 12), int(bar['y_mean']) + 13):
            count = 0
            for dx in [-4, -3, 3, 4]:
                r, g, b = im.getpixel((int(bar['x_center']) + dx, y))
                colored = b - r > 15 if screen['target'] == 'B4N' else g - r > 9 and g - b > 9
                count += colored
            if count >= 3:
                hits.append(y)
        assert hits, key
        difference = min(hits) - bar['y_mean']
        assert abs(difference) <= screen['mean_reading_halfwidth_px'], (key, difference)
        pixel_checks.append({'design': key[0], 'endpoint': key[1], 'edge_minus_retained_y_px': difference})

rank_checks = []
for result in analysis['associations']:
    rows = [r for r in dataset['outcomes'] if r['target'] == result['target'] and r['endpoint'] == result['endpoint'] and r['relative_expression_mean'] is not None]
    x = [designs[r['design_id']][result['feature']] for r in rows]
    y = [r['relative_expression_mean'] for r in rows]
    actual = float(spearmanr(x, y).statistic)
    assert math.isclose(actual, result['spearman_remaining'], abs_tol=1e-12)
    assert math.isclose(-actual, result['spearman_suppression_index'], abs_tol=1e-12)
    assert len(rows) == result['n_quantitative_designs']
    for sensitivity in result['sensitivity']:
        intervals = []
        for r in rows:
            half = (r['reading_high'] - r['reading_low']) * sensitivity['reading_halfwidth_multiplier'] / 2
            intervals.append((r['relative_expression_mean'] - half, r['relative_expression_mean'] + half))
        overlaps = sum(max(a[0], b[0]) <= min(a[1], b[1]) for i, a in enumerate(intervals) for b in intervals[:i])
        assert overlaps == sensitivity['ambiguous_order_pairs']
    rank_checks.append({'target': result['target'], 'endpoint': result['endpoint'], 'feature': result['feature'], 'scipy_spearman': actual, 'n': len(rows)})

for d in designs.values():
    a = d['antisense_core_5to3']
    assert d['gc_fraction'] == (a.count('G') + a.count('C')) / 19
    assert d['terminal_gc_asymmetry'] == (sum(a[-4:].count(c) for c in 'GC') - sum(a[:4].count(c) for c in 'GC')) / 4
    missing = outcomes[(d['design_id'], 'second_parent')]
    assert missing['relative_expression_mean'] is None

report = {'utc': datetime.now(timezone.utc).isoformat(), 'source_root': str(root),
          'status': 'passed', 'colored_mean_edges_checked': len(pixel_checks),
          'pixel_checks': pixel_checks, 'independent_scipy_rank_checks': rank_checks,
          'limitations': ['Coordinate neighborhood check is supported by a separate visual source review, not blind re-digitization.', 'SD coordinates visually reviewed; arithmetic checked here, no biological replication verified.', 'Seeded sensitivity simulation remains a reproduction check, not exhaustive rank bounds.'],
          'input_sha256': {name: hashlib.sha256((root/name).read_bytes()).hexdigest() for name in ['dataset.json', 'analysis.json', 'extraction-coordinates.json', 'protocol.md']}}
dest.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'status': report['status'], 'mean_edges': len(pixel_checks), 'rank_checks': len(rank_checks), 'receipt': str(dest)}))
