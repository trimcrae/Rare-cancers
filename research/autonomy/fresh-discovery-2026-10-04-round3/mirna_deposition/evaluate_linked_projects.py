"""Retain every linked experimental record and distinguish spurious matches."""
from pathlib import Path
import xml.etree.ElementTree as E,json,collections
D=Path(__file__).resolve().parent;out={}
for acc in ['PRJNA692081','PRJEB110929']:
    x=E.parse(D/(acc+'-sra-experiments.xml'));rr=[]
    for p in x.findall('.//EXPERIMENT_PACKAGE'):
        s=p.find('SAMPLE');e=p.find('EXPERIMENT');study=p.find('STUDY')
        rr.append({'sample':s.attrib,'title':s.findtext('TITLE'),'organism':s.findtext('.//SCIENTIFIC_NAME'),'attrs':[(a.findtext('TAG'),a.findtext('VALUE'))for a in s.findall('.//SAMPLE_ATTRIBUTE')],'experiment':e.attrib,'strategy':e.findtext('.//LIBRARY_STRATEGY'),'selection':e.findtext('.//LIBRARY_SELECTION'),'library_source':e.findtext('.//LIBRARY_SOURCE'),'library_protocol':e.findtext('.//LIBRARY_CONSTRUCTION_PROTOCOL'),'design':e.findtext('.//DESIGN_DESCRIPTION'),'study':study.attrib,'study_external_ids':[(a.attrib,a.text)for a in study.findall('.//EXTERNAL_ID')],'study_title':study.findtext('.//STUDY_TITLE'),'study_abstract':study.findtext('.//STUDY_ABSTRACT'),'runs':[a.attrib for a in p.findall('.//RUN')]})
    out[acc]={'all_returned_experiment_records':rr,'n':len(rr),'organism_counts':dict(collections.Counter(r['organism']for r in rr)),'study_counts':dict(collections.Counter(r['study'].get('accession')for r in rr))}
out['PRJNA692081']['decision']='Verified prior evaluation reused after parent correction: Brenca DOI10.1002/path.5284 describes12 patient tumors plus11 engineered cultures (4EN,4TN,3NR4A3), all under genericEMC metadata. This is not23patient tumors or new coverage. No mature-miRNA protocol/MSTS2013crosswalk. Current metadata supplies no new patient/culture mapping for the remaining15aliases.'
out['PRJNA692081']['verified_engineered_aliases']={'EN':['315','316','317','363'],'TN':['367','385','386','318']}
out['PRJNA692081']['prior_sources']=['C:/Projects/EMC-Research/research/autonomy/tmem266-prepublication-2026-10-03/SOURCE-GATES.txt','C:/Projects/EMC-Research/research/autonomy/tmem266-tissue-2026-10-03/SOURCE-AUDIT.txt','C:/Projects/EMC-Research/research/autonomy/tmem266-tissue-2026-10-03/PLAN.txt']
assert all(any(r['sample']['alias']==alias for r in out['PRJNA692081']['all_returned_experiment_records'])for ids in out['PRJNA692081']['verified_engineered_aliases'].values()for alias in ids)
out['PRJEB110929']['decision']='Search yields9human records collected2019 and1unrelated plantWGS record. Ninehuman libraries labelledOTHER/GENOMIC despite small-ncRNA study title; no EMC diagnosis/crosswalk. Unrelated plant record cannot become a tenth patient. Neither matches16FFPEMSTS2013identity. Underlying miRNA matrices not opened.'
(D/'linked-project-evaluation.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({a:{k:v for k,v in r.items()if k in ['n','organism_counts','study_counts']}for a,r in out.items()}))
