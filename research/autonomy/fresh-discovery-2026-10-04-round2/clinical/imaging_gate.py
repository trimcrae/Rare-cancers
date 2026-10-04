"""Account for every released Ashburner metastatic case; no inferred risk model."""
from pathlib import Path
from datetime import datetime,timezone
import json,re,hashlib
BASE=Path(__file__).resolve().parent
table=json.loads((BASE/'mri2025-table2-tables.json').read_text())['tables'][0]
patients=[r for r in table if r[0].startswith('Patient')]
assert len(patients)==10
records=[]
for row in patients:
 assert len(row)==5
 rowid=int(row[0].split()[1])
 rec={'id':rowid,'preoperative_nodal':row[1]=='+','preoperative_lung':row[2]=='+','postoperative_lung_months':int(re.search(r'(\d+) m',row[3])[1]) if row[3] else None,'other_postoperative_soft_tissue':row[4] or None,'source_row':row}
 records.append(rec)
assert [x['postoperative_lung_months'] for x in records if x['postoperative_lung_months'] is not None]==[14,23,128,14,61]
notes=(BASE/'mri2025-table2.xml').read_text(encoding='utf8')
assert 'months postoperatively, presentation of metastases' in notes
table3=json.loads((BASE/'mri2025-table3-tables.json').read_text())['tables'][0]
assert any('18% (6/34)' in x for r in table3 for x in r)
assert any('82% (28/34)' in x for r in table3 for x in r)
out={'utc':datetime.now(timezone.utc).isoformat(),'citation':'Ashburner et al., online2025 / print2026, DOI10.1007/s00256-025-05050-w','n_cohort':44,'n_enhancement':34,'n_solid':6,'n_mixed_sparse':28,'records':records,'preoperative_nodal':sum(x['preoperative_nodal'] for x in records),'preoperative_lung':sum(x['preoperative_lung'] for x in records),'postoperative_lung':sum(x['postoperative_lung_months'] is not None for x in records),'postoperative_lung_with_preoperative_nodal':sum(x['postoperative_lung_months'] is not None and x['preoperative_nodal'] for x in records),'source_url':'https://link.springer.com/article/10.1007/s00256-025-05050-w/tables/2','source_sha256':hashlib.sha256((BASE/'mri2025-table2.xml').read_bytes()).hexdigest(),'measurement_gate':'FAIL: no individual enhancement/compartment-to-outcome crosswalk; no censoring times for nonmetastatic patients; raw data explicitly nonpublic','scientific_interpretation':'Unanswered future-risk question. Does not refute the reported presence/absence association; no predictive model fit.'}
(BASE/'imaging-gate-results.json').write_text(json.dumps(out,indent=2))
print(json.dumps({k:v for k,v in out.items() if k!='records'},indent=2))
