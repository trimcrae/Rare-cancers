"""Recheck retained source metadata, scope and hashes; no assay outcomes."""
import json,pathlib,hashlib,datetime
B=pathlib.Path(__file__).parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
d=json.loads((B/'CHECKED-SOURCE-BINDINGS-INITIAL.json').read_text())
for r in d['inputs']:
 p=pathlib.Path(r['path']);assert p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],p
owner=pathlib.Path(d['inputs'][0]['path']).parent
api=json.loads((owner/'source-cache/phospho_API').read_text())['collection'][0]
assert api['doi']=='10.64898/2026.07.08.737171'
assert '1,998 tumor samples' in api['abstract'] and '46' in api['abstract']
queries={}
for n in ['PRIDE-search-precision','PRIDE-search-pan-cancer','PRIDE-search-MASTER','PRIDE-search-phosphoproteomics','PRIDE-search-phospho','PRIDE-search-doi']:
 p=owner/'source-cache'/n;rs=json.loads(p.read_text());assert isinstance(rs,list)
 match=[]
 for r in rs:
  text=r.get('title','')+' '+r.get('projectDescription','')
  if any(s in text for s in ['TOPAS','MASTER','CATCH','INFORM','Prospective pan-cancer phosphoproteomics','737171']):match.append({'accession':r.get('accession'),'title':r.get('title')})
 queries[n]={'returned_projects':len(rs),'source_phrase_project_matches':match,'query_limit':'Exact indexed query or available firstpage; no globalabsence or EMCexclusion claim'}
invalid=json.loads((owner/'PHOSPHO-REPOSITORY-ACCESS.json').read_text())
assert invalid[0]['sha256']==invalid[1]['sha256']
amend=json.loads((owner/'AMENDMENT-01-PREVALUE-QA.json').read_text());assert 'invalid search evidence' in amend['retrieval_QA']
assert 'docking' in amend['assay_clarification'] and 'not proof of catalytic activation' in amend['assay_clarification']
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'input_bindings_checked':len(d['inputs']),'mismatches':0,'primary_source_unit':'1998tumor samples, independent patients/pairedassaysunestablished','source_metadata_scope':'MASTER/CATCH/INFORM,46TOPASkinases; no EMC roster in retained abstract/metadata','PRIDE_metadata_checks':queries,'invalid_query_QA':'Two initialwrong-route receipts shareidenticalunrelatedpayload; ownerwithdrawal explicitlyretained','Y1062_amendment':'Pass: directsite phosphorylation versus docking/catalyticactivity/dependence distinct','assay_values_inspected':False,'full_primary_and_EMC_roster':'Unavailable or pending, not negativemeasurements'}
(B/'RETAINED-SOURCE-AUDIT.json').write_text(json.dumps(out,indent=2)+'\n')
print('source-bindings',len(d['inputs']),'mismatches',0,'assayvalues',False)
