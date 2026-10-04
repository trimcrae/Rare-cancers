"""Reproduce metadata eligibility, same-experiment check and bound prior-evidence reuse.
No RNA/ATAC/ChIP signal or disease-effect calculation is performed.
"""
from pathlib import Path
import json,hashlib,datetime
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parent
PRIMARY=Path('C:/Projects/EMC-Research')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,x):(ROOT/n).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
records={};queries=[]
for n in ['epmc-emc-regulatory.json','epmc-fusion-regulatory.json','epmc-authentic-models.json','six3-contrary2004.json']:
 p=ROOT/n;d=json.loads(p.read_text(encoding='utf-8')); rows=d['resultList']['result'];assert d['hitCount']==len(rows)
 queries.append({'file':n,'sha256':sha(p),'hit_count':d['hitCount'],'returned':len(rows),'interpretation':'complete returned metadata, not full scientific evaluation of every paper'})
 for r in rows:records.setdefault((r['source'],r['id']),r)
ids=['39048711','18680143','10359536','12049818','11673470','12543801','15262426','26310886','34018649','29455671','23329308','41342886']
selected=[]
for i in ids:
 r=records[('MED',i)]
 selected.append({k:r.get(k) for k in ['source','id','pmcid','doi','title','authorString','firstPublicationDate','abstractText','fullTextUrlList','meshHeadingList']})
write('selected-primary-metadata.json',selected)
geo=[]
for d in ET.parse(ROOT/'geo-fusion-summary.xml').getroot().findall('DocSum'):
 vals={x.attrib['Name']:' '.join(x.itertext()) for x in d.findall('Item')}
 if vals.get('Accession') not in ['GSE11185','GDS3481']:continue
 samples=[]
 for s in d.findall("Item[@Name='Samples']/Item"):
  samples.append({x.attrib['Name']:x.text for x in s.findall('Item')})
 geo.append({k:vals[k] for k in ['Accession','summary','GPL','GSE','n_samples']}|{'samples':sorted(samples,key=lambda x:x['Accession'])})
assert len(geo)==2 and geo[0]['samples']==geo[1]['samples'] and len(geo[0]['samples'])==4
assert all('293-tet-On-' in s['Title'] for s in geo[0]['samples'])
write('geo-four-condition-evaluation.json',{'source_file':'geo-fusion-summary.xml','sha256':sha(ROOT/'geo-fusion-summary.xml'),'records':geo,'unique_GSMs':4,'independent_EMC_donors':0,'interpretation':'Four engineered 293 condition arrays, one listed array per condition. GDS3481 reuses GSE11185; no authentic EMC perturbation and no independent-donor error estimate.'})
reuse=[]
for rel in [
'research/autonomy/fresh-discovery-2026-10-04-round2/regulatory/filion2009-source-evaluation.json',
'research/autonomy/fresh-discovery-2026-10-04-round2/regulatory/brenca2019.xml.excerpts.txt',
'research/autonomy/fresh-discovery-2026-10-04-round2/regulatory/zullow2022-source-evaluation.json',
'research/autonomy/fresh-discovery-2026-10-04-round2/regulatory/zullow-tableS1-evaluation.json',
'research/autonomy/fresh-discovery-2026-10-04-round2/regulatory/zullow-eligibility-summary.json',
'research/autonomy/fresh-discovery-2026-10-04-round2/regulatory/COVERAGE.txt',
'research/autonomy/fresh-discovery-2026-10-04-round3/small_rna/deposition-review-reuse.json']:
 p=PRIMARY/rel;reuse.append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'scope':'bound prior completed evaluation; original underlying source hash remains in that record; no reanalysis claimed'})
write('reused-evidence.json',reuse)
models=json.loads((ROOT/'epmc-authentic-models.json').read_text(encoding='utf-8'))['resultList']['result']
write('model-query-title-screen.json',{'scope':'title/abstract discovery screen, not complete assay evaluation of 29 studies','records':[{k:r.get(k) for k in ['source','id','doi','title']} for r in models]})
write('evaluation.json',{'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'decision':'SHELVE the proposed standalone endogenous-fusion regulatory/dependency claim','new_demonstrated_EMC_findings':[],'quantitative_pilot_performed':False,'reason':'No new authentic EMC perturbation/binding/output comparison qualified; published tissue observations and engineered-cell results do not supply that bridge. This is a feasibility/value result, not biological absence.','query_completeness':queries,'selected_primary_PMIDs':ids,'same_experiment_check':'all four GSE11185/GDS3481 GSM identities matched','contrary_primary':{'PMID':'15262426','doi':'10.1016/j.cancergencyto.2003.11.011','observations':'One index case plus 18 surveyed author-labelled EMCs. Two lack detected NR4A3 fusion and coexpress native NOR1/SIX3; 14 fusion-positive tumors express neither according to the abstract; assay level unresolved. Remaining three cases, individual crosswalk and donor overlap are not resolved by abstract.','limits':'Published result, not new discovery. Does not equate fusion not detected with reclassification. The title mentions proteins but abstract does not establish assay level. Do not explain discordance with 2003 RT-PCR by an assumed assay difference; full methods/case differences unresolved.'},'no_claims':['no claim that authentic EMC regulatory perturbation data do not exist','no dependency, efficacy or shared program claim','no new SIX3 negative finding','no global evidence-exhaustion claim'],'promotion_blocks':['full historical source/supplement and individual donor mapping gaps','unresolved seven-EMC RNA linkage in Zullow deposit','no qualifying authentic endogenous perturbation comparison','independent challenge before any future promotion']})
print(json.dumps({'metadata_queries':queries,'unique_metadata_records':len(records),'selected_primary':len(selected),'GEO_unique_conditions':4,'reused_receipts':len(reuse)},indent=2))