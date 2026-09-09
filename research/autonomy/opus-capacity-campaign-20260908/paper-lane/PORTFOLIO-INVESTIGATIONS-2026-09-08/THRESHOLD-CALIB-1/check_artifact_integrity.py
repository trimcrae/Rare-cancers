#!/usr/bin/env python3
"""Artifact integrity: the missing-call set is exact, on-panel, HLA-C-free, 8-11mers, and no
discrimination is reported anywhere. Provenance hashes are re-verified against the inputs in place."""
import json, hashlib, sys
REPO = '/home/user/Rare-cancers/'
d = json.load(open('threshold-calibration.json'))
m = d['missing_predictor_call_set']
F, N = m['arm_F_pairs'], m['arm_N_pairs']
ok = True
def chk(name, cond):
    global ok
    print(f"{'PASS' if cond else 'FAIL'}  {name}"); ok = ok and bool(cond)
chk("arm F count matches list", len(F) == m['arm_F_fusion_junction_calls_required'] == 652)
chk("arm N count matches list", len(N) == m['arm_N_nonfusion_calls_required'] == 473)
chk("total is the sum", m['total_calls_required'] == len(F) + len(N) == 1125)
allp = F + N
panel = set(json.load(open(REPO + 'research/modalities/epitope-allele-matrix-mhcnuggets.json'))['panel'])
chk("every allele is on the 34-allele panel", all(x['allele'] in panel for x in allp))
chk("no HLA-C anywhere", not any(x['allele'].startswith('HLA-C') for x in allp))
chk("every peptide is 8-11mer", all(8 <= len(x['peptide']) <= 11 for x in allp))
chk("peptides are plain uppercase residues", all(x['peptide'].isalpha() and x['peptide'].isupper() for x in allp))
chk("pairs unique", len({(x['peptide'], x['allele']) for x in allp}) == len(allp))
chk("no measured discrimination is reported",
    d['measured_discrimination']['auroc'] is None and d['verdict']['discrimination_measured'] is False)
chk("all instrument checks passed", d['checks']['all_passed'] is True)
chk("intersection is zero in both arms",
    all(v['peptide_allele_pairs_in_common'] == 0 and v['peptides_in_common'] == 0
        for v in d['intersection'].values()))
for k, v in d['provenance'].items():
    h = hashlib.sha256(open(REPO + v['path'], 'rb').read()).hexdigest()
    chk(f"provenance hash still current: {k}", h == v['sha256'])
print("ALL PASSED" if ok else "SOME FAILED")
sys.exit(0 if ok else 1)
