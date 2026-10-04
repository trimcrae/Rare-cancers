"""Offline arithmetic and evidence-integrity check; no new experiments."""
import csv
import datetime
import hashlib
import json
import math
from pathlib import Path
import re
import statistics as stats
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
sys.path.insert(0, str(ROOT / '.cache/python-deps'))
import numpy as np


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def A(x, y):
    return sum((a > b) + 0.5 * (a == b) for a in x for b in y) / (len(x) * len(y))


def check_stat(values, saved):
    for key, sl in [('EMC', slice(0, 6)), ('LGFMS', slice(6, 23)), ('muscle', slice(23, 25))]:
        assert len(values[sl]) == len(saved[key])
        assert max(abs(a-b) for a, b in zip(values[sl], saved[key])) < 1e-12
    assert math.isclose(A(values[:6], values[6:23]), saved['A'], abs_tol=1e-14)
    assert math.isclose(stats.median(values[:6]), saved['EMC_median'], abs_tol=1e-12)
    assert math.isclose(stats.median(values[6:23]), saved['LGFMS_median'], abs_tol=1e-12)


def main():
    r = json.loads((BASE / 'raw-array-results.json').read_text())
    assert r['map_sha256'] == sha(BASE / 'probe-map.csv')
    assert r['metadata_sha256'] == sha(ROOT / 'research/autonomy/atlas-primary-provenance-2026-09-06/GSE24369.soft.gz')
    rows = list(csv.DictReader((BASE / 'probe-map.csv').open()))
    ids = [int(x['physical_probe_id']) for x in rows]
    assert len(ids) == len(set(ids)) == 30
    regions = {g: [i for i, row in enumerate(rows) if int(row['child_probeset']) == g]
               for g in sorted({int(row['child_probeset']) for row in rows})}
    assert len(r['arrays']) == 25
    arrays = []
    for arr in r['arrays']:
        assert arr['finite_features'] == 1102500 and arr['nonfinite_features'] == 0
        assert [p['id'] for p in arr['selected']] == ids
        assert all(p['raw'] > 0 for p in arr['selected'])
        arrays.append(arr['selected'])
    def score(gs, metric):
        return [stats.mean(stats.mean((math.log2(arr[i]['raw']) if metric == 'log2raw' else arr[i][metric])
                                      for i in regions[g]) for g in gs) for arr in arrays]
    groups = {'upstream': list(range(7985069, 7985075)), 'downstream': [7985076, 7985077, 7985078],
              'UTR': [7985067, 7985068, 7985079], 'antisense_shared': [7985075],
              'strict_current_CDS': list(range(7985070, 7985075))}
    checked_stats = 0
    for name, gs in groups.items():
        for key, metric in [('percentile', 'percentile'), ('log2raw', 'log2raw'),
                            ('GC_control_percentile', 'gc_control_mean_percentile')]:
            if key not in r['summary'][name]:
                continue
            check_stat(score(gs, metric), r['summary'][name][key]); checked_stats += 1
    for g in regions:
        for metric in ['percentile', 'log2raw']:
            check_stat(score([g], metric), r['regions'][str(g)][metric]); checked_stats += 1
    for i, p in enumerate(r['probes']):
        assert p['id'] == ids[i]
        for metric in ['percentile', 'log2raw']:
            values = [math.log2(arr[i]['raw']) if metric == 'log2raw' else arr[i][metric] for arr in arrays]
            check_stat(values, p[metric]); checked_stats += 1
    intervals = {}
    for name in ['upstream', 'strict_current_CDS']:
        v = score(groups[name], 'percentile')
        rng = np.random.default_rng(20261004)
        # Explicit pairwise comparisons, independent of the pilot's vectorized A.
        boot = [A([float(a) for a in rng.choice(v[:6], 6, replace=True)],
                  [float(b) for b in rng.choice(v[6:23], 17, replace=True)]) for _ in range(2000)]
        ci = np.quantile(boot, [.025, .975]).tolist()
        assert np.allclose(ci, r['summary'][name]['bootstrap_A95'], atol=1e-14, rtol=0)
        intervals[name] = ci
    flag_counts = {k: sum(p[k] for arr in arrays for p in arr) for k in ['mask', 'outlier']}
    assert flag_counts == {'mask': 0, 'outlier': 11}
    independent = json.loads((BASE / 'independent-raw-verification.json').read_text())
    assert independent['artifact_sha256'] == sha(BASE / 'raw-array-results.json')
    previous = {}
    for folder, manifest in [('discovery-2026-10-03', 'MANIFEST-CURRENT.json'),
                             ('tmem266-tissue-2026-10-03', 'MANIFEST.json')]:
        p = BASE.parent / folder
        saved = json.loads((p / manifest).read_text())
        for name, entry in saved['files'].items():
            f = p / name
            assert f.stat().st_size == entry['bytes'] and sha(f) == entry['sha256'], str(f)
        previous[folder] = {'files_verified': len(saved['files']), 'manifest_sha256': sha(p / manifest)}
    syntax = []
    for p in BASE.glob('*.py'):
        compile(p.read_text(encoding='utf-8-sig'), str(p), 'exec')
        syntax.append(p.name)
    links = 0
    for name in ['DRAFT.md', 'SUPPLEMENT.md']:
        s = (BASE / name).read_text(encoding='utf8')
        for target in re.findall(r'\]\(([^)]+)\)', s):
            if target.startswith(('https:', 'http:', '#')):
                continue
            assert (BASE / target).exists(), (name, target)
            links += 1
    out = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'status': 'pass',
           'raw_arrays': 25, 'target_values': 750, 'statistic_blocks_recomputed': checked_stats,
           'bootstrap_intervals_recomputed': intervals, 'target_flags': flag_counts,
           'previous_packets_unchanged': previous, 'python_syntax_checked': syntax,
           'local_manuscript_links_verified': links, 'network_bytes': 0,
           'limitations': 'Offline selected-output arithmetic is distinct from independent raw-CEL verification and biological validation',
           'draft_sha256': sha(BASE / 'DRAFT.md'), 'supplement_sha256': sha(BASE / 'SUPPLEMENT.md')}
    (BASE / 'verification.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out))


if __name__ == '__main__':
    main()
