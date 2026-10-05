#!/usr/bin/env python3
"""Verify frozen source eligibility labels; never inspect table/protocol rows."""
from pathlib import Path
import json,hashlib,re
P=Path(__file__).resolve().parent
plan=json.loads((P/'PLAN-FROZEN.json').read_text());q=Path(plan['original_path'])
assert len(q.read_bytes())==plan['original_bytes'] and hashlib.sha256(q.read_bytes()).hexdigest()==plan['original_sha256']
fields=['!Sample_geo_accession','!Sample_title','!Sample_source_name_ch1','!Sample_library_strategy','!Sample_library_source','!Sample_library_selection','!Sample_molecule_ch1','!Sample_platform_id']
raw=[];r=None
for line in q.read_text().splitlines():
 if line.startswith('^SAMPLE'):r={'accession':line.split('=',1)[1].strip()};raw.append(r)
 elif r is not None and line.startswith('!Sample_') and '=' in line:
  k,v=line.split('=',1);k=k.strip();v=v.strip()
  if k in fields:r.setdefault(k,[]).append(v)
  elif k=='!Sample_characteristics_ch1':
   label=v.split(':',1)[0].lower()
   if label=='cell line':r.setdefault('literal_model_label',[]).append(v.split(':',1)[1].strip())
   elif label=='experimental condition':r.setdefault('literal_condition_label',[]).append(v.split(':',1)[1].strip())
assert raw==json.loads((P/'DIRECT-RAW-SOURCE-IDENTITY138.json').read_text())['source_records']
assert len(raw)==len({r['accession'] for r in raw})==138
out=json.loads((P/'ALL138-ELIGIBILITY-DISPOSITIONS.json').read_text())['complete_source_records']
assert [r['accession'] for r in raw]==[r['accession'] for r in out]
checks=0
for a,b in zip(raw,out):
 assert a['literal_model_label']==[b['literal_model_label']]
 assert a['literal_condition_label']==b['literal_condition_labels']
 assert a['!Sample_title']==[b['literal_title']]
 assert a['!Sample_library_strategy']==[b['library_strategy']]
 assert a['!Sample_library_source']==[b['library_source']]
 assert a['!Sample_source_name_ch1']==[b['literal_source_name']]
 checks+=6
c=json.loads((P/'ASSAY-AND-IDENTITY-CENSUS.json').read_text());assert c['native_vs_culture_counts']=={'source_primary_tumor':22,'source_cancer_cell_line':68,'source_stem_cell_line':48}
assert sum(r['library_source']=='transcriptomic' and r['library_strategy']=='RNA-Seq' for r in out)==52
assert sum(r['library_source']=='transcriptomic' and r['literal_source_name']!='primary tumor' for r in out)==30
ctx=json.loads((P/'SOURCE-LINEAGE-CONTEXT-AMENDMENT.json').read_text());f=Path(ctx['cached_source']);assert hashlib.sha256(f.read_bytes()).hexdigest()==ctx['sha256']
line=next(s for s in f.read_text().splitlines() if s.startswith('!Series_overall_design'))
for frag in json.loads((P/'EXACT-SOURCE-MODEL-LINEAGE.json').read_text())['selected_fragments']:
 assert frag['alias']+' ('+frag['literal_source_parenthetical']+')' in line
assert all(not r['gene_values_read'] and not r['native_EMC_authenticated'] for r in out)
print(json.dumps({'status':'PASS','literal_field_checks':checks,'unique_GSM_records':138,'source_context_fragments':2,'new_gene_values':0,'new_network':0}))
