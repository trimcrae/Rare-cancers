"""Read-only peer diagnostics of a fixed ligand panel; no new gene selection."""
import csv
import datetime
import gzip
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np
from scipy.stats import mannwhitneyu, t

OUT = Path(__file__).resolve().parent
WORKER_LANE = Path('/workspace/emc-r6-single_cell/research/autonomy/fresh-discovery-2026-10-05-round8/microenvironment')
LANE = WORKER_LANE if WORKER_LANE.exists() else OUT.parents[1]/'microenvironment'
REPO = OUT.parents[4]
EMC = 'Extraskeletal myxoid chondrosarcoma'
H = json.loads((LANE / 'HOFVANDER-FIXED-CONTRAST.json').read_text())
A = json.loads((LANE / 'GSE24369-FIXED-CONTRAST.json').read_text())
RB = json.loads((LANE / 'DECISIVE-ROBUSTNESS-RESULTS.json').read_text())


def binding(p):
    return {'path': str(p), 'bytes': p.stat().st_size,
            'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}


def source_path(recorded):
    p = Path(recorded)
    if p.exists():
        return p
    return REPO/str(p).split('/Rare-cancers/', 1)[1]


# Replay directly from the shared source, preserving actual measured zeros.
source = source_path(H['inputs'][0]['path'])
assert hashlib.sha256(source.read_bytes()).hexdigest() == H['inputs'][0]['sha256']
data = {}
genes = set(H['all704_gene_observations'][0]['genes_TPM'])
with gzip.open(source, 'rt') as handle:
    rows = csv.reader(handle, delimiter='\t')
    samples = next(rows)[1:]
    for row in rows:
        if row[0] in genes:
            assert row[0] not in data
            data[row[0]] = list(map(float, row[1:]))
assert set(data) == genes
source_rows = {r['sample']: r for r in H['all704_gene_observations']}
assert len(source_rows) == len(samples) == 704
for j, sample in enumerate(samples):
    r = source_rows[sample]
    for gene in genes:
        assert data[gene][j] == r['genes_TPM'][gene]
    scores = {k: np.mean([np.log2(r['genes_TPM'][g]+1) for g in panel])
              for k, panel in H['panels'].items()}
    assert all(abs(scores[k]-r['scores_log2_TPMplus1'][k]) < 1e-12 for k in scores)
    assert abs(scores['myeloid_ligand']-scores['T_ligand']-r['myeloid_minus_T_ligand_score']) < 1e-12

array_source = source_path(A['source'])
assert hashlib.sha256(array_source.read_bytes()).hexdigest() == A['sha256']
probe_genes = {pr: gene for gene, prs in A['gene_probe_mapping'].items() for pr in prs}
annotated = {g: set() for g in genes}
observed = {}
sample = None
intable = False
inplatform = False
with gzip.open(array_source, 'rt') as handle:
    for line in handle:
        line = line.rstrip('\n')
        if line.startswith('!platform_table_begin'):
            inplatform = True
            platform_header = next(handle).strip().split('\t')
        elif line.startswith('!platform_table_end'):
            inplatform = False
        elif inplatform:
            r = dict(zip(platform_header, line.split('\t')))
            symbols = {item.split(' // ')[1] for item in r['gene_assignment'].split(' /// ')
                       if len(item.split(' // ')) >= 2}
            if len(symbols) == 1 and next(iter(symbols)) in genes:
                annotated[next(iter(symbols))].add(r['ID'])
        elif line.startswith('^SAMPLE = '):
            sample = line.split(' = ', 1)[1]
            observed[sample] = {}
        elif line.startswith('!sample_table_begin'):
            intable = True
            next(handle)
        elif line.startswith('!sample_table_end'):
            intable = False
        elif intable:
            parts = line.split('\t')
            if parts[0] in set.union(*annotated.values()):
                observed[sample][parts[0]] = float(parts[1])
assert len(observed) == len(A['all42source_observations']) == 42
common_probes = set.intersection(*(set(r) for r in observed.values()))
independent_mapping = {g: sorted(prs & common_probes) for g, prs in annotated.items()}
assert independent_mapping == {g: sorted(prs) for g, prs in A['gene_probe_mapping'].items()}
for r in A['all42source_observations']:
    for gene, prs in A['gene_probe_mapping'].items():
        assert np.mean([observed[r['accession']][pr] for pr in prs]) == r['genes_published_log2_array'][gene]


def diagnostic(rows, is_emc, balance, scores, covariates):
    X = np.array([[1, int(is_emc(r))]+[scores(r)[k] for k in covariates] for r in rows])
    y = np.array([balance(r) for r in rows])
    coef = np.linalg.lstsq(X, y, rcond=None)[0]
    residual = y-X@coef
    rank = np.linalg.matrix_rank(X)
    df = len(y)-rank
    se = np.sqrt((residual@residual/df)*np.linalg.pinv(X.T@X)[1, 1])
    interval = t.ppf(.975, df)*se
    return {'N': len(rows), 'EMC': sum(is_emc(r) for r in rows),
            'fixed_covariates': covariates, 'EMC_coefficient': float(coef[1]),
            'OLS_t95CI_descriptive': [float(coef[1]-interval), float(coef[1]+interval)],
            'design_rank': int(rank), 'condition_number': float(np.linalg.cond(X)),
            'interpretation': 'Post-result diagnostic, conditional association; no recruitment or cell-source inference.'}


def all_diagnostics(rows, is_emc, balance, scores, content):
    result = []
    for n in range(4):
        for subset in itertools.combinations(content, n):
            result.append(diagnostic(rows, is_emc, balance, scores, list(subset)))
    return result


hrows = [r for r in H['all704_gene_observations'] if r['diagnosis'] == EMC or r['diagnosis'] in H['comparators']]
assert len(hrows) == 59 and len({r['patient_group'] for r in hrows}) == 59
h_emc = lambda r: r['diagnosis'] == EMC
h_y = lambda r: r['myeloid_minus_T_ligand_score']
h_s = lambda r: r['scores_log2_TPMplus1']
h_content = ['leukocyte', 'myeloid_content', 'T_content']
hmodels = all_diagnostics(hrows, h_emc, h_y, h_s, h_content)
assert abs(hmodels[-1]['EMC_coefficient']-RB['Hofvander']['fixed_content_adjusted_EMC_coefficient']) < 1e-12
arows = [r for r in A['all42source_observations'] if r['tissue'] in [EMC, 'Low-grade fibromyxoid sarcoma']]
assert len(arows) == 23
a_emc = lambda r: r['tissue'] == EMC
a_y = lambda r: r['balance']
a_s = lambda r: r['scores']
a_content = ['leukocyte', 'myeloid_content', 'T_cell_content']
amodels = all_diagnostics(arows, a_emc, a_y, a_s, a_content)
assert abs(amodels[-1]['EMC_coefficient']-RB['GSE24369']['fixed_content_adjusted_EMC_coefficient']) < 1e-12

nonoverlap = [r for r in hrows if not h_emc(r) or (not r['specimen_exception'] and not r['known_overlap'])]
lgfms = [r for r in hrows if h_emc(r) or r['diagnosis'] == 'Low-grade fibromyxoid sarcoma']
sensitivity = {'Hofvander_nonoverlapping_primary9': diagnostic(nonoverlap, h_emc, h_y, h_s, h_content),
               'Hofvander_EMC_vs_LGFMS_only': diagnostic(lgfms, h_emc, h_y, h_s, h_content)}
parts = {'Hofvander': {}, 'GSE24369': {}}
for cohort, rows, flag, score, content, panels in [
    ('Hofvander', hrows, h_emc, h_s, h_content, ['myeloid_ligand', 'T_ligand']),
    ('GSE24369', arows, a_emc, a_s, a_content, ['myeloid_recruitment', 'T_cell_recruitment'])]:
    for panel in panels:
        parts[cohort][panel] = diagnostic(rows, flag, lambda r, p=panel: score(r)[p], score, content)
out = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
       'question': 'Independent fixed-score and source replay plus content-adjustment dependence.',
       'source_replay': {'Hofvander_704x13_gene_values': True, 'array_42x13_released_probe_values': True,
                         'array_unique_original_GPL6244_and_common_probe_mapping': True,
                         'all13_EMC_and46_unique_comparator_donors': True, 'array_six_EMC_vs17_LGFMS': True},
       'Hofvander_fixed_covariate_models': hmodels, 'GSE24369_fixed_covariate_models': amodels,
       'Hofvander_fixed_sensitivities': sensitivity, 'fixed_ligand_score_decomposition': parts,
       'caution': 'All diagnostics are declared after initial results. Model variants are not additional discoveries or independent validation. RNA and array cohort donor overlap is unresolved. Source values are transcripts, not immune recruitment or cell fractions.',
       'bindings': [binding(p) for p in [LANE/'PLAN.json', LANE/'AMENDMENT-01-COMPARATOR-FREEZE.json',
                    LANE/'AMENDMENT-02-DECISIVE-VALUE-CHECK.json', LANE/'AMENDMENT-03-COMPLETE-TEMPO-STAGE.json',
                    LANE/'HOFVANDER-FIXED-CONTRAST.json', LANE/'GSE24369-FIXED-CONTRAST.json',
                    LANE/'DECISIVE-ROBUSTNESS-RESULTS.json', source, array_source]]}
(OUT/'FIXED-COHORT-DIAGNOSTICS.json').write_text(json.dumps(out, indent=2, allow_nan=False)+'\n')
print(json.dumps({'Hofvander_models': [r['EMC_coefficient'] for r in hmodels],
                  'array_models': [r['EMC_coefficient'] for r in amodels],
                  'sensitivities': sensitivity}, indent=2))
