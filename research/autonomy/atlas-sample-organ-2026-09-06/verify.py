"""Independent Fraction arithmetic and source mapping checks; no analysis-module import."""
from pathlib import Path
from fractions import Fraction as F
import csv,gzip,json,re,hashlib
P=Path(__file__).resolve().parent

def median(x):
    a=sorted(x); n=len(a)
    return (a[(n-1)//2]+a[n//2])/2 if n else None

def main():
    d=json.loads((P/'results.json').read_text()); m=json.loads((P/'column-mapping.json').read_text())
    with gzip.open(P/'GSE28866_36048_normalized_peaks_cancer_and_normal.txt.gz','rt') as f: original=list(csv.DictReader(f,delimiter='\t'))
    with (P/'selected-source-rows.tsv').open() as f: selected=list(csv.DictReader(f,delimiter='\t'))
    source={r['peak']:r for r in original}
    assert all(source[r['peak']]==r for r in selected)
    expected=[]
    for row in original:
        toks=set(re.findall(r'[^,;|/\s]+',row['gene_symbol']+' '+row['peak_exon_gene_symbol']))
        for g in d['panel']:
            if g in toks: expected.append((g,row['peak'],toks=={g}))
    assert sorted(expected)==sorted((r['gene'],r['peak'],r['mapping']['strict_mapping']) for r in d['peaks'])
    assert {r['peak'] for r in selected}=={p for g,p,s in expected}
    checks=0
    for r in d['peaks']:
        raw=source[r['peak']]
        units={u:sum(F(raw[h]) for h in hs)/len(hs) for u,hs in m['units'].items()}
        assert {u:F(v) for u,v in r['unit_values'].items()}==units
        e=[units[u] for u in m['emc_units']]
        for c in r['contrasts']:
            vals=[units[u] for u in m['strata'][c['stratum']]]
            assert F(c['delta'])==median(e)-median(vals)
            assert F(c['comparator_median'])==median(vals)
            assert F(c['minimum_emc_minus_maximum_comparator'])==min(e)-max(vals)
            assert all(F(c['individual_emc_deltas'][u])==units[u]-median(vals) for u in m['emc_units'])
            assert c['coverage_complete'] and c['n_emc_available']==4 and c['n_comparator_available']==len(vals)
            checks+=1
        for s in r['sensitivity']:
            ee=[units[u] for u in m['emc_units'] if not (s['family']=='leave_one_EMC_out' and u==s['deleted'])]
            uu=m['strata']['sarcoma:pooled']
            if s['family']=='leave_one_histology_out': uu=[u for u in uu if u not in m['strata']['sarcoma:'+s['deleted']]]
            assert F(s['delta'])==median(ee)-median([units[u] for u in uu]);checks+=1
    assert not d['missing_cells']
    assert len(m['columns'])==93 and len(m['units'])==91 and len(m['strata']['sarcoma:pooled'])==30
    report={'status':'passed','source_rows_compared':len(selected),'gene_peak_assignments_checked':len(expected),'exact_fraction_contrasts_and_sensitivities_checked':checks,'checks':['Selected source cells identical to archived gzip','Independent regex symbol mapping covers all selected genes and peaks','All technical means recomputed with Fraction','All contrasts, per-EMC differences and extrema recomputed with Fraction','All leave-one sensitivities independently recomputed','93 libraries / 91 STT analysis units / 30 comparator STT units','Selected cells complete; all coverage flags verified'],'limits':'These checks validate arithmetic and extraction, not gene annotation truth or independent patients.'}
    (P/'checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
