"""Independent bounded metadata coverage/identity audit; no expression values."""
import argparse,pathlib,json,hashlib,re,collections
ap=argparse.ArgumentParser();ap.add_argument('--packet',type=pathlib.Path,required=True);ap.add_argument('--output',type=pathlib.Path,required=True);a=ap.parse_args();P=a.packet
j=json.load(open(P/'GSM-ELIGIBILITY-OBSERVATIONS.json'));retry=json.load(open(P/'GSM9511154-RETRY-OBSERVATION.json'));j['libraries'][retry['accession']]=retry;s=json.load(open(P/'GEO-SERIES-ELIGIBILITY.json'))
out={'series_metadata_count':len(s['series']),'all_library_rosters':{},'source_prefix_conflicts':[],'pending_library_metadata':[],'all_series_disease_model_hits':[],'interpretation':'Counts refer to library conditions, not independent donors or evaluated biological measurements.'}
for accession,ids in j['by_series'].items():
 diseases=collections.Counter(); missing=[]
 for gsm in ids:
  r=j['libraries'].get(gsm)
  if not r or r.get('source_status')!=200: missing.append(gsm);out['pending_library_metadata'].append(gsm);continue
  attrs=[x.split(':',1)[1].strip() for x in r.get('characteristics_ch1',[]) if x.startswith('disease:') or x.startswith('cell type:')]
  diseases['|'.join(attrs) if attrs else '|'.join(r.get('source_name_ch1',[]))]+=1
  title='|'.join(r.get('title',[]));d=[x.split(':',1)[1].strip() for x in r.get('characteristics_ch1',[]) if x.startswith('disease:')]
  # Source-title prefixes are a challenge flag, not diagnosis. Preserve original labels.
  if accession=='GSE319124' and title.startswith('SJEWS') and d!=['EWS'] or accession=='GSE319124' and title.startswith('SJRHB') and d!=['RMS']:
   out['source_prefix_conflicts'].append({'accession':gsm,'title':r.get('title'),'source_disease':d,'source_sha256':r.get('source_sha256'),'consequence':'Potential title/annotation or disease-reclassification conflict; do not silently relabel. No EMC identity established.'})
 out['all_library_rosters'][accession]={'listed_conditions':len(ids),'parsed_conditions':len(ids)-len(missing),'pending':missing,'reported_source_condition_classes':dict(diseases)}
for r in s['series'].values():
 if re.search(r'extraskeletal|\bEMC\b|\bEMCS\b|chordoid|chondromyxoid|H.EMC.SS|MUG.EMCS|NCC.EMC|USZ2[023]|myxoid.chondro',json.dumps(r),re.I):
  out['all_series_disease_model_hits'].append({'accession':r['accession'],'title':r['title'],'n_samples':r.get('n_samples'),'consequence':'Existing bulk/reference evidence, not single-cell by alias alone; source assay determines eligibility.'})
# Current source rosters are exact subsets; broader authors' samples require their own source mapping.
for accession,expect in [('GSE319327',1),('GSE319124',59),('GSE200529',26)]:
 assert out['all_library_rosters'][accession]['listed_conditions']==expect
assert [x['accession'] for x in out['source_prefix_conflicts']]==['GSM9511127','GSM9511129']
additional=json.load(open(P/'ADDITIONAL-GSM-ELIGIBILITY-OBSERVATIONS.json'))
out['additional_all_library_rosters']={}
for accession,ids in additional['by_series'].items():
 status=collections.Counter(str(additional['libraries'].get(gsm,{}).get('source_status')) for gsm in ids)
 out['additional_all_library_rosters'][accession]={'listed_conditions':len(ids),'source_status_counts':dict(status)}
# This whole supplemental roster closes explicit source classes, not every panel/cell-line provenance.
table=(P/'SCTUMOR-TABLE1-EXTRACT.txt').read_text().split('\nReferences')[0]
classes=['ALL','ATC','BCC','BLCA','BRCA','CESC','ccRCC','CRC','cSCC','DSRCT','GCTB','GBM','HNSCC','HCC','ICC','LUAD','LUSC','MPNST','MB','MCC','MESO','MPAL','NB','OS','OV','PAAD','PNET','PTC','PRAD','RMS','SACC','SKCM','STAD','SyS','TGCT','WT']
assert all('('+code+')' in table for code in classes)
out['scTumor_primary_table']={'all36_source_classes':classes,'disease_label_hits':[word for word in ['extraskeletal','chondrosarcoma','myxoid'] if word in table.lower()],'limits':'All36 reported primary-source classes checked. Table has reused datasets and some breast cell lines; rows/samples/cells are not independent donors. Generic pan-cancer CCL panels require separate authentication.'}
bo=additional['by_series']['GSE313859']; known={'Patient 004':'myxofibrosarcoma','Patient 010':'undifferentiated pleomorphic sarcoma','Patient 011':'undifferentiated pleomorphic sarcoma'};pending=[]
for gsm in bo:
 r=additional['libraries'][gsm];patient=[x.split(':',1)[1].strip() for x in r.get('characteristics_ch1',[]) if x.startswith('patient:')]
 if not patient or patient[0] not in known:pending.append({'accession':gsm,'patient':patient,'title':r.get('title'),'conditions':r.get('characteristics_ch1')})
out['BO112_unresolved_conditions']={'all_six_library_conditions':pending,'apparent_donor_count':4,'limits':'Patient012 baseline/surgery; RT001CD45neg/pos sorts; RT002 and RT003. Five may be malignant-compatible but all6 conditions remain relevant source coverage. No fusion/pathology crosswalk here; not non-EMC.'}
assert len(pending)==6
out['input_bindings']=[{'path':f,'sha256':hashlib.sha256((P/f).read_bytes()).hexdigest()} for f in ['GSM-ELIGIBILITY-OBSERVATIONS.json','GSM9511154-RETRY-OBSERVATION.json','GEO-SERIES-ELIGIBILITY.json','ADDITIONAL-GSM-ELIGIBILITY-OBSERVATIONS.json','SCTUMOR-TABLE1-EXTRACT.txt']]
a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'series_metadata':out['series_metadata_count'],'library_conditions':sum(r['listed_conditions'] for r in out['all_library_rosters'].values()),'pending':out['pending_library_metadata'],'subtype_conflicts':[x['accession'] for x in out['source_prefix_conflicts']]},indent=2))
