"""Frozen descriptive follow-up; cloud execution only. Requires pandas/numpy."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import threading
import urllib.request

import numpy as np
import pandas as pd

REVISION = 'da49c4e836533253825587f83656675dac4c913b'
MATCHED_SHA = '46deef9526068591a76c62bda6c20fa26ca95969f666769850eb626306f63f24'
MATRIX_SHA = '5e7adf7e8217e5a02389c299dce1266e74c7a3b786b8c177e56d12402fe783ac'
MATRIX_BYTES = 94222540
URL = 'https://ndownloader.figshare.com/files/34411172'
GENES = {'CSPG4': 'Q6UVK1', 'L1CAM': 'P32004'}
EXPECTED = {'CSPG4': {'original': (33, 0.6657754010695187), 'added': (18, -0.30443756449948395)},
            'L1CAM': {'original': (29, 0.669950738916256), 'added': (17, -0.482843137254902)}}

def verify(path, digest, size):
    if path.stat().st_size != size:
        raise ValueError('Input byte count mismatch: ' + str(path))
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    if h.hexdigest() != digest:
        raise ValueError('Input SHA256 mismatch: ' + str(path))

def matrix_file(path):
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        if shutil.disk_usage(path.parent).free < 10 * 1024**3 + MATRIX_BYTES * 2:
            raise ValueError('Insufficient cloud disk headroom')
        part = path.with_name(path.name + '.part')
        try:
            req = urllib.request.Request(URL, headers={'User-Agent': 'EMC-frozen-lineage-followup/1'})
            n = 0
            with urllib.request.urlopen(req, timeout=30) as response, part.open('xb') as out:
                while True:
                    block = response.read(1024 * 1024)
                    if not block:
                        break
                    n += len(block)
                    if n > MATRIX_BYTES:
                        raise ValueError('Matrix download exceeded frozen byte cap')
                    out.write(block)
            verify(part, MATRIX_SHA, MATRIX_BYTES)
            part.replace(path)
        except Exception:
            part.unlink(missing_ok=True)
            raise
    verify(path, MATRIX_SHA, MATRIX_BYTES)
    return path

def describe(x, y):
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    if len(x) != len(y) or not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError('Expected finite paired measurements')
    result = {'n': len(x), 'distinctRNA': len(set(x)), 'distinctProtein': len(set(y)), 'rho': None}
    if len(x) < 3:
        result['undefinedReason'] = 'fewer_than_three_pairs'
    elif np.std(x, ddof=1) < 1e-12 or np.std(y, ddof=1) < 1e-12:
        result['undefinedReason'] = 'constant_or_near_constant_measurement'
    else:
        rx, ry = pd.Series(x).rank().to_numpy(), pd.Series(y).rank().to_numpy()
        result['rho'] = float(np.corrcoef(rx, ry)[0, 1])
    return result

def decompose(x, y, labels):
    result = describe(x, y)
    if len(labels) != len(x):
        raise ValueError('Stratum length mismatch')
    if result['rho'] is None:
        return dict(result, withinComponent=None, betweenComponent=None, strata=[])
    rx, ry = pd.Series(x).rank().to_numpy(), pd.Series(y).rank().to_numpy()
    mx, my = rx.mean(), ry.mean()
    scale = math.sqrt(float(np.mean((rx-mx)**2) * np.mean((ry-my)**2)))
    within = between = 0.0
    strata = []
    labels = np.asarray(labels)
    for label in sorted(set(labels)):
        a, b = rx[labels == label], ry[labels == label]
        weight = len(a) / len(rx)
        w = weight * float(np.mean((a-a.mean())*(b-b.mean()))) / scale
        t = weight * float((a.mean()-mx)*(b.mean()-my)) / scale
        within += w
        between += t
        strata.append({'histology': str(label), 'n': len(a), 'weight': weight,
                       'meanGlobalRankRNA': float(a.mean()), 'meanGlobalRankProtein': float(b.mean()),
                       'withinContribution': w, 'betweenContribution': t})
    error = within + between - result['rho']
    if abs(error) > 1e-12:
        raise ValueError('Covariance component identity failed')
    return dict(result, withinComponent=within, betweenComponent=between, sumError=error, strata=strata)

def clean(value):
    if isinstance(value, dict): return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, list): return [clean(v) for v in value]
    if isinstance(value, (np.integer,)): return int(value)
    if isinstance(value, (float, np.floating)): return float(value) if math.isfinite(value) else None
    if isinstance(value, np.bool_): return bool(value)
    return value

def run(args):
    verify(args.matched, MATCHED_SHA, 2926326)
    published = json.loads(args.matched.read_text(encoding='utf-8'))
    d = published['result']
    if d['schema'] != 'frozen-sarcoma-matched-measurements/1' or published['execution']['run_id'] != 36896523203:
        raise ValueError('Frozen matched schema/run mismatch')
    def frame(records, index):
        df = pd.DataFrame(records).set_index(index)
        df.index = df.index.astype(str)
        if not df.index.is_unique: raise ValueError('Duplicate matched identifiers')
        return df
    meta, rna, original = frame(d['metadata'], 'model_id'), frame(d['rna'], 'index'), frame(d['protein'], 'index')
    if (len(meta), int(meta.primarySarcomaTest.sum()), int(meta.isTraining.sum())) != (786, 61, 717):
        raise ValueError('Frozen cohort mismatch')
    primary = meta[meta.primarySarcomaTest]
    if primary.relatedGroup.nunique() != 61 or primary[['relatedGroup', 'Cancer_type']].isna().any().any():
        raise ValueError('Primary family/lineage identity mismatch')
    histologies = sorted(primary.Cancer_type.unique())
    if len(histologies) != 6: raise ValueError('Expected six histologies')
    path = matrix_file(args.matrix)
    raw = pd.read_csv(path, sep='\t', index_col=0)
    if sum(str(x).startswith('SIDM') for x in raw.index) < sum(str(x).startswith('SIDM') for x in raw.columns):
        raw = raw.T
    raw.index = [str(x).split(';')[0] for x in raw.index]
    mapping = {g: [c for c in raw.columns if a in re.split(r'[;|]', str(c))] for g, a in GENES.items()}
    if any(not cols for cols in mapping.values()): raise ValueError('Missing accession mapping')
    # Columnwise duplicate-model means precede accession means, exactly as the producer.
    selected = list(dict.fromkeys(c for cols in mapping.values() for c in cols))
    raw = raw[selected].apply(pd.to_numeric, errors='coerce').groupby(level=0).mean()
    less = pd.DataFrame({g: raw[cols].mean(axis=1) for g, cols in mapping.items()}).reindex(meta.index)
    measurements, cells, decompositions = [], [], []
    for gene in GENES:
        z = pd.DataFrame({'rna': rna[gene], 'protein6692': original[gene], 'protein8498': less[gene]}).join(meta[['relatedGroup', 'Cancer_type', 'primarySarcomaTest']])
        z = z[z.primarySarcomaTest].groupby(['relatedGroup', 'Cancer_type'], as_index=False).mean(numeric_only=True)
        if len(z) != 61: raise ValueError('Family aggregation changed cohort')
        z['gene'] = gene
        z['support'] = np.where(z.protein6692.notna(), 'original', 'added')
        z['rnaAvailable'] = z.rna.notna()
        z['protein6692Available'] = z.protein6692.notna()
        z['protein8498Available'] = z.protein8498.notna()
        z['paired'] = z.rna.notna() & z.protein8498.notna()
        measurements.extend(z.to_dict('records'))
        for support in ('original', 'added'):
            pool = z[(z.support == support) & z.paired]
            observed = describe(pool.rna, pool.protein8498)
            n, rho = EXPECTED[gene][support]
            if observed['n'] != n or observed['rho'] is None or abs(observed['rho']-rho) > 1e-12:
                raise ValueError(f'Accepted aggregate mismatch: {gene}/{support}: {observed}')
            decompositions.append(dict(gene=gene, support=support, **decompose(pool.rna, pool.protein8498, pool.Cancer_type)))
            for hist in histologies:
                all_rows = z[(z.support == support) & (z.Cancer_type == hist)]
                paired = all_rows[all_rows.paired]
                cells.append(dict(gene=gene, histology=hist, support=support,
                    familiesWithSupportStatus=len(all_rows), rnaAvailable=int(all_rows.rnaAvailable.sum()),
                    protein8498Available=int(all_rows.protein8498Available.sum()),
                    **describe(paired.rna, paired.protein8498)))
    if len(cells) != 24 or len(decompositions) != 4: raise ValueError('Incomplete fixed output grid')
    args.out.mkdir(parents=True, exist_ok=False)
    output = {'schema': 'frozen-protein-lineage-followup/1', 'sourceRevision': REVISION,
              'matchedSHA256': MATCHED_SHA, 'matrixSHA256': MATRIX_SHA, 'matrixURL': URL,
              'accessionMapping': mapping, 'primaryModels': primary.reset_index()[['model_id','relatedGroup','Cancer_type']].to_dict('records'),
              'measurements': measurements, 'cells': cells, 'decompositions': decompositions,
              'scope': 'Post hoc descriptive known-cohort follow-up; no fits, P values or causal attribution'}
    target = args.out / 'protein-lineage-results.json'
    target.write_text(json.dumps(clean(output), indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps({'status':'complete', 'cells':len(cells), 'decompositions':len(decompositions),
                      'resultSHA256':hashlib.sha256(target.read_bytes()).hexdigest()}))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--matched', type=Path, required=True)
    parser.add_argument('--matrix', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    # Hard wall-clock bound includes download and parsing; incomplete outputs are not success.
    watchdog = threading.Timer(295, lambda: os._exit(124))
    watchdog.daemon = True
    watchdog.start()
    try: run(args)
    finally: watchdog.cancel()
