#!/usr/bin/env python3
"""Complete original GSE24369 fixed-gene extraction, source GPL6244 mapping."""
from pathlib import Path
import gzip, json, re, hashlib, datetime
import numpy as np
from scipy.stats import mannwhitneyu

P=Path(__file__).parent
SRC=Path('/workspace/Rare-cancers/research/autonomy/atlas-primary-provenance-2026-09-06/GSE24369.soft.gz')
PANELS=json.loads((P/'PLAN.json').read_text())['fixed_panels']
WANTED=set(sum(PANELS.values(),[]))
mapping={g:[] for g in WANTED}; annotation=[];samples={};current=None; inplatform=False; intable=False
with gzip.open(SRC,'rt') as h:
    for line in h:
        line=line.rstrip('\n')
        if line.startswith('!platform_table_begin'):
            inplatform=True;header=h.readline().strip().split('\t');continue
        if line.startswith('!platform_table_end'):inplatform=False;continue
        if inplatform:
            cells=line.split('\t');row=dict(zip(header,cells));assign=row['gene_assignment'];symbols=set()
            for a in assign.split(' /// '):
                parts=a.split(' // ')
                if len(parts)>=2:symbols.add(parts[1])
            for g in WANTED&symbols:
                annotation.append({'probe':row['ID'],'symbol':g,'source_gene_assignment':assign,'unique_symbol':symbols=={g}})
                if symbols=={g}:mapping[g].append(row['ID'])
            continue
        if line.startswith('^SAMPLE'):
            current=line.split(' = ')[1];samples[current]={'accession':current,'values':{}};continue
        if current is not None and line.startswith(('!Sample_title','!Sample_source_name_ch1','!Sample_characteristics_ch1','!Sample_platform_id')):
            key,value=line.split(' = ',1);samples[current].setdefault(key,[]).append(value)
        if line.startswith('!sample_table_begin'):intable=True;h.readline();continue
        if line.startswith('!sample_table_end'):intable=False;continue
        if intable:
            probe,value=line.split('\t')[:2]
            if probe in {p for ps in mapping.values() for p in ps}:samples[current]['values'][probe]=float(value)
assert len(samples)==42
assert all(mapping.values()), [g for g,ps in mapping.items() if not ps]
common=set.intersection(*(set(s['values']) for s in samples.values()))
unmeasured={g:[pr for pr in ps if pr not in common] for g,ps in mapping.items()}
mapping={g:[pr for pr in ps if pr in common] for g,ps in mapping.items()}
assert all(mapping.values()), ('No common released probe for fixed genes',mapping,unmeasured)
rows=[]
for accession,s in samples.items():
    genes={g:float(np.mean([s['values'][pr] for pr in mapping[g]])) for g in WANTED}
    scores={k:float(np.mean([genes[g] for g in panel])) for k,panel in PANELS.items()}
    balance=scores['myeloid_recruitment']-scores['T_cell_recruitment']
    tissue=[x.split(': ',1)[1] for x in s['!Sample_characteristics_ch1'] if x.startswith('tissue: ')][0]
    rows.append({'accession':accession,'title':s['!Sample_title'][0],'source_characteristics':s['!Sample_characteristics_ch1'],
                 'tissue':tissue,'genes_published_log2_array':genes,'scores':scores,'balance':balance})
emc=[r for r in rows if r['tissue']=='Extraskeletal myxoid chondrosarcoma']
lg=[r for r in rows if r['tissue']=='Low-grade fibromyxoid sarcoma'];assert len(emc)==6 and len(lg)==17
def effect(rs):
    a=[r['balance'] for r in emc];b=[r['balance'] for r in rs];u=mannwhitneyu(a,b,alternative='two-sided',method='auto')
    return {'n_EMC':len(a),'n_comparator':len(b),'median_EMC':float(np.median(a)),'median_comparator':float(np.median(b)),
            'median_difference':float(np.median(a)-np.median(b)), 'probability_EMC_gt_comparator':float(u.statistic/(len(a)*len(b))),
            'two_sided_MWU_p_exploratory':float(u.pvalue)}
contrasts={'fixed_LGFMS':effect(lg)}
for t in sorted({r['tissue'] for r in rows if r not in emc and r['tissue']!='Low-grade fibromyxoid sarcoma'}):
    contrasts['context_'+t]=effect([r for r in rows if r['tissue']==t])
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
     'source':str(SRC),'bytes':SRC.stat().st_size,'sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),
     'units':'Original sample_table VALUE; alreadylog2normalizedarray intensity, notTPM/TempOCPM; no absolute crossplatformpooling',
     'probe_rule':'All unique-original-GPLgene-symbol probes, averaged within gene; ambiguousmulti-symbol annotations excluded before inspecting values.',
     'gene_probe_mapping':mapping,'annotated_but_unmeasured_probes':unmeasured,
     'measurement_rule':'Use only unambiguouslymapped probe IDs present in all42released samples; excluded annotation-only IDs selected by availability, never expression value.',
     'original_annotation_rows':annotation,'all42source_observations':rows,'contrasts':contrasts,
     'missing_primary_comparator_histologies':['Myxoid liposarcoma','Synovial sarcoma'],
     'independence':'SixsourceEMC observations; patientcodecrosswalk withHofvander/otherarrays unresolved, no pooling. Skeletalmuscle entries are pooledRNA references, not2independent normaldonors.'}
(P/'GSE24369-FIXED-CONTRAST.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'probes':mapping,'contrasts':contrasts},indent=2))
