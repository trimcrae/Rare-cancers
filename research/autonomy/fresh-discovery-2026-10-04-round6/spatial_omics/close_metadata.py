import json,re,hashlib,xml.etree.ElementTree as E,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parent
LEAD=Path('C:/Users/mcrae/.codex/worktrees/emc-fresh-20261004-lead/research/autonomy')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
old=LEAD/'fresh-discovery-2026-10-04-round3/immune'
reuse=[]
for n in ['COVERAGE.md','geo-eligibility.json','subramanian-table-eligibility.json','gse212526.txt','gse212527.txt','gse213065.txt','subramanian2024-tables.xlsx']:
 p=old/n
 reuse.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'role':'Verified prior sample/assay exclusion reused; no numerical expression reanalysis.'})
(ROOT/'prior-evaluation-reuse.json').write_text(json.dumps(reuse,indent=2),encoding='utf-8')
meta=[]
for chunk in (ROOT/'GSE313859.soft').read_text(encoding='utf-8').split('^SAMPLE = ')[1:]:
 lines=chunk.splitlines();c=[x.split(' = ',1)[1] for x in lines if x.startswith('!Sample_characteristics_ch1 = ')]
 title=next(x.split(' = ',1)[1] for x in lines if x.startswith('!Sample_title = '))
 meta.append({'gsm':lines[0].strip(),'title':title,'characteristics':c,'biosamples':sorted(set(re.findall(r'SAMN\d+',chunk)))})
(ROOT/'bo112-library-identities.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
patients={next(c for c in x['characteristics'] if c.startswith('patient:')) for x in meta}
patient_times={(next(c for c in x['characteristics'] if c.startswith('patient:')),next(c for c in x['characteristics'] if c.startswith('timepoint:'))) for x in meta}
summary={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'new_eligible_emc_measurements_authenticated':0,'biological_pilot_performed':False,'reason':'EMC identity and useful independent contrast not established in any newly scoped cell-resolved source; absence not demonstrated.', 'bo112_libraries':len(meta),'bo112_donors':len(patients),'bo112_donor_timepoint_combinations':len(patient_times),'bo112_independence':'Four paired baseline/surgery donors plus three RT-only surgical donors. RT001 has CD45-positive and CD45-negative libraries at the same surgical time point; those are not independent donors.', 'original_source_identifiers':{},'unreadable_supplements':[]}
for n in ['ngo2025.xml','luthria2024.xml','atlas2026.xml']:
 x=E.parse(ROOT/n)
 summary['original_source_identifiers'][n]=[{'type':el.attrib.get('pub-id-type'),'id':el.text} for el in x.findall('.//article-id')]
for n in ['luthria-S1.xlsx','atlas2026-S1.pdf']:
 b=(ROOT/n).read_bytes()
 summary['unreadable_supplements'].append({'file':n,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'actual_content':'HTML response, not requested spreadsheet/PDF; not parsed as measurement or sample roster.'})
assert len(meta)==12
assert len({x['gsm'] for x in meta})==12
assert not any('extraskeletal' in ' '.join(x['characteristics']).lower() for x in meta)
assert all((old/n).exists() for n in ['gse212526.txt','gse212527.txt','gse213065.txt'])
(ROOT/'metadata-verification.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps({'libraries':len(meta),'reused_files':len(reuse),'identifiers':summary['original_source_identifiers']},indent=2))
