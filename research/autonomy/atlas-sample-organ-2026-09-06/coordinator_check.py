"""Independent source/header/stratum reconstruction; no worker-module import."""
import csv
import gzip
import hashlib
import json
import re
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from statistics import median

P = Path(__file__).resolve().parent
panel = ['CHRNA6','CD276','SSTR2','PRAME','FAP','CD248','CSPG4','MSLN','L1CAM','GPC3','ALPP','CDH17']
raw = P/'GSE28866_36048_normalized_peaks_cancer_and_normal.txt.gz'
assert hashlib.sha256(raw.read_bytes()).hexdigest() == '11dae64b2d6b6e77846c3f14971fc9a313da86eb52a4b8b83df96c23eedc0ffd'
with gzip.open(raw, 'rt') as f:
    reader = csv.DictReader(f, delimiter='\t')
    headers = reader.fieldnames[7:]
    rows = list(reader)
assert len(headers) == 93 and len(rows) == 36048
units = defaultdict(list)
for h in headers:
    # Only these two primary-documented pairs are collapsed.
    u = re.sub(r'_rep[12]$', '', h) if h in {
        'ESS_STT5520_rep1','ESS_STT5520_rep2','LMS_STT516_rep1','LMS_STT516_rep2'
    } else h
    units[u].append(h)
strata = defaultdict(list)
emc = []
sarcomas = {'ESS','EWS','GIST','LMS','MLPS','DDLPS','SS'}
for u in units:
    hist = u.split('_')[0]
    if hist == 'EMC':
        emc.append(u)
    if hist in sarcomas:
        strata['sarcoma:'+hist].append(u)
        strata['sarcoma:pooled'].append(u)
    m = re.fullmatch(r'STT\d+_(Adult|Fetal)_normal_(\w+)', u)
    if m:
        stage, organ = m[1].lower(), m[2]
        strata[stage+':'+organ].append(u)
        strata[stage+':pooled'].append(u)
        strata['normal:adult_fetal_pooled'].append(u)
mapping = json.loads((P/'column-mapping.json').read_text())
assert dict(units) == mapping['units']
assert set(emc) == set(mapping['emc_units'])
assert {k:set(v) for k,v in strata.items()} == {k:set(v) for k,v in mapping['strata'].items()}
result = json.loads((P/'results.json').read_text())
assert result['panel'] == panel
expected = {}
for r in rows:
    symbols = set(re.split(r'[,;|/\s]+', r['gene_symbol']+' '+r['peak_exon_gene_symbol'])) - {''}
    for g in panel:
        if g in symbols:
            expected[(g,r['peak'])] = (r,symbols == {g})
assert set(expected) == {(r['gene'],r['peak']) for r in result['peaks']}
n = 0
for peak in result['peaks']:
    row, strict = expected[(peak['gene'],peak['peak'])]
    assert strict == peak['mapping']['strict_mapping']
    values = {u:sum(Fraction(row[h]) for h in hs)/len(hs) for u,hs in units.items()}
    ev = [values[u] for u in emc]
    for c in peak['contrasts']:
        cv = [values[u] for u in strata[c['stratum']]]
        assert Fraction(c['delta']) == median(ev)-median(cv)
        assert Fraction(c['minimum_emc_minus_maximum_comparator']) == min(ev)-max(cv)
        assert {u:Fraction(v) for u,v in c['individual_emc_deltas'].items()} == {u:values[u]-median(cv) for u in emc}
        assert c['coverage_complete'] and c['n_emc_available']==4 and c['n_comparator_available']==len(cv)
        n += 1
    for s in peak['sensitivity']:
        kept_e = [u for u in emc if not (s['family']=='leave_one_EMC_out' and u==s['deleted'])]
        kept_c = [u for u in strata['sarcoma:pooled'] if not (s['family']=='leave_one_histology_out' and u.split('_')[0]==s['deleted'])]
        assert Fraction(s['delta']) == median([values[u] for u in kept_e])-median([values[u] for u in kept_c])
        n += 1
receipt = {'status':'passed','source_rows':len(rows),'source_headers':len(headers),'independently_reconstructed_units':len(units),'independently_reconstructed_strata':{k:len(v) for k,v in strata.items()},'gene_peak_assignments':len(expected),'exact_contrasts_and_sensitivities':n,'scope':'Root independently reconstructed source-header units/strata and checked exact Fraction arithmetic; no worker module imported. Does not validate annotation biology or patient independence.'}
(P/'coordinator-check.json').write_bytes((json.dumps(receipt,indent=2)+'\n').encode())
print(json.dumps(receipt))
