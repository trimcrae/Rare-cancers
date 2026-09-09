import json
d=json.load(open('research/modalities/emc-expression-panels.json'))
gr=d['gene_reads']
S={'GPL6244':'GSE24369_series_matrix.txt.gz','GPL3290':'GSE4303-GPL3290_series_matrix.txt.gz'}
for g in ['BCL2','MCL1','BCL2L1','BCL2L2','BCL2A1']:
    for lab,s in S.items():
        r=gr[g][s]
        t=r.get('t') or (r.get('score') or {}).get('t')
        print(f"{g:<8} {lab:<8} delta={r['EMC']['mean_z']-r['comparator']['mean_z']:+.4f} t={t} verdict={r.get('verdict','')[:130]}")
