#!/usr/bin/env python3
"""Replay frozen source labels/schema without reading any gene/table rows."""
from pathlib import Path
import json, hashlib
P=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
checks=0
for x in json.loads((P/'REUSED-SOURCE-BINDINGS.json').read_text())['sources']:
 p=Path(x['path']);assert sha(p)==x['sha256'] and p.stat().st_size==x['bytes'];checks+=1
access=json.loads((P/'ZULLOW-GSM-METADATA-ACCESS.json').read_text());raw=Path(access['cache_path'])
assert sha(raw)==access['sha256'] and raw.stat().st_size==access['bytes'];checks+=1
recs=[];r=None
allowed=['!Sample_title','!Sample_source_name_ch1','!Sample_library_strategy','!Sample_library_source','!Sample_library_selection','!Sample_platform_id']
for line in raw.read_text().splitlines():
 if line.startswith('^SAMPLE'): r={'accession':line.split('=',1)[1].strip()};recs.append(r)
 elif r is not None and line.startswith('!Sample_') and '=' in line:
  k,v=line.split('=',1);k=k.strip();v=v.strip()
  if k in allowed or k.startswith('!Sample_supplementary_file_'):r.setdefault(k,[]).append(v)
  if k=='!Sample_characteristics_ch1' and v.split(':',1)[0].lower() in ['cell line','experimental condition']:r.setdefault('identity',[]).append(v)
assert len(recs)==138
native=[r for r in recs if r.get('!Sample_source_name_ch1')==['primary tumor']]
assert len(native)==22 and all(r['!Sample_library_strategy']==['RNA-Seq'] and r['!Sample_library_source']==['transcriptomic'] for r in native);checks+=1
assert sum('cell line: MLPS Primary Tumor' in r.get('identity',[]) for r in native)==12
assert sum('experimental condition: genotype: EWS-FLI1 fusion primary tumor' in r.get('identity',[]) for r in native)==10;checks+=1
frozen=json.loads((P/'ZULLOW-PUBLIC-NATIVE-DECLARATIONS.json').read_text())['primary_tumor_library_records']
assert len(frozen)==len(native)
for a,b in zip(native,frozen):
 assert a['accession']==b['accession']
 for k in allowed:
  assert a.get(k)==b.get(k)
 for k in ['!Sample_supplementary_file_1','!Sample_supplementary_file_2']:
  assert a.get(k)==b.get(k)
 checks+=1
ident=json.loads((P/'ZULLOW-EXPLICIT-IDENTITY-CHARACTERISTICS.json').read_text())['rows']
for a,b in zip(native,ident):
 assert a['accession']==b['accession'] and a['identity']==b['identity_condition_characteristics'];checks+=1
port=json.loads((P/'PORTABILITY.json').read_text())
for x in port['new_cached_files']:
 p=Path(x['path']);assert sha(p)==x['sha256'] and p.stat().st_size==x['bytes'];checks+=1
assert sum(x['bytes'] for x in port['new_cached_files'])==port['new_retained_total_bytes']<8388608
assert json.loads((P/'DECISION.json').read_text())['fully_ready_additional_native_GPNMB_inputs_authenticated']==0
print(json.dumps({'status':'PASS','source_hash_and_label_checks':checks,'metadata_records':138,'native_RNA_source_declarations':22,'new_gene_values':0,'new_statistics':0}))
