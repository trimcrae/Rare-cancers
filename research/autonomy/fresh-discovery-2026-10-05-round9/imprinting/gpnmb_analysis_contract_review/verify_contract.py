#!/usr/bin/env python3
"""Independent replay of frozen source bindings and metadata; no expression reads."""
import pathlib,json,hashlib,collections,datetime,shutil
P=pathlib.Path(__file__).resolve().parent
hashof=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
checks=[]
def check(label,ok,detail=None):
 checks.append({'check':label,'pass':bool(ok),'detail':detail})
 assert ok,label
bound=json.loads((P/'EXACT-INPUT-BINDINGS.json').read_text()); roots={x['role']:pathlib.Path(x['root']) for x in bound}
for stage in bound:
 check(stage['role']+':freeze hash',hashof(stage['freeze_path'])==stage['freeze_sha256'])
 for x in stage['bindings']:
  check(stage['role']+':'+pathlib.Path(x['path']).name,hashof(x['path'])==x['sha256'] and pathlib.Path(x['path']).stat().st_size==x['bytes'])
C=json.loads((roots['contract']/'CONTRACT-FROZEN.json').read_text())
check('exact prospectively frozen contract',hashof(roots['contract']/'CONTRACT-FROZEN.json')=='e2709d933df37d3f053978c7714dd6424ef94de7f844ed2970ad21cfc4019434')
check('exact MLPS source-confidence amendment',hashof(roots['contract']/'AMENDMENT-01-UNCERTAIN-MLPS-CONTROL.json')=='93c6d53f4f9396632e91af9d06f7b90b159d4cc2bae1e5e60324239a16ba4a6e')
W=json.loads((roots['contract']/'FROZEN-SPECIMEN-UNITS.json').read_text()); F=json.loads((roots['confounding']/'ACTUAL-SOURCE-METADATA40.json').read_text())['rows']
meta={x['sample_id']:x for x in W['Hofvander']};check('all59 distinct source sample aliases',len(meta)==59)
for r in F:
 m=meta[r['sample_id']]
 check('source/contract metadata:'+r['sample_id'],m['source_label']==r['literal_source_label'] and m['diagnosis']==r['source_diagnosis'] and m['sequencing_year']==r['manifest_sequencing_year'] and m['primary_lesion']==r['source_primary_by_footnote'])
check('40 explicitly absent source purity cells',all(r['purity_status']=='explicit source NA' for r in F))
check('all13 EMC grade source NA',all(r['source_grade']=='NA' for r in F if r['source_diagnosis']=='Extraskeletal myxoid chondrosarcoma'))
check('2492-91 revised Unclear source',next(r for r in F if r['sample_id']=='2492-91')['source_revised_diagnosis']=='Unclear')
check('other39 blank revised diagnosis',sum(r['source_revised_diagnosis'] is None for r in F)==39)
sets=W['sets']; EMC='Extraskeletal myxoid chondrosarcoma';LG='Low-grade fibromyxoid sarcoma';ML='Myxoid liposarcoma';SS='Synovial sarcoma'
check('all/primary/nonknownoverlap counts',[[len(x[h]) for h in [EMC,LG,ML,SS]] for x in sets.values()]==[[13,13,14,19],[12,13,14,18],[9,13,14,18]])
check('known exclusions exact',[x for x in sets['primary_lesions'][EMC] if x not in sets['primary_non_known_overlap'][EMC]]==['104-92','168-97','536-00'])
S=json.loads((roots['readiness']/'ARRAY-PROBE-ANNOTATION.json').read_text());check('GPNMB preselected unique probe sets',[r['probe'] for r in S['GPL6244']]==['8131844'] and {r['probe'] for r in S['GPL3290']}=={'5535','10100','19562'} and all(r['symbols']==['GPNMB'] and not r['unmapped_accessions'] for k in ['GPL6244','GPL3290'] for r in S[k]))
check('all58 original array conditions',len(W['ARRAY_SOURCE_RECORDS'])==58)
Q=json.loads((roots['readiness']/'GSE28866-ASSAY-AND-PEAK-ANNOTATION.json').read_text());check('all FOUR3SEQ exact EMC aliases',Q['EMC_header_columns']==C['GSE28866']['all_EMC'])
check('both fixed coding features',[(x['peak'],x['classification'],x['gene_symbol'],x['peak_exon_gene_symbol']) for x in Q['GPNMB_candidate_peak_annotations']]==[('10146','coding','GPNMB','GPNMB'),('10147','coding','GPNMB','GPNMB')])
check('3SEQ source-labelled sixMLPS threeSS controls',len(Q['comparison_headers'])==9 and sum(x.startswith('MLPS_') for x in Q['comparison_headers'])==6 and sum(x.startswith('SS_') for x in Q['comparison_headers'])==3)
T=json.loads((roots['readiness']/'TEMPO-FILTERED-SCHEMA-ONLY.json').read_text())['sheets'][0];B=json.loads((roots['broader']/'TEMPO12-CONDITION-COVERAGE.json').read_text())
check('all twelve published TempO aliases',T['header'][1:]==C['published_TempO']['all_conditions'] and set(T['header'][1:])=={x['sample_alias'] for x in B['conditions']} and T['GPNMB_first_column_rows']==[7134])
years=[]
for key,x in sets.items():
 for comparator in [LG,ML]:
  e=x[EMC]; c=x[comparator]; common=sorted({meta[i]['sequencing_year'] for i in e}&{meta[i]['sequencing_year'] for i in c})
  ec={y:sum(meta[i]['sequencing_year']==y for i in e) for y in common};cc={y:sum(meta[i]['sequencing_year']==y for i in c) for y in common}
  pairs=sum(ec[y]*cc[y] for y in common)
  uncertain={'omit':'2492-91','available_control_count':sum(meta[i]['sequencing_year'] in common for i in c if i!='2492-91'),'pair_count':sum(ec[y]*sum(meta[i]['sequencing_year']==y for i in c if i!='2492-91') for y in common)} if comparator==ML else None
  years.append({'scope':key,'comparator':comparator,'common_years':common,'EMC_by_year':ec,'control_by_year':cc,'available_EMC':sum(ec.values()),'available_controls':sum(cc.values()),'pair_count_not_independent_donors':pairs,'uncertain_MLPS_omission':uncertain})
  check('recorded year overlap:'+key+':'+comparator,common==['2019','2021'])
check('available EMC years7/6/3',[years[i]['available_EMC'] for i in [0,2,4]]==[7,6,3])
check('LGFMS available controls12',[years[i]['available_controls'] for i in [0,2,4]]==[12,12,12])
check('MLPS base available controls7 and unclearomit6',[years[i]['available_controls'] for i in [1,3,5]]==[7,7,7] and all(years[i]['uncertain_MLPS_omission']['available_control_count']==6 for i in [1,3,5]))
check('free floor',shutil.disk_usage(P).free>=10737418240)
(P/'METADATA-REPLAY.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Only source identity/annotation/metadata counts, no expression cells/effects','year_context':years,'pair_count_unit':'Descriptive eligible ordered EMC-control pairs; never independent biological observations','checks':checks,'all_pass':True,'new_network_or_raw_bytes':0,'expression_outcomes_read':False,'free_bytes':shutil.disk_usage(P).free},indent=2)+'\n')
print(json.dumps({'all_pass':True,'checks':len(checks),'frozen_exports':sum(s['count'] for s in bound),'expression_values':False,'source_queries':0}))
