"""Extract fixed TMEM266/control rows from the retained official API subset.
No raw read retrieval, expression thresholds or differential testing.
"""
import csv, hashlib, io, json, zipfile
from collections import Counter
from pathlib import Path

P = Path(__file__).parent
raw = (P / 'archs4-subset.zip').read_bytes()
assert hashlib.sha256(raw).hexdigest() == 'f0bcd17e0c56ec038ea47ee14b7b57700333b46790d2cfb18a555cbf70ea4446'
with zipfile.ZipFile(io.BytesIO(raw)) as z:
    assert z.namelist() == ['matrix.tsv']
    data = z.read('matrix.tsv')
rows = list(csv.reader(io.StringIO(data.decode()), delimiter='\t'))
samples = rows[0][1:]
assert len(samples) == len(set(samples))
genes = [r[0] for r in rows[1:]]
values = [[int(x) for x in r[1:]] for r in rows[1:]]
assert all(len(v) == len(samples) and min(v) >= 0 for v in values)
target = {'TMEM266', 'C15orf27', 'C15ORF27', 'ENSG00000169758', 'NR4A3', 'CHRNA6', 'ACTB', 'GAPDH'}
sums = [sum(v[j] for v in values) for j in range(len(samples))]
selected = []
for i, gene in enumerate(genes):
    if gene.split('.')[0] in target:
        selected.append({'row_index1': i+2, 'gene': gene, 'counts': dict(zip(samples, values[i])),
                         'CPM_of_reported_counts': {s: 1e6*values[i][j]/sums[j] for j,s in enumerate(samples)}})
out = {
    'source': {'api': 'https://maayanlab.cloud/sigpy/data/samples',
               'documentation': 'https://archs4.org/help',
               'archive_bytes': len(raw), 'archive_sha256': hashlib.sha256(raw).hexdigest(),
               'matrix_bytes': len(data), 'matrix_sha256': hashlib.sha256(data).hexdigest(),
               'service_last_update': '09/30/2026',
               'release_caveat': 'API archive has no per-file HDF5 release identifier; service update is not a pinned database version'},
    'requested_GSMs': ['GSM2113301','GSM6883080','GSM9037837'],
    'returned_GSMs': samples,
    'missing_GSMs_not_zeros': sorted(set(['GSM2113301','GSM6883080','GSM9037837'])-set(samples)),
    'gene_rows': len(genes),
    'duplicate_gene_symbols': {g:n for g,n in Counter(genes).items() if n>1},
    'column_sums': dict(zip(samples,sums)),
    'nonzero_rows': {s:sum(v[j]>0 for v in values) for j,s in enumerate(samples)},
    'selected_rows': selected,
    'units': 'ARCHS4 rounded estimated gene counts (Kallisto pseudocounts); derived CPM uses sum over every returned row, not TPM',
    'units_documentation': 'https://archs4.org/download',
    'limitations': 'One library per source culture; V1-34 technical runs may be aggregated by ARCHS4. Counts are not original GEO quantification, independently collected samples, protein or dependency.'
}
(P/'archs4-results.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['returned_GSMs','missing_GSMs_not_zeros','gene_rows','column_sums','selected_rows']},indent=2))
