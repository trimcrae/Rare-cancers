#!/usr/bin/env python3
"""Audit source bindings and prevalue scope; never inspect cell outcomes/images."""
import datetime,hashlib,json,shutil
from pathlib import Path
p=Path(__file__).resolve().parent
def read(n):return json.loads((p/n).read_text())
def check_binding(row):
 q=Path(row['path']); assert q.is_file(),q
 assert q.stat().st_size==row['bytes'],q
 assert hashlib.sha256(q.read_bytes()).hexdigest()==row['sha256'],q
sources=read('SOURCE-HASHES.json')
for row in sources['new_sources']:check_binding(row)
assert sum(x['bytes'] for x in sources['new_sources'])==sources['retained_raw_bytes']
assert sources['retained_raw_bytes']<=sources['soft_cap_bytes']
assert shutil.disk_usage(p).free>=sources['minimum_free_bytes']
reused=read('REUSED-EVIDENCE.json')
for row in reused['bindings']:check_binding(row)
queries=read('SEARCH-RECEIPTS.json')
for row in queries:
 check_binding(row)
 d=json.loads(Path(row['path']).read_text())
 assert d['hitCount']==row['hit_count']
 assert len(d['resultList']['result'])==row['returned']
api=json.loads((p/'source-cache/pan2025-preprintAPI').read_text())
assert api['collection'][0]['published']=='10.1016/j.xcrm.2025.102418'
assert api['collection'][0]['doi']=='10.1101/2025.03.05.641733'
exact=read('EXACT-ALIAS-ELIGIBILITY.json')
assert len(exact['records'])==exact['all_returned_metadata_records']==16
assert {x['id'] for x in exact['records']}=={x['id'] for x in json.loads((p/'source-cache/exact_EMC_protein_imaging.json').read_text())['resultList']['result']}
question=read('CONDITIONAL-QUESTION-FROZEN.json'); decision=read('DECISION.json'); status=read('PAN2025-SOURCE-STATUS.json')
assert 'CD8-positive' in question['fixed_assay_scope']
assert 'source-measured compartment areas' in question['primary_measurement']
assert decision['finding'] is None and decision['scientific_negative'] is False
assert decision['numerical_outcomes_inspected'] is False and status['numeric_outcomes_inspected'] is False
assert read('COVERAGE.json')['promotion_blocked'] is True
prior={'SCIENCE-FREEZE.json':'73ae0545cde59168163f72315f077560b964a7d4778595a5e5b12edba4254f29','FINAL-FREEZE.json':'ef6700a2bc53a047f835c481a92d8010f94fb25a3b8f02c9e833a5b197c382a2','igf2_review/FREEZE.json':'4dea2cd980a227b0da9554263027fc81d1a1355261c43d545c01f0599aac5eab'}
for n,h in prior.items():assert hashlib.sha256((p.parent/n).read_bytes()).hexdigest()==h,n
result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS','new_source_hashes_checked':len(sources['new_sources']),'reused_source_hashes_checked':len(reused['bindings']),'query_catalogues_checked':len(queries),'exact_alias_records_checked':16,'previous_freezes_unchanged':prior,'retained_raw_bytes':sources['retained_raw_bytes'],'free_bytes':shutil.disk_usage(p).free,'numeric_outcomes_inspected':False,'limit':'Source/hash/scope QA only. No claimed EMC biological/quantitative result or all-public full-source completeness.'}
print(json.dumps(result,indent=2))
