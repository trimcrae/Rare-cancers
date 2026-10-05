from pathlib import Path
import urllib.request,urllib.error,datetime,json,hashlib
P=Path(__file__).resolve().parent
if (P/'PUBLIC-SOURCE-RECEIPTS.json').exists():
 raise SystemExit('Historical routes already recorded; do not retry unchanged failed routes. A new source/access amendment is required.')
(P/'raw').mkdir(exist_ok=True)
conditions=json.loads(Path('/workspace/Rare-cancers/research/autonomy/fresh-discovery-2026-10-05-round8/microenvironment/TEMPO-SOURCE-GATE.json').read_text())['all12_library_ids']
ids=','.join(r['sample_accession'] for r in conditions)
urls=[('supplement-archive','https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13374579/supplementaryFiles',6*1024**2),('all12-biosample','https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=biosample&id='+ids+'&retmode=xml',1024**2)]
plan={'date':'2026-10-05','frozen_before_request_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'routes':urls,'supplement_scope':'Actual declared S001 clinical variable table: only table headers/first-column clinical variable labels/explicit specimen IDs if any. No Cox HR/p-values or gene tables/image pixels opened. Full archive ignored; do not extract S002,S003-008 or S009 gene cells.','biosample_scope':'All12 exact known SAMN fields for patient/specimen/source archive/age/sex/site/treatment/disease/sample material/collection; no outcomes or sequence/target/mechanism. Existing R8 ENA accession crosswalk reused; no duplicate ENA/source requery.','cache_gate':'No retained archive or all12 BioSample originals found in prior known TempO source/cache folders; original successful archive receipt defines genuine route. No unchanged failed route retried.','retrieval_selection':'Two declared primary/source branches, no broad search or new cases.'}
(P/'AMENDMENT-01-DECLARED-SOURCE-ROUTES.json').write_text(json.dumps(plan,indent=2)+'\n')
receipts=[]
for name,url,cap in urls:
 rec={'name':name,'url':url,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cap':cap}
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Codex EMC public source metadata review'}),timeout=25) as resp:
   rec['status']=resp.status;body=resp.read(cap+1);rec['final_url']=resp.geturl();rec['content_type']=resp.headers.get('Content-Type')
  if len(body)>cap:rec['cap_exceeded']=True;raise ValueError('Source byte cap exceeded; no body retained/inspected')
  target=P/'raw'/(name+('.zip' if name=='supplement-archive' else '.xml'));target.write_bytes(body);rec.update(path=str(target),bytes=len(body),sha256=hashlib.sha256(body).hexdigest())
 except urllib.error.HTTPError as e:rec.update(status=e.code,error=str(e))
 except Exception as e:rec['error']=type(e).__name__+': '+str(e)
 receipts.append(rec)
(P/'PUBLIC-SOURCE-RECEIPTS.json').write_text(json.dumps({'receipts':receipts},indent=2)+'\n');print(json.dumps(receipts,indent=2))
