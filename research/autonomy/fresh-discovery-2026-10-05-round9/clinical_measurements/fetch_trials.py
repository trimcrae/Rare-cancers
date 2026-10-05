"""Quiet original-source retrieval; new routes only, no figure/image rendering."""
from pathlib import Path
import json,urllib.request,datetime,hashlib,concurrent.futures,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent
SOURCES=['PMC11443219','PMC10520347','PMC11164811','PMC12434394','PMC12451337','PMC7286446','PMC5035789','PMC13396634']
def one(pmc):
 receipts=[];accepted=None
 for route,url in [('EPMC-JATS',f'https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/fullTextXML'),('official-BioC',f'https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/{pmc}/unicode')]:
  rec={'pmcid':pmc,'route':route,'url':url,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
  try:
   with urllib.request.urlopen(url,timeout=30) as r:b=r.read(4000001);rec['http_status']=r.status
   assert len(b)<4000001,'size limit incomplete; not retained'
   target=ROOT/'source-cache'/f'{pmc}-{route}.xml';target.write_bytes(b);x=ET.fromstring(b);valid=x.tag=='article' or x.tag=='collection' and x.find('.//document/id') is not None and (x.find('.//document/id').text or '').replace('PMC','')==pmc[3:];rec.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),path=str(target.relative_to(ROOT)),valid_article=valid)
   if valid:accepted=rec;receipts.append(rec);break
  except Exception as e:rec['error']=type(e).__name__+':'+str(e)
  receipts.append(rec)
 return {'pmcid':pmc,'attempts':receipts,'accepted':accepted,'status':'pending source evaluation' if accepted else 'unavailable evidence'}
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:rr=list(ex.map(one,SOURCES))
 ROOT.joinpath('SOURCE-ACCESS.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sources':rr},indent=2)+'\n');print(json.dumps([{x['pmcid']:x['status'],'route':x['accepted']['route'] if x['accepted'] else None,'errors':[y.get('error') for y in x['attempts'] if y.get('error')]} for x in rr]))
