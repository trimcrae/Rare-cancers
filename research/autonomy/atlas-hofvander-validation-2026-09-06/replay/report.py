"""Portable reporting adapter derived from frozen summarize.py CSV operations only."""
from pathlib import Path
import csv,json,hashlib
P=None
OUT=None
def writecsv(name,rows):
    with (OUT/name).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def direction(a):return 'undefined' if a is None else 'positive' if a>.5 else 'negative' if a<.5 else 'neutral'
def front(ident,title):return f'''---
id: DOC-{ident}
title: {title}
level: cross-cutting
kind: memo
status: live
canonical_for: []
purpose: Report every prespecified gene and contrary sensitivity from the completed frozen analysis.
scope: Single-cohort tissue RNA prioritization and separate shared-histology array replication.
audience: [autonomous research agents, external reviewers]
date: "2026-09-06"
last_verified: "2026-09-06"
related: [DOC-ATLAS-HOFVANDER-VALIDATION-20260906]
---

'''
def main():
    a=json.loads((P/'results/result.json').read_text());b=json.loads((P/'replication-results/result.json').read_text());panel=[];contrasts=[];sensitivity=[];rep=[];cells=[]
    for g,r in a['genes'].items():
        ints=r['bootstrap_pointwise_conditional_95']['summary'];anchor=b['genes'][g]['contrasts']['Low-grade fibromyxoid sarcoma']
        panel.append({'gene':g,'role':r['role'],'Hof_marginal_A':r['primary']['summary']['marginal'],'Hof_marginal_pointwise_conditional95_low':ints['marginal'][0],'Hof_marginal_pointwise_conditional95_high':ints['marginal'][1],'Hof_matched_A':r['primary']['summary']['matched'],'Hof_matched_pointwise_conditional95_low':ints['matched'][0],'Hof_matched_pointwise_conditional95_high':ints['matched'][1],'array_LGFMS_A':anchor['array']['A'],'Hof_LGFMS_A':anchor['hofvander']['summary']['marginal'],'Hof_LGFMS_matched_A':anchor['hofvander']['summary']['matched'],'allocation_pass':r['allocation_rule'].get('consistent_RNA_rationale','context_not_applied')})
        for group in ['primary','context']:
            for h,v in r[group]['histologies'].items():
                it=r['bootstrap_pointwise_conditional_95'].get(h,{})
                contrasts.append({'gene':g,'role':r['role'],'group':group,'histology':h,'n_emc':v['n_emc'],'n_comparator':v['n_comparator'],'n_matched_emc':v['matched_emc'],'marginal_A':v['marginal'],'marginal_direction':direction(v['marginal']),'matched_A':v['matched'],'matched_direction':direction(v['matched']),'marginal_conditional_interval':json.dumps(it.get('marginal')),'matched_conditional_interval':json.dumps(it.get('matched'))})
                for c in v['cells']:cells.append({'gene':g,'histology':h,**c})
        for kind,ds in r['deletions'].items():
            for d in ds:
                sensitivity.append({'gene':g,'deletion_type':kind,'deleted':d['deleted'],'marginal_A':d['summary']['marginal'],'marginal_direction':direction(d['summary']['marginal']),'matched_A':d['summary']['matched'],'matched_direction':direction(d['summary']['matched'])})
        for h,c in b['genes'][g]['contrasts'].items():
            rr={'gene':g,'gene_role':r['role'],'histology':h,'contrast_role':c['role'],'array_n_emc':c['array']['n_emc'],'array_n_comparator':c['array']['n_comparator'],'array_A':c['array']['A'],'array_direction':c['array']['direction'],'array_EMC_deletion_range':json.dumps(c['array']['deletion_ranges']['EMC']),'array_comparator_deletion_range':json.dumps(c['array']['deletion_ranges']['comparator']),'Hof_A':c['hofvander']['summary']['marginal'],'Hof_direction':direction(c['hofvander']['summary']['marginal']),'Hof_matched_A':c['hofvander']['summary']['matched'],'Hof_matched_direction':direction(c['hofvander']['summary']['matched'])}
            for typ,ds in c['hofvander_deletions'].items():
                for mode in ['marginal','matched']:
                    vs=[d['summary'][mode] for d in ds];vs=[x for x in vs if x is not None];rr[f'Hof_{typ}_{mode}_deletion_range']=json.dumps([min(vs),max(vs)] if vs else None)
            rep.append(rr)
    writecsv('all12-gene-effects.csv',panel);writecsv('all-hofvander-contrasts.csv',contrasts);writecsv('all-primary-deletions.csv',sensitivity);writecsv('all-year-cells.csv',cells);writecsv('all-shared-histology-replication.csv',rep)
    normal=json.loads(normal_path.read_text())
    assert {r['gene'] for r in normal}==set(a['genes'])
    (OUT/'normal-context.json').write_bytes(normal_path.read_bytes())
    (OUT/'report-provenance.json').write_text(json.dumps({'normal_context_path':str(normal_path),'normal_context_sha256':hashlib.sha256(normal_path.read_bytes()).hexdigest(),'purpose':'Presentation-only export of completed JSON; no new scientific computation'},indent=2)+'\n')
if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--run-dir',type=Path,required=True);parser.add_argument('--normal-context',type=Path,required=True);args=parser.parse_args()
    P=args.run_dir;OUT=P/'reports';OUT.mkdir(exist_ok=False);normal_path=args.normal_context;main()
