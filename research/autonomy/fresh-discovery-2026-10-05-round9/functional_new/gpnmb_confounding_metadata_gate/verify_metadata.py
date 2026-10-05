#!/usr/bin/env python3
"""Replay only frozen specimen metadata; no gene outcomes or unlisted columns."""
import json, hashlib
from pathlib import Path
from openpyxl import load_workbook
P=Path(__file__).resolve().parent
W=Path('/workspace/Rare-cancers/research/autonomy/atlas-hofvander-source-2026-09-06/ccr-25-3740_supplementary_table_s1_suppts1.xlsx')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
a=json.loads((P/'ACTUAL-SOURCE-METADATA40.json').read_text())
assert sha(W)==a['source_sha256']
s=load_workbook(W,read_only=False,data_only=True).worksheets[0]
fields={'A':'literal_source_label','B':'source_diagnosis','C':'source_revised_diagnosis','F':'source_age_at_diagnosis','G':'source_sex','H':'source_site','K':'source_grade','M':'source_samplef','V':'source_comment_metadata_only','W':'source_UniqMappedReadsMillion'}
checks=0
for r in a['rows']:
 for col,key in fields.items():
  assert s[f"{col}{r['s1_row']}"].value==r[key],(r['sample_id'],key)
  checks+=1
 assert s[f"S{r['s1_row']}"].value=='NA'
 checks+=1
assert len(a['rows'])==40
em=[r for r in a['rows'] if r['source_diagnosis']=='Extraskeletal myxoid chondrosarcoma']
assert len(em)==13 and all(r['source_grade']=='NA' for r in em)
assert sum(r['source_samplef'] is None for r in em)==12
assert [r['sample_id'] for r in em if r['source_samplef']=='LR']==['5081-14']
assert all(r['source_UniqMappedReadsMillion'] is not None for r in a['rows'])
rev=[r for r in a['rows'] if r['source_revised_diagnosis'] is not None]
assert len(rev)==1 and rev[0]['sample_id']=='2492-91' and rev[0]['source_revised_diagnosis']=='Unclear'
t=json.loads((P/'TECHNICAL-METADATA-SENSITIVITY-AVAILABILITY.json').read_text())
for r in t['sensitivities']:
 assert r['common_recorded_sequencing_years']==['2019','2021']
 assert r['EMC_available_sameyear_case_count']=={'all13':7,'primary12':6,'old_primary9':3}.get(r['EMC_sensitivity'],3)
 assert r['control_available_sameyear_case_count']==(12 if r['control']=='Low-grade fibromyxoid sarcoma' else 7)
print(json.dumps({'status':'PASS','literal_source_cell_checks':checks,'cases':40,'new_gene_values':0,'new_RNA_statistics':0}))
