"""Meaningful source-integrity, identity and technical-condition checks."""
import hashlib,json,pathlib,re,datetime,os
ROOT=pathlib.Path(__file__).resolve().parent
def read(name):return json.loads((ROOT/name).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if __name__=='__main__':
 failures=[];checked=set();n=0
 for f in ROOT.glob('*RECEIPT*.json'):
  obj=json.loads(f.read_text());queue=[obj]
  while queue:
   x=queue.pop()
   if isinstance(x,list):queue.extend(x)
   elif isinstance(x,dict):
    if x.get('path') and x.get('sha256'):
     key=(x['path'],x['sha256'])
     if key in checked:continue
     checked.add(key);n+=1;p=ROOT/x['path']
     if not p.exists() or sha(p)!=x['sha256']:failures.append(str(key))
    else:queue.extend(x.values())
 a=read('GSM-ELIGIBILITY-OBSERVATIONS.json');b=read('ADDITIONAL-GSM-ELIGIBILITY-OBSERVATIONS.json')
 assert len(a['libraries'])==121 and len(b['libraries'])==303
 assert not set(a['libraries']).intersection(b['libraries'])
 assert read('GSM9511154-RETRY-OBSERVATION.json')['source_status']==200
 c=read('BO112-COVERAGE-BY-CONDITION.json')
 assert len(c['rows'])==26 and len(c['unresolved_libraries'])==6 and len(c['unresolved_donors'])==4
 assert sum(r['status']=='pending accessible analysis' for r in c['rows'])==6
 assert len(read('PEDIATRIC-SIBLING-ASSAY-OBSERVATIONS.json'))==277
 assert all(r['RSEM_gene_vector'] for r in read('PEDIATRIC-SIBLING-ASSAY-OBSERVATIONS.json'))
 assert len(read('SCTUMOR-ROSTER-OBSERVATIONS.json')['primary_type_abbreviations'])==36
 assert (ROOT/'sources/sctumor_media1.pdf').read_bytes().startswith(b'%PDF')
 assert (ROOT/'sources/sctumor_table1.json').read_bytes().startswith(b'<!doctype html>') # challenge is not PDF
 assert (ROOT/'sources/bo112_bioc.json').read_bytes().startswith(b'[Error]')
 assert read('COVERAGE.json')['eligible_authenticated_EMC_biological_observations']==0
 assert read('DECISION.json')['decision']=='shelve the standalone paper'
 retained=sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file())
 free=os.statvfs(ROOT).f_bavail*os.statvfs(ROOT).f_frsize
 assert retained<64*1024**2 and free>=10*1024**3
 assert not failures,failures
 result={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'source_receipts_hash_checked':n,'library_metadata_records':424,'BO112_library_conditions':26,'BO112_unresolved_conditions':6,'BO112_unresolved_donors':4,'raw_and_derived_packet_bytes_including_copies':retained,'limit_bytes':64*1024**2,'filesystem_free_bytes':free,'scope':'Source integrity and eligibility/technical-condition arithmetic. No expression analysis or malignant-cell state validation was performed.','independent_scientific_reproduction':False}
 (ROOT/'VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
